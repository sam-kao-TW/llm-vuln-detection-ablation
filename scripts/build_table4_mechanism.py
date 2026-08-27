"""Rebuild TABLE4_gpt55_by_sanitizer_mechanism.csv over the complete factorial.

Two changes from the published version. All 180 safe samples are included: the
previous table omitted two samples carrying no sanitiser and two using
`escapeshellarg`, which the mechanism taxonomy had left unassigned. And rates
are reported for every condition rather than for Baseline and Full alone, so
the asymmetry can be seen to hold across the factorial rather than within one
contrast.

The published two-condition figures are recomputed alongside, so the change
introduced by the wider inclusion can be read off directly.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd

# Paths default to the repository layout, so that a fresh clone runs with
#     python scripts/build_table4_mechanism.py
# Set REPRO_DATA to run against another location, for instance a Google Drive
# working directory in Colab.
_HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get('REPRO_DATA', _HERE.parent / 'data'))
OUT = WORK
OUT.mkdir(exist_ok=True, parents=True)

CONDS = [f'{v}_{h}' for v in 'ABCDE' for h in ('clean', 'hinted')]

MECHANISM = {
    **{k: 'Type coercion' for k in [
        'CAST-cast_float', 'CAST-cast_float_sort_of', 'CAST-cast_int',
        'CAST-cast_int_sort_of', 'CAST-cast_int_sort_of2',
        'CAST-func_settype_float', 'CAST-func_settype_int',
        'func_floatval', 'func_intval',
        'func_FILTER-CLEANING-number_float_filter',
        'func_FILTER-CLEANING-number_int_filter',
        'func_FILTER-VALIDATION-number_float_filter',
        'func_FILTER-VALIDATION-number_int_filter']},
    **{k: 'Whitelist' for k in [
        'ternary_white_list', 'whitelist_using_array',
        'whitelist_using_array_from']},
    **{k: 'Regex validation' for k in [
        'func_preg_match-letters_numbers', 'func_preg_match-only_letters',
        'func_preg_match-only_numbers', 'func_preg_match-no_filtering']},
    **{k: 'Regex replacement' for k in [
        'func_preg_replace', 'func_preg_replace2']},
    **{k: 'HTML escaping' for k in [
        'func_htmlentities', 'func_htmlspecialchars']},
    **{k: 'Quote escaping' for k in [
        'func_addslashes', 'func_escapeshellarg',
        'func_mysql_real_escape_string',
        'object-func_mysql_real_escape_string',
        'object-func_mysql_real_escape_stringGetter',
        'func_FILTER-CLEANING-magic_quotes_filter']},
    **{k: 'Special-char filter' for k in [
        'func_FILTER-CLEANING-special_chars_filter',
        'func_FILTER-CLEANING-full_special_chars_filter']},
    **{k: 'Email filter' for k in [
        'func_FILTER-VALIDATION-email_filter',
        'func_FILTER-CLEANING-email_filter']},
    'no_sanitizing': 'No sanitiser',
}

# `escapeshellarg` sits in Quote escaping on the reading that it escapes
# metacharacters for a shell sink, as the other members escape for their own
# sinks. The published table left it unassigned; the note below records the
# effect of the change.
PREVIOUSLY_OMITTED = ['no_sanitizing', 'func_escapeshellarg']

f55 = pd.read_csv(WORK / 'frontier_gpt55.csv')
f55 = f55[f55.run_id == 1].copy()
f55['correct'] = f55.prediction == f55.true_label
f55['mechanism'] = f55.sanitizer.map(MECHANISM)

unmapped = sorted(f55[f55.mechanism.isna()].sanitizer.unique())
assert not unmapped, f'unmapped sanitisers: {unmapped}'

rows = []
for label in ('Safe', 'Vulnerable'):
    sub = f55[f55.true_label == label]
    for mech, g in sub.groupby('mechanism'):
        n = g[g.condition == 'A_clean'].shape[0]
        if not n:
            continue
        rec = {'TrueLabel': label, 'Mechanism': mech, 'n': n}
        for c in CONDS:
            gc = g[g.condition == c]
            rec[f'{c}_correct'] = int(gc.correct.sum())
            rec[f'{c}_rate'] = round(gc.correct.mean(), 3)
        rows.append(rec)

t4 = pd.DataFrame(rows).sort_values(['TrueLabel', 'A_clean_rate'])
t4.to_csv(OUT / 'TABLE4_gpt55_by_sanitizer_mechanism.csv', index=False)

print('written:', OUT / 'TABLE4_gpt55_by_sanitizer_mechanism.csv')
print()
safe = t4[t4.TrueLabel == 'Safe']
print(safe[['Mechanism', 'n', 'A_clean_rate', 'E_clean_rate',
            'A_hinted_rate', 'E_hinted_rate']].to_string(index=False))
print(f'\\nsafe samples covered: {safe.n.sum()} (expect 180)')

# --- effect of including the previously omitted samples -------------------
om = f55[(f55.true_label == 'Safe') & (f55.sanitizer.isin(PREVIOUSLY_OMITTED))
         & (f55.condition == 'A_clean')]
print(f'\\npreviously omitted from the stratification: {len(om)} samples')
print(om.groupby('sanitizer').size().to_string())
