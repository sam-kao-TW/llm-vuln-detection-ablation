"""Generate editable draw.io (.drawio) versions of the three manuscript figures.

Coordinates are plain pixels so that everything can be dragged in the editor.
Each figure is a separate file; each logical part is a separate shape.
"""
from pathlib import Path
import pandas as pd

OUT = Path('/mnt/user-data/outputs/figures')
SRC = Path('/mnt/user-data/outputs/revision')

BLUE, ORANGE, GREEN, GREY = '#0072B2', '#D55E00', '#009E73', '#666666'
FONT = 'Times New Roman'

_id = [0]


def nid():
    _id[0] += 1
    return f'n{_id[0]}'


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;')
            .replace('>', '&gt;').replace('"', '&quot;'))


def rect(x, y, w, h, fill, stroke='#000000', sw=1):
    return (f'<mxCell id="{nid()}" value="" style="rounded=0;whiteSpace=wrap;html=1;'
            f'fillColor={fill};strokeColor={stroke};strokeWidth={sw};" vertex="1" parent="1">'
            f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')


def ellipse(cx, cy, d, fill, stroke='#000000'):
    return (f'<mxCell id="{nid()}" value="" style="ellipse;whiteSpace=wrap;html=1;'
            f'fillColor={fill};strokeColor={stroke};strokeWidth=1;" vertex="1" parent="1">'
            f'<mxGeometry x="{cx-d/2:.1f}" y="{cy-d/2:.1f}" width="{d}" height="{d}" as="geometry"/></mxCell>')


def tri(cx, cy, d, fill, stroke='#000000'):
    return (f'<mxCell id="{nid()}" value="" style="triangle;direction=north;whiteSpace=wrap;html=1;'
            f'fillColor={fill};strokeColor={stroke};strokeWidth=1;" vertex="1" parent="1">'
            f'<mxGeometry x="{cx-d/2:.1f}" y="{cy-d/2:.1f}" width="{d}" height="{d}" as="geometry"/></mxCell>')


def text(x, y, w, h, s, size=11, align='center', bold=False, color='#000000',
         rotate=0):
    st = (f'text;html=1;strokeColor=none;fillColor=none;align={align};'
          f'verticalAlign=middle;whiteSpace=wrap;fontFamily={FONT};'
          f'fontSize={size};fontColor={color};')
    if bold:
        st += 'fontStyle=1;'
    if rotate:
        st += f'rotation={rotate};'
    return (f'<mxCell id="{nid()}" value="{esc(s)}" style="{st}" vertex="1" parent="1">'
            f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')


def line(x1, y1, x2, y2, color='#000000', sw=1, dashed=False):
    st = f'endArrow=none;html=1;strokeColor={color};strokeWidth={sw};'
    if dashed:
        st += 'dashed=1;dashPattern=2 3;'
    return (f'<mxCell id="{nid()}" style="{st}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{x1:.1f}" y="{y1:.1f}" as="sourcePoint"/>'
            f'<mxPoint x="{x2:.1f}" y="{y2:.1f}" as="targetPoint"/></mxGeometry></mxCell>')


def wrap(cells, name, w=1100, h=560):
    body = '\n        '.join(cells)
    return f'''<mxfile host="app.diagrams.net" type="device">
  <diagram name="{name}" id="{name}">
    <mxGraphModel dx="1200" dy="700" grid="1" gridSize="10" guides="1" tooltips="1"
                  connect="1" arrows="1" fold="1" page="1" pageScale="1"
                  pageWidth="{w}" pageHeight="{h}" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {body}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
'''


# ==================================================================== FIG 1
def figure1():
    t = pd.read_csv(SRC / 'TABLE1_full_metrics.csv')
    c = []

    # ---------------- panel (a): dot plot, specificity by model -----------
    X0, Y0, PW, PH = 90, 90, 330, 300          # axes origin (bottom-left), size
    ybot, ytop = Y0 + PH, Y0
    sy = lambda v: ybot - v * PH               # specificity -> y

    c.append(text(X0 - 30, Y0 - 45, 300, 22, '(a)  Specificity by model', 13,
                  'left', bold=True))
    # axes
    c.append(line(X0, ybot, X0 + PW, ybot, sw=1.5))
    c.append(line(X0, ybot, X0, ytop, sw=1.5))
    for v in [0, .2, .4, .6, .8, 1.0]:
        c.append(line(X0 - 5, sy(v), X0, sy(v)))
        c.append(text(X0 - 52, sy(v) - 9, 45, 18, f'{v:.1f}', 10, 'right'))
        if v:
            c.append(line(X0, sy(v), X0 + PW, sy(v), '#DDDDDD', 1))
    c.append(text(X0 - 92, Y0 + PH / 2 - 10, 120, 20, 'Specificity', 12,
                  rotate=270))

    models = [('GPT-3.5-turbo-0125', 'GPT-3.5-turbo', GREY),
              ('GPT-4o-mini', 'GPT-4o-mini', BLUE),
              ('GPT-5.5', 'GPT-5.5', ORANGE)]
    for i, (key, lab, col) in enumerate(models):
        cx = X0 + PW * (i + 0.5) / 3
        vals = t[t.Model == key].Specificity.tolist()
        n = len(vals)
        for j, v in enumerate(vals):
            jitter = (j - (n - 1) / 2) * (7 if n > 2 else 16)
            c.append(ellipse(cx + jitter, sy(v), 9, col))
        c.append(text(cx - 60, ybot + 8, 120, 18, lab, 11))
        c.append(text(cx - 60, ybot + 26, 120, 16,
                      f'{n} conditions', 9, color='#666666'))

    c.append(line(X0, sy(.5), X0 + PW, sy(.5), '#999999', 1, dashed=True))
    c.append(text(X0 + PW - 150, sy(.5) - 20, 150, 16, 'chance level', 9,
                  'right', color='#666666'))
    # annotation
    c.append(text(X0 + 10, sy(.05) - 40, 190, 34,
                  'saturated: near-constant\nVulnerable verdict', 9, 'left',
                  color='#666666'))

    # ---------------- panel (b): F1 vs MCC --------------------------------
    X1, PW1 = 560, 330
    fx = lambda v: X1 + (v - 0.60) / 0.30 * PW1        # F1 0.60-0.90
    my = lambda v: ybot - (v + 0.15) / 0.90 * PH       # MCC -0.15-0.75

    c.append(text(X1 - 30, Y0 - 45, 340, 22,
                  '(b)  F1 conceals discrimination', 13, 'left', bold=True))
    c.append(line(X1, ybot, X1 + PW1, ybot, sw=1.5))
    c.append(line(X1, ybot, X1, ytop, sw=1.5))
    for v in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:
        c.append(line(fx(v), ybot, fx(v), ybot + 5))
        c.append(text(fx(v) - 25, ybot + 8, 50, 18, f'{v:.2f}', 10))
    for v in [-0.1, 0, 0.2, 0.4, 0.6]:
        c.append(line(X1 - 5, my(v), X1, my(v)))
        c.append(text(X1 - 52, my(v) - 9, 45, 18, f'{v:.1f}', 10, 'right'))
    c.append(text(X1 + PW1 / 2 - 40, ybot + 30, 80, 18, 'F1', 12))
    c.append(text(X1 - 100, Y0 + PH / 2 - 10, 140, 20,
                  'Matthews correlation', 12, rotate=270))
    c.append(line(X1, my(0), X1 + PW1, my(0), '#000000', 1))
    c.append(line(fx(0.667), ybot, fx(0.667), ytop, '#999999', 1, dashed=True))
    c.append(text(fx(0.667) + 6, ytop + 4, 170, 30,
                  'F1 of a constant\nclassifier', 9, 'left', color='#666666'))

    for key, lab, col in models:
        sub = t[t.Model == key]
        for _, r in sub.iterrows():
            if key == 'GPT-5.5':
                c.append(tri(fx(r.F1), my(r.MCC), 11, col))
            else:
                c.append(ellipse(fx(r.F1), my(r.MCC), 9, col))

    # ---------------- shared legend --------------------------------------
    lx, ly = X0 + 6, Y0 + 6
    c.append(rect(lx - 6, ly - 6, 190, 74, '#FFFFFF', '#CCCCCC', 1))
    for k, (key, lab, col) in enumerate(models):
        c.append(ellipse(lx + 8, ly + 12 + k * 20, 9, col))
        c.append(text(lx + 20, ly + 3 + k * 20, 160, 18, lab, 10, 'left'))

    (OUT / 'Figure1_capability_threshold.drawio').write_text(
        wrap(c, 'Figure1_capability_threshold', 1000, 500))
    print('  Figure1_capability_threshold.drawio')


# ==================================================================== FIG 2
def figure2():
    t = pd.read_csv(SRC / 'TABLE4_gpt55_by_sanitizer_mechanism.csv')
    s = t[t.TrueLabel == 'Safe'].sort_values('A_rate', ascending=False)
    c = []

    X0, Y0, PW = 250, 80, 420
    BAR, GAP = 26, 16

    c.append(text(X0 - 200, Y0 - 46, 620, 22,
                  'GPT-5.5: identification of safe code, by sanitisation mechanism',
                  13, 'left', bold=True))
    c.append(line(X0, Y0 - 6, X0, Y0 + len(s) * (BAR + GAP), sw=1.5))
    for v in [0, .2, .4, .6, .8, 1.0]:
        x = X0 + v * PW
        c.append(line(x, Y0 - 6, x, Y0 + len(s) * (BAR + GAP), '#DDDDDD', 1))
        c.append(text(x - 25, Y0 + len(s) * (BAR + GAP) + 6, 50, 18,
                      f'{v:.1f}', 10))
    c.append(text(X0 + PW / 2 - 150, Y0 + len(s) * (BAR + GAP) + 28, 300, 18,
                  'Proportion correctly identified as safe', 12))

    for i, (_, r) in enumerate(s.iterrows()):
        y = Y0 + i * (BAR + GAP)
        typeish = r.Mechanism in ('Type coercion', 'Whitelist')
        col = GREEN if typeish else ORANGE
        c.append(rect(X0, y, r.A_rate * PW, BAR, col))
        c.append(text(X0 - 210, y + 3, 200, 20, r.Mechanism, 11, 'right'))
        c.append(text(X0 + r.A_rate * PW + 8, y + 3, 130, 20,
                      f'{r.A_rate:.2f}   (n = {int(r.n)})', 10, 'left'))

    ly = Y0 + len(s) * (BAR + GAP) + 56
    c.append(rect(X0, ly, 14, 14, GREEN))
    c.append(text(X0 + 20, ly - 2, 200, 18, 'Type-level guarantee', 10, 'left'))
    c.append(rect(X0 + 210, ly, 14, 14, ORANGE))
    c.append(text(X0 + 230, ly - 2, 200, 18, 'Escaping or filtering', 10, 'left'))
    c.append(text(X0 - 210, ly + 26, 640, 34,
                  'Aggregated: 94.3% for type-level mechanisms against 21.2% for '
                  'escaping\n(Fisher exact test, odds ratio 61.5, p = 3.5 × 10⁻²¹)',
                  10, 'left', color='#666666'))

    (OUT / 'Figure2_sanitisation_mechanism.drawio').write_text(
        wrap(c, 'Figure2_sanitisation_mechanism', 800, 480))
    print('  Figure2_sanitisation_mechanism.drawio')


# ==================================================================== FIG 3
def figure3():
    c = []
    Y0, PH = 90, 280
    ybot = Y0 + PH

    # ---- panel (a) ------------------------------------------------------
    X0, PW = 90, 300
    sy = lambda v: ybot - v / 190 * PH
    c.append(text(X0 - 30, Y0 - 45, 320, 22, '(a)  Accuracy by stratum', 13,
                  'left', bold=True))
    c.append(line(X0, ybot, X0 + PW, ybot, sw=1.5))
    c.append(line(X0, ybot, X0, Y0, sw=1.5))
    for v in [0, 50, 100, 150]:
        c.append(line(X0 - 5, sy(v), X0, sy(v)))
        c.append(text(X0 - 52, sy(v) - 9, 45, 18, str(v), 10, 'right'))
        if v:
            c.append(line(X0, sy(v), X0 + PW, sy(v), '#DDDDDD', 1))
    c.append(text(X0 - 100, Y0 + PH / 2 - 10, 150, 20, 'Correct predictions',
                  12, rotate=270))

    for k, (lab, A, E, p) in enumerate([('Vulnerable  (n = 180)', 162, 144, 'p = 0.0003'),
                                        ('Safe  (n = 180)', 126, 133, 'p = 0.065')]):
        gx = X0 + PW * (k + 0.5) / 2
        for j, (v, col) in enumerate([(A, BLUE), (E, ORANGE)]):
            bx = gx - 46 + j * 46
            c.append(rect(bx, sy(v), 40, ybot - sy(v), col))
            c.append(text(bx - 10, sy(v) - 20, 60, 18, str(v), 10))
        c.append(text(gx - 90, ybot + 8, 180, 18, lab, 11))
        c.append(text(gx - 60, sy(max(A, E)) - 42, 120, 18, p, 10,
                      color='#666666'))

    # ---- panel (b) ------------------------------------------------------
    X1, PW1 = 560, 340
    sy2 = lambda v: ybot - v / 36 * PH
    c.append(text(X1 - 30, Y0 - 45, 340, 22, '(b)  Discordant pairs', 13,
                  'left', bold=True))
    c.append(line(X1, ybot, X1 + PW1, ybot, sw=1.5))
    c.append(line(X1, ybot, X1, Y0, sw=1.5))
    for v in [0, 10, 20, 30]:
        c.append(line(X1 - 5, sy2(v), X1, sy2(v)))
        c.append(text(X1 - 52, sy2(v) - 9, 45, 18, str(v), 10, 'right'))
        if v:
            c.append(line(X1, sy2(v), X1 + PW1, sy2(v), '#DDDDDD', 1))
    c.append(text(X1 - 105, Y0 + PH / 2 - 10, 160, 20, 'Discordant samples',
                  12, rotate=270))

    for k, (lab, a, e) in enumerate([('Vulnerable\nsamples', 21, 3),
                                     ('Safe\nsamples', 2, 9),
                                     ('Verdict shift\n(V to S)', 30, 5)]):
        gx = X1 + PW1 * (k + 0.5) / 3
        for j, (v, col) in enumerate([(a, BLUE), (e, ORANGE)]):
            bx = gx - 42 + j * 42
            c.append(rect(bx, sy2(v), 36, ybot - sy2(v), col))
            c.append(text(bx - 12, sy2(v) - 20, 60, 18, str(v), 10))
        c.append(text(gx - 70, ybot + 8, 140, 34, lab, 11))

    # ---- legend ---------------------------------------------------------
    lx, ly = X1 + 20, Y0 + 4
    c.append(rect(lx - 6, ly - 6, 250, 52, '#FFFFFF', '#CCCCCC', 1))
    c.append(rect(lx + 4, ly + 6, 14, 14, BLUE))
    c.append(text(lx + 24, ly + 4, 220, 18, 'Baseline (A)', 10, 'left'))
    c.append(rect(lx + 4, ly + 26, 14, 14, ORANGE))
    c.append(text(lx + 24, ly + 24, 220, 18, 'Full Framework (E)', 10, 'left'))

    (OUT / 'Figure3_tradeoff.drawio').write_text(
        wrap(c, 'Figure3_tradeoff', 1000, 480))
    print('  Figure3_tradeoff.drawio')


if __name__ == '__main__':
    print('Generating draw.io figures:')
    figure1()
    figure2()
    figure3()
    print('\nWritten to', OUT)
