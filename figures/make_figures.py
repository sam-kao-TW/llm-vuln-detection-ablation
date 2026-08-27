"""Generate the three figures for the revised manuscript.

Output: 600-dpi PNG (for the Word manuscript) and PDF (for archival).
Sizing follows IEEE Access: 3.5 in single column, 7.16 in double column.
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Paths default to the repository layout, so that a fresh clone runs with
#     python figures/make_figures.py
# Set REPRO_DATA / REPRO_FIGS to run against another location, for instance a
# Google Drive working directory in Colab.
_HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get('REPRO_FIGS', _HERE))
SRC = Path(os.environ.get('REPRO_DATA', _HERE.parent / 'data'))
OUT.mkdir(exist_ok=True, parents=True)

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
    ax1.set_xticklabels([c.replace('_clean', ' neutral').replace('_hinted', ' naming')
                         for c in conds], fontsize=6.5, rotation=45, ha='right')
    ax1.tick_params(axis='x', pad=1)
    ax1.set_ylabel('Specificity')
    ax1.set_ylim(0, 1.0)
    ax1.axhline(0.5, color='black', lw=0.5, ls=':', alpha=0.6)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_axisbelow(True)
    ax1.set_title('(a)  Specificity by prompt condition', loc='left')

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
    ax2.legend(frameon=False, loc='lower right', fontsize=7,
               handletextpad=0.4, borderaxespad=0.6)
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
    t = pd.read_csv(SRC / 'TABLE4_gpt55_by_sanitizer_mechanism.csv',
                    keep_default_na=False, na_values=[''])
    s = t[(t.TrueLabel == 'Safe') & (t.Mechanism != 'No sanitiser')]
    s = s.sort_values('A_clean_rate', ascending=True)

    fig, ax = plt.subplots(figsize=(3.5, 2.6))
    y = np.arange(len(s))
    TYPE_LEVEL = ['Type coercion', 'Whitelist']
    ESCAPING = ['Regex replacement', 'HTML escaping', 'Quote escaping']
    cols = [GREEN if m in TYPE_LEVEL else ORANGE if m in ESCAPING else GREY
            for m in s.Mechanism]

    ax.barh(y, s.A_clean_rate, 0.62, color=cols, edgecolor='black', linewidth=0.4)
    for i, (r, n) in enumerate(zip(s.A_clean_rate, s.n)):
        ax.text(r + 0.02, i, f'{r:.2f}  (n={n})', va='center', fontsize=6.2)

    ax.set_yticks(y)
    ax.set_yticklabels(s.Mechanism)
    ax.set_xlabel('Proportion correctly identified as safe')
    ax.set_xlim(0, 1.52)
    ax.grid(axis='x', alpha=0.3)
    ax.set_axisbelow(True)

    h = [plt.Rectangle((0, 0), 1, 1, fc=GREEN, ec='black', lw=0.4),
         plt.Rectangle((0, 0), 1, 1, fc=ORANGE, ec='black', lw=0.4),
         plt.Rectangle((0, 0), 1, 1, fc=GREY, ec='black', lw=0.4)]
    ax.legend(h, ['Type-level guarantee', 'Escaping / filtering',
                  'Neither group'],
              frameon=False, fontsize=6.5, loc='upper center',
              bbox_to_anchor=(0.5, -0.20), ncol=3, borderaxespad=0,
              handlelength=1.1, columnspacing=1.0)
    fig.tight_layout()
    save(fig, 'Figure2_sanitisation_mechanism')


# ---------------------------------------------------------------- Figure 3
def figure3():
    """Component attribution and the cost of category naming, on GPT-5.5."""
    t3 = pd.read_csv(SRC / 'TABLE3_component_attribution.csv')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.16, 2.6),
                                   gridspec_kw={'width_ratios': [1, 1.15]})

    # -- left: each component against the shared baseline, vulnerable stratum
    comps = [('A_clean vs B_clean', 'Persona'),
             ('A_clean vs C_clean', 'Taint\ninstruction'),
             ('A_clean vs D_clean', 'Chain of\nthought'),
             ('A_clean vs E_clean', 'All three')]
    v = t3[t3.Stratum == 'Vulnerable'].set_index('Contrast')

    lost   = [int(v.loc[c].A_only) for c, _ in comps]
    gained = [int(v.loc[c].B_only) for c, _ in comps]
    sig    = [bool(v.loc[c].sig_holm) for c, _ in comps]

    xs = np.arange(len(comps))
    w = 0.34
    b1 = ax1.bar(xs - w / 2, lost, w, color=BLUE, edgecolor='black',
                 linewidth=0.4, label='Detections lost')
    b2 = ax1.bar(xs + w / 2, gained, w, color=ORANGE, edgecolor='black',
                 linewidth=0.4, label='Detections gained')
    for b in list(b1) + list(b2):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.5,
                 f'{int(b.get_height())}', ha='center', fontsize=6.8)
    for i, ok in enumerate(sig):
        if ok:
            ax1.text(i, max(lost[i], gained[i]) + 3.2, '*', ha='center',
                     fontsize=11, color='black')

    ax1.set_xticks(xs)
    ax1.set_xticklabels([lab for _, lab in comps], fontsize=6.8)
    ax1.set_ylabel('Discordant samples')
    ax1.set_ylim(0, 37)
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_axisbelow(True)
    ax1.legend(frameon=True, loc='upper left', fontsize=6.6,
               handlelength=1.2, borderaxespad=0.3, framealpha=0.95,
               edgecolor='none')
    ax1.set_title('(a)  Each component against the baseline\n'
                  '(vulnerable samples)', loc='left', fontsize=7.6)

    # -- right: category naming within every structural variant ------------
    pairs = [(f'{v_}_clean vs {v_}_hinted', v_) for v_ in 'ABCDE']
    vv = t3[t3.Stratum == 'Vulnerable'].set_index('Contrast')
    ss = t3[t3.Stratum == 'Safe'].set_index('Contrast')

    v_lost = [int(vv.loc[c].A_only) for c, _ in pairs]
    s_gain = [int(ss.loc[c].B_only) for c, _ in pairs]

    xs = np.arange(len(pairs))
    b1 = ax2.bar(xs - w / 2, v_lost, w, color=BLUE, edgecolor='black',
                 linewidth=0.4, label='Vulnerabilities missed')
    b2 = ax2.bar(xs + w / 2, s_gain, w, color=ORANGE, edgecolor='black',
                 linewidth=0.4, label='False positives avoided')
    for b in list(b1) + list(b2):
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8,
                 f'{int(b.get_height())}', ha='center', fontsize=6.8)

    ax2.set_xticks(xs)
    ax2.set_xticklabels([f'{lab}' for _, lab in pairs])
    ax2.set_xlabel('Structural variant')
    ax2.set_ylabel('Discordant samples')
    ax2.set_ylim(0, 92)
    ax2.grid(axis='y', alpha=0.3)
    ax2.set_axisbelow(True)
    ax2.legend(frameon=True, loc='upper right', fontsize=6.6,
               handlelength=1.2, borderaxespad=0.3, framealpha=0.95,
               edgecolor='none')
    ax2.set_title('(b)  Cost of naming the category\n'
                  '(every contrast significant after Holm)',
                  loc='left', fontsize=7.6)

    fig.tight_layout(w_pad=1.8)
    save(fig, 'Figure3_component_attribution')


if __name__ == '__main__':
    print('Generating figures:')
    figure1()
    figure2()
    figure3()
    print('\nAll figures written to', OUT)
