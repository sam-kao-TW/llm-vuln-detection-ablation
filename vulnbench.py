"""
vulnbench.py — shared runner for the LLM vulnerability-detection ablation study.

Design notes (addressing reviewer concerns):
  * CLEAN and HINTED prompts form strict minimal pairs: HINTED is CLEAN with a
    single, identical category-naming clause inserted at a fixed position.
    No other wording differs.
  * The system message is category-neutral ("CWE-XX"); no concrete CWE
    identifier appears in any condition.
  * Results are stored in long format, one row per
    (sample_id, condition, run_id), enabling repeated-run variance analysis.
  * Every call is written incrementally, so an interrupted session resumes
    exactly where it stopped.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

import pandas as pd
from openai import OpenAI


# --------------------------------------------------------------------------
# Benchmark hygiene
# --------------------------------------------------------------------------

_LEAK_RE = re.compile(r'\b(un)?safe sample\b', re.I)


def strip_header(text: str) -> str:
    """Remove the SARD descriptive header and copyright block.

    CRITICAL: every file in the SARD PHP test suite begins with a comment that
    states "Safe sample" or "Unsafe sample" - the ground-truth label is embedded
    in the input. Passing the raw file to a model therefore leaks the answer.
    This function removes the header and copyright block so that only the
    executable code is presented to the model.
    """
    if 'MODIFICATIONS.*/' in text:
        body = text.split('MODIFICATIONS.*/')[-1]
    else:
        body = re.sub(r'^\s*<\?php\s*(/\*.*?\*/\s*)+', '', text, flags=re.S)
    body = _LEAK_RE.sub('', body).strip()
    return body if body.startswith('<?php') else '<?php\n' + body

# --------------------------------------------------------------------------
# Prompt definitions
# --------------------------------------------------------------------------

SYSTEM_MESSAGE = (
    'You must respond strictly in JSON format with exactly three keys:\n'
    '1. "prediction": String, MUST be either "Vulnerable" or "Safe".\n'
    '2. "cwe_type": String, the identified CWE identifier (for example, '
    '"CWE-XX") or "None" if safe.\n'
    '3. "confidence": Integer from 0 to 100.'
)

_TASK = ('Analyze the following PHP code and determine whether it contains a '
         'security vulnerability.')

_PERSONA = ('You are a senior cybersecurity auditor with extensive experience '
            'in PHP application security.')

_PATTERNS = ('Apply taint analysis: trace data flow from untrusted user inputs '
             '(sources such as $_GET, $_POST, $_REQUEST, $_COOKIE, $_SESSION) '
             'to security-sensitive operations (sinks), and determine whether '
             'any unsanitized tainted data reaches a sink.')

_COT = ('Think step by step: first identify the untrusted inputs, then trace '
        'how they propagate, then examine any transformations applied to them, '
        'and finally decide whether the code is vulnerable.')

VARIANTS: dict[str, str] = {
    'A': _TASK,
    'B': f'{_PERSONA} {_TASK}',
    'C': f'{_TASK} {_PATTERNS}',
    'D': f'{_TASK} {_COT}',
    'E': f'{_PERSONA} {_TASK} {_PATTERNS} {_COT}',
}

CWE_NAMES: dict[str, tuple[str, str]] = {
    'CWE_78': ('OS command injection', 'CWE-78'),
    'CWE_89': ('SQL injection', 'CWE-89'),
    'CWE_98': ('PHP remote file inclusion', 'CWE-98'),
}

# Deliberately wrong category, used by the mismatch control
MISMATCH_MAP: dict[str, str] = {
    'CWE_78': 'CWE_89',
    'CWE_89': 'CWE_78',
    'CWE_98': 'CWE_78',
}


def build_prompt(variant: str, hint: str = 'clean', cwe: str | None = None) -> str:
    """Return the instruction text for one condition.

    variant : 'A' | 'B' | 'C' | 'D' | 'E'
    hint    : 'clean' | 'hinted' | 'mismatch'
    cwe     : e.g. 'CWE_78' (required unless hint == 'clean')
    """
    body = VARIANTS[variant]
    if hint == 'clean':
        clause = ''
    elif hint in ('hinted', 'mismatch'):
        key = cwe if hint == 'hinted' else MISMATCH_MAP[cwe]
        name, ident = CWE_NAMES[key]
        clause = f' The vulnerability class of interest is {name} ({ident}).'
    else:
        raise ValueError(f'unknown hint mode: {hint}')
    return f'{body}{clause} Return JSON.'


# --------------------------------------------------------------------------
# Pricing (USD per 1M tokens) — used only for cost reporting
# --------------------------------------------------------------------------

PRICING = {
    'gpt-4o-mini':          (0.15, 0.60),
    'gpt-3.5-turbo-0125':   (0.50, 1.50),
    'gpt-5.5-2026-04-23':   (5.00, 30.00),
}


def _price(model: str, tin: int, tout: int) -> float:
    for k, (pin, pout) in PRICING.items():
        if model.startswith(k.split('-2026')[0]):
            return tin / 1e6 * pin + tout / 1e6 * pout
    return 0.0


# --------------------------------------------------------------------------
# Experiment runner
# --------------------------------------------------------------------------

def run_experiment(bench: pd.DataFrame,
                   dataset_root: Path,
                   conditions: list[tuple[str, str]],
                   model: str,
                   out_csv: Path,
                   temperature: float | None = 0.1,
                   run_ids: tuple[int, ...] = (1,),
                   client: OpenAI | None = None,
                   sleep: float = 0.0,
                   max_retries: int = 4) -> pd.DataFrame:
    """Run every (sample, condition, run_id) combination and append to out_csv.

    bench      : DataFrame with columns sample_id, rel_path, cwe, true_label
    conditions : list of (variant, hint) e.g. [('A','clean'), ('A','hinted')]
    temperature: pass None for models that reject a custom temperature
    """
    client = client or OpenAI()
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    done: set[tuple] = set()
    if out_csv.exists():
        prev = pd.read_csv(out_csv)
        done = set(zip(prev['sample_id'], prev['condition'], prev['run_id']))
        print(f'resuming — {len(done)} calls already recorded')

    jobs = [(row, v, h, r)
            for r in run_ids
            for (v, h) in conditions
            for _, row in bench.iterrows()
            if (row['sample_id'], f'{v}_{h}', r) not in done]

    print(f'{len(jobs)} calls to make with {model}')
    if not jobs:
        return pd.read_csv(out_csv)

    buf, n_tin, n_tout, header = [], 0, 0, not out_csv.exists()

    for i, (row, variant, hint, run_id) in enumerate(jobs, 1):
        code = strip_header((dataset_root / row['rel_path']).read_text(
            encoding='utf-8', errors='replace'))
        instruction = build_prompt(variant, hint, row['cwe'])
        user_msg = f'{instruction}\n\n```php\n{code}\n```'

        kwargs = dict(model=model,
                      messages=[{'role': 'system', 'content': SYSTEM_MESSAGE},
                                {'role': 'user', 'content': user_msg}],
                      response_format={'type': 'json_object'})
        if temperature is not None:
            kwargs['temperature'] = temperature

        pred, cwe_out, conf, err = None, None, None, ''
        for attempt in range(max_retries):
            try:
                resp = client.chat.completions.create(**kwargs)
                raw = resp.choices[0].message.content
                n_tin += resp.usage.prompt_tokens
                n_tout += resp.usage.completion_tokens
                parsed = json.loads(raw)
                pred = str(parsed.get('prediction', '')).strip()
                cwe_out = str(parsed.get('cwe_type', '')).strip()
                conf = parsed.get('confidence')
                break
            except Exception as exc:                      # noqa: BLE001
                err = f'{type(exc).__name__}: {exc}'[:200]
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        buf.append({
            'sample_id':  row['sample_id'],
            'rel_path':   row['rel_path'],
            'cwe':        row['cwe'],
            'sanitizer':  row.get('sanitizer', ''),
            'true_label': row['true_label'],
            'condition':  f'{variant}_{hint}',
            'variant':    variant,
            'hint':       hint,
            'run_id':     run_id,
            'model':      model,
            'prediction': pred,
            'cwe_type':   cwe_out,
            'confidence': conf,
            'error':      err if pred is None else '',
        })

        if len(buf) >= 50 or i == len(jobs):
            pd.DataFrame(buf).to_csv(out_csv, mode='a', header=header,
                                     index=False, encoding='utf-8-sig')
            header, buf = False, []
            cost = _price(model, n_tin, n_tout)
            print(f'  {i}/{len(jobs)}  |  tokens in/out {n_tin}/{n_tout}  '
                  f'|  running cost ${cost:.3f}', flush=True)

        if sleep:
            time.sleep(sleep)

    res = pd.read_csv(out_csv)
    print(f'\ndone — {len(res)} rows in {out_csv}')
    print(f'this session cost ≈ ${_price(model, n_tin, n_tout):.3f}')
    n_err = (res['prediction'].isna()).sum()
    if n_err:
        print(f'WARNING: {n_err} calls returned no parsable prediction')
    return res
