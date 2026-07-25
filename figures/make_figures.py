"""Generate the three figures for the revised manuscript.

Output: 600-dpi PNG (for the Word manuscript) and PDF (for archival).
Sizing follows IEEE Access: 3.5 in single column, 7.16 in double column.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path('/mnt/user-data/outputs/figures')
OUT.mkdir(exist_ok=True, parents=True)
SRC = Path('/mnt/user-data/outputs/revision')

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'font.size': 8,
    'axes.labelsize': 8,
    'axes.titlesize': 8.5,
    'xtick.labelsize': 7.5,
    'ytick.labelsize': 7.5,
    'legend.fontsize': 7.5,
    'axes.linewidth': 0.6,
    'grid.linewidth': 0.4,
    'lines.linewidth': 1.1,
    'figure.dpi': 120,
})

# Colour-blind-safe (Okabe–Ito)
BLUE, ORANGE, GREEN, GREY = '#0072B2', '#D55E00', '#009E73', '#666666'


def save(fig, name):
    for ext in ('png', 'pdf'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=600, bbox_inches='tight',
                    facecolor='white')
    plt.close(fig)
    print(f'  {name}.png / .pdf')


# ---------------------------------------------------------------- Figure 1
def figure1():
    """Capability threshold: specificity by model and condition."""
    t = pd.read_csv(SRC / 'TABLE1_full_metrics.csv')
    order = ['GPT-3.5-turbo-0125', 'GPT-4o-mini', 'GPT-5.5']
    labels = ['GPT-3.5-turbo', 'GPT-4o-mini', 'GPT-5.5']

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.16, 2.7),
                                   gridspec_kw={'width_ratios': [1.55, 1]})

    # -- left: specificity per condition --------------------------------
    conds = [f'{v}_{h}' for v in 'ABCDE' for h in ('clean', 'hinted')]
    xs = np.arange(len(conds))
    w = 0.27
    for k, (m, lab, col) in enumerate(zip(order, labels, [GREY, BLUE, ORANGE])):
        sub = t[t.Model == m].set_index(t[t.Model == m].Variant + '_' +
                                        t[t.Model == m].Hint)
        vals = [sub.Specificity.get(c, np.nan) for c in conds]
        ax1.bar(xs + (k - 1) * w, vals, w, label=lab, color=col,
                edgecolor='black', linewidth=0.4)
    ax1.set_xticks(xs)
    ax1.set_xticklabels([c.replace('_clean', '\nneutral').replace('_hinted', '\nnaming')
                         for c in conds], fontsize=6.5)
    ax1.set_ylabel('Specificity')
    ax1.set_ylim(0, 1.0)
    ax1.axhline(0.5, color='black', lw=0.5, ls=':', alpha=0.6)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_axisbelow(True)
    ax1.legend(frameon=False, loc='upper left', ncol=1)
    ax1.set_title('(a)  Specificity by prompt condition', loc='left')
    # mark the conditions GPT-5.5 was not run on
    for i, c in enumerate(conds):
        if c not in ('A_clean', 'E_clean'):
            ax1.text(i + w, 0.02, 'n/e', ha='center', fontsize=5.6,
                     color=ORANGE, rotation=90, va='bottom')

    # -- right: F1 vs MCC ------------------------------------------------
    for m, lab, col, mk in zip(order, labels, [GREY, BLUE, ORANGE], ['o', 's', '^']):
        sub = t[t.Model == m]
        ax2.scatter(sub.F1, sub.MCC, s=26, color=col, marker=mk,
                    edgecolor='black', linewidth=0.4, label=lab, zorder=3)
    ax2.axhline(0, color='black', lw=0.6)
    ax2.set_xlabel('F1')
    ax2.set_ylabel('Matthews correlation coefficient')
    ax2.set_xlim(0.55, 0.90)
    ax2.set_ylim(-0.15, 0.72)
    ax2.grid(alpha=0.3)
    ax2.set_axisbelow(True)
    ax2.set_title('(b)  F1 conceals discrimination', loc='left')
    ax2.annotate('constant-classifier F1',
                 xy=(0.667, 0.02), xytext=(0.70, 0.22),
                 fontsize=6.8, color='#444',
                 arrowprops=dict(arrowstyle='->', lw=0.5, color='#444'))
    ax2.axvline(0.667, color='black', lw=0.5, ls=':', alpha=0.6)

    fig.tight_layout(w_pad=1.6)
    save(fig, 'Figure1_capability_threshold')


# ---------------------------------------------------------------- Figure 2
def figure2():
    """Sanitisation mechanism: type-level safety versus escaping."""
    t = pd.read_csv(SRC / 'TABLE4_gpt55_by_sanitizer_mechanism.csv')
    s = t[t.TrueLabel == 'Safe'].sort_values('A_rate', ascending=True)

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    y = np.arange(len(s))
    typeish = s.Mechanism.isin(['Type coercion', 'Whitelist'])
    cols = [GREEN if v else ORANGE for v in typeish]

    ax.barh(y, s.A_rate, 0.62, color=cols, edgecolor='black', linewidth=0.4)
    for i, (r, n) in enumerate(zip(s.A_rate, s.n)):
        ax.text(r + 0.02, i, f'{r:.2f}  (n={n})', va='center', fontsize=6.6)

    ax.set_yticks(y)
    ax.set_yticklabels(s.Mechanism)
    ax.set_xlabel('Proportion correctly identified as safe')
    ax.set_xlim(0, 1.18)
    ax.grid(axis='x', alpha=0.3)
    ax.set_axisbelow(True)

    h = [plt.Rectangle((0, 0), 1, 1, fc=GREEN, ec='black', lw=0.4),
         plt.Rectangle((0, 0), 1, 1, fc=ORANGE, ec='black', lw=0.4)]
    ax.legend(h, ['Type-level guarantee', 'Escaping / filtering'],
              frameon=False, loc='lower right', fontsize=7)
    fig.tight_layout()
    save(fig, 'Figure2_sanitisation_mechanism')


# ---------------------------------------------------------------- Figure 3
def figure3():
    """The trade-off: Baseline versus Full Framework on GPT-5.5."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.16, 2.5),
                                   gridspec_kw={'width_ratios': [1, 1.15]})

    # -- left: correct counts by stratum ---------------------------------
    strata = ['Vulnerable\n(n = 180)', 'Safe\n(n = 180)']
    A = [162, 126]
    E = [144, 133]
    xs = np.arange(2)
    w = 0.34
    b1 = ax1.bar(xs - w / 2, A, w, label='Baseline (A)', color=BLUE,
                 edgecolor='black', linewidth=0.4)
    b2 = ax1.bar(xs + w / 2, E, w, label='Full Framework (E)', color=ORANGE,
                 edgecolor='black', linewidth=0.4)
    for b in list(b1) + list(b2):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 2,
                 f'{int(b.get_height())}', ha='center', fontsize=6.8)
    ax1.set_xticks(xs)
    ax1.set_xticklabels(strata)
    ax1.set_ylabel('Correct predictions')
    ax1.set_ylim(0, 195)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_axisbelow(True)
    ax1.legend(frameon=False, loc='lower right', fontsize=7)
    ax1.set_title('(a)  Accuracy by stratum', loc='left')
    ax1.text(0, 173, 'p = 0.0003', ha='center', fontsize=6.8, color=GREY)
    ax1.text(1, 147, 'p = 0.065', ha='center', fontsize=6.8, color=GREY)

    # -- right: discordant counts ----------------------------------------
    cats = ['Vulnerable\nsamples', 'Safe\nsamples', 'Verdict\nshift']
    only_a = [21, 2, 30]
    only_e = [3, 9, 5]
    xs = np.arange(3)
    b1 = ax2.bar(xs - w / 2, only_a, w, color=BLUE, edgecolor='black',
                 linewidth=0.4, label='Favours Baseline')
    b2 = ax2.bar(xs + w / 2, only_e, w, color=ORANGE, edgecolor='black',
                 linewidth=0.4, label='Favours Full Framework')
    for b in list(b1) + list(b2):
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6,
                 f'{int(b.get_height())}', ha='center', fontsize=6.8)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(cats)
    ax2.set_ylabel('Discordant samples')
    ax2.set_ylim(0, 36)
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=False, loc='upper left', fontsize=7)
    ax2.set_title('(b)  Discordant pairs', loc='left')

    fig.tight_layout(w_pad=1.8)
    save(fig, 'Figure3_tradeoff')


if __name__ == '__main__':
    print('Generating figures:')
    figure1()
    figure2()
    figure3()
    print('\nAll figures written to', OUT)
