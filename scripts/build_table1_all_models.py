"""Rebuild TABLE1_full_metrics.csv with all three models across all ten conditions.

The published table carried only two conditions for GPT-5.5. Schema and rounding
are preserved so the figure scripts need no adjustment beyond removing the
'not evaluated' markers.

Run from the revision working directory; writes TABLE1_full_metrics.csv.
"""
import os
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportion_confint

# Paths default to the repository layout, so that a fresh clone runs with
#     python scripts/build_table1_all_models.py
# Set REPRO_DATA to run against another location, for instance a Google Drive
# working directory in Colab.
_HERE = Path(__file__).resolve().parent
WORK = Path(os.environ.get('REPRO_DATA', _HERE.parent / 'data'))
OUT = WORK
OUT.mkdir(exist_ok=True, parents=True)

SOURCES = [
    ('GPT-3.5-turbo-0125', 'crossgen_gpt35.csv'),
    ('GPT-4o-mini',        'main_4omini.csv'),
    ('GPT-5.5',            'frontier_gpt55.csv'),
]
CONDS = [(v, h) for v in 'ABCDE' for h in ('clean', 'hinted')]


def ci(k, n):
    lo, hi = proportion_confint(k, n, method='wilson')
    return f'[{lo:.3f}, {hi:.3f}]'


def row(model, variant, hint, g):
    tp = int(((g.true_label == 'Vulnerable') & (g.prediction == 'Vulnerable')).sum())
    fn = int(((g.true_label == 'Vulnerable') & (g.prediction == 'Safe')).sum())
    tn = int(((g.true_label == 'Safe') & (g.prediction == 'Safe')).sum())
    fp = int(((g.true_label == 'Safe') & (g.prediction == 'Vulnerable')).sum())

    rec  = tp / (tp + fn) if tp + fn else np.nan
    spec = tn / (tn + fp) if tn + fp else np.nan
    prec = tp / (tp + fp) if tp + fp else np.nan
    f1   = 2 * prec * rec / (prec + rec) if prec and rec and (prec + rec) else np.nan

    # MCC is undefined when a margin is zero — that is, when the model emits a
    # single verdict for every sample. Reported as 0 by convention; the table
    # note must say so, since a degenerate classifier is not the same thing as
    # one that happens to score zero.
    den = np.sqrt(float((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)))
    mcc = (tp * tn - fp * fn) / den if den else 0.0

    return {
        'Model': model, 'Variant': variant, 'Hint': hint,
        'TP': tp, 'FN': fn, 'TN': tn, 'FP': fp,
        'Recall': round(rec, 3), 'Recall_CI': ci(tp, tp + fn),
        'Specificity': round(spec, 3), 'Spec_CI': ci(tn, tn + fp),
        'Precision': round(prec, 3), 'F1': round(f1, 3),
        'BalancedAcc': round((rec + spec) / 2, 3), 'MCC': round(mcc, 3),
        'MCC_defined': bool(den),
    }


rows = []
for model, fname in SOURCES:
    d = pd.read_csv(WORK / fname)
    d = d[d.run_id == 1]
    for variant, hint in CONDS:
        g = d[(d.variant == variant) & (d.hint == hint)]
        assert len(g) == 360, f'{model} {variant}_{hint}: {len(g)} rows, expected 360'
        rows.append(row(model, variant, hint, g))

t1 = pd.DataFrame(rows)
assert len(t1) == 30, f'expected 30 rows, built {len(t1)}'

undefined = t1[~t1.MCC_defined]
if len(undefined):
    print(f'MCC undefined in {len(undefined)} conditions (single-verdict classifier):')
    print(undefined[['Model', 'Variant', 'Hint', 'TP', 'FN', 'TN', 'FP']].to_string(index=False))
    print()

t1.drop(columns=['MCC_defined']).to_csv(OUT / 'TABLE1_full_metrics.csv', index=False)
print('written:', OUT / 'TABLE1_full_metrics.csv')
print()
print(t1.groupby('Model')[['Specificity', 'BalancedAcc', 'MCC']]
        .agg(['min', 'max']).round(3).to_string())
