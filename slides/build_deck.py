"""Build the vishing proposal deck as an editable .pptx."""
from pptx import Presentation
from pptx.util import Inches as In, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR

# ---------- tokens ----------
INK   = RGBColor(0x15, 0x1A, 0x21)
INK2  = RGBColor(0x3C, 0x45, 0x51)
MUTED = RGBColor(0x6B, 0x76, 0x84)
BLUE  = RGBColor(0x1A, 0x6A, 0xA8)
RED   = RGBColor(0xB0, 0x39, 0x2E)
AMBER = RGBColor(0x9E, 0x67, 0x12)
RULE  = RGBColor(0xD0, 0xD6, 0xDE)
PANEL = RGBColor(0xF1, 0xF3, 0xF6)
WASH_B= RGBColor(0xE6, 0xEE, 0xF6)
WASH_R= RGBColor(0xF7, 0xE9, 0xE7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

DISP = "Arial"      # headings
BODY = "Calibri"    # running text
MONO = "Consolas"   # data, labels, codec names

W, H = 13.333, 7.5
M    = 0.72          # side margin

prs = Presentation()
prs.slide_width  = In(W)
prs.slide_height = In(H)
BLANK = prs.slide_layouts[6]


# ---------- helpers ----------
def slide():
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = WHITE
    return s


def tb(s, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = s.shapes.add_textbox(In(x), In(y), In(w), In(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    tf.paragraphs[0].alignment = align
    return tf


def para(tf, first=False, space_after=6, space_before=0, line=1.15, align=None):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    p.line_spacing = line
    if align is not None:
        p.alignment = align
    return p


def run(p, text, size=14, bold=False, color=INK2, font=BODY, italic=False):
    r = p.add_run()
    r.text = text
    f = r.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.name = font
    f.color.rgb = color
    return r


def rect(s, x, y, w, h, fill=None, line=None, lw=1.0):
    sh = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, In(x), In(y), In(w), In(h))
    sh.shadow.inherit = False
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.text_frame.text = ""
    return sh


def oval(s, cx, cy, d, fill, line=WHITE, lw=1.5):
    sh = s.shapes.add_shape(MSO_SHAPE.OVAL, In(cx - d / 2), In(cy - d / 2), In(d), In(d))
    sh.shadow.inherit = False
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.color.rgb = line
    sh.line.width = Pt(lw)
    sh.text_frame.text = ""
    return sh


def line(s, x1, y1, x2, y2, color=RULE, lw=1.0, dash=False):
    c = s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, In(x1), In(y1), In(x2), In(y2))
    c.line.color.rgb = color
    c.line.width = Pt(lw)
    if dash:
        from pptx.enum.dml import MSO_LINE_DASH_STYLE
        c.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    return c


def eyebrow(s, act, label):
    tf = tb(s, M, 0.42, W - 2 * M, 0.3)
    p = para(tf, first=True, space_after=0)
    run(p, act.upper(), 11, True, AMBER, MONO)
    run(p, "     |     ", 11, False, RULE, MONO)
    run(p, label.upper(), 11, False, MUTED, MONO)


def title(s, parts, y=0.82, size=34):
    """parts: list of (text, color) tuples."""
    tf = tb(s, M, y, W - 2 * M - 0.4, 1.0)
    p = para(tf, first=True, space_after=0, line=1.06)
    for text, col in parts:
        run(p, text, size, True, col, DISP)


def foot(s, parts, y=6.72):
    tf = tb(s, M, y, W - 2 * M, 0.55)
    p = para(tf, first=True, space_after=0, line=1.25)
    for text, col, mono in parts:
        run(p, text, 10.5, False, col, MONO if mono else BODY)


def panel(s, x, y, w, h, tag=None, tagcol=MUTED, border=None, fill=PANEL):
    rect(s, x, y, w, h, fill=fill, line=border, lw=1.25 if border else 1.0)
    tf = tb(s, x + 0.26, y + 0.22, w - 0.52, h - 0.44)
    if tag:
        p = para(tf, first=True, space_after=8)
        run(p, tag.upper(), 10, True, tagcol, MONO)
        return tf, False
    return tf, True


def callout(s, x, y, w, h, kicker, parts, color=RED, wash=WASH_R):
    rect(s, x, y, w, h, fill=wash, line=None)
    rect(s, x, y, 0.035, h, fill=color, line=None)
    tf = tb(s, x + 0.30, y + 0.20, w - 0.58, h - 0.40, anchor=MSO_ANCHOR.MIDDLE)
    p = para(tf, first=True, space_after=7)
    run(p, kicker.upper(), 10, True, MUTED, MONO)
    p2 = para(tf, space_after=0, line=1.25)
    for text, col, bold, mono in parts:
        run(p2, text, 14, bold, col, MONO if mono else BODY)


def bullets(s, x, y, w, h, items, size=14.5, gap=11):
    """items: list of list-of-(text, color, bold)."""
    tf = tb(s, x, y, w, h)
    for i, segs in enumerate(items):
        p = para(tf, first=(i == 0), space_after=gap, line=1.3)
        run(p, "•   ", size, True, AMBER, BODY)
        for text, col, bold in segs:
            run(p, text, size, bold, col, BODY)
    return tf


def numbered(s, x, y, w, h, items, size=14.5, gap=13):
    tf = tb(s, x, y, w, h)
    for i, segs in enumerate(items):
        p = para(tf, first=(i == 0), space_after=gap, line=1.3)
        run(p, f"{i+1}    ", 12, True, AMBER, MONO)
        for text, col, bold in segs:
            run(p, text, size, bold, col, BODY)
    return tf


def table(s, x, y, w, h, headers, rows, widths, fsize=12):
    gt = s.shapes.add_table(len(rows) + 1, len(headers), In(x), In(y), In(w), In(h)).table
    gt.first_row = False
    for i, cw in enumerate(widths):
        gt.columns[i].width = In(cw)
    for c, htxt in enumerate(headers):
        cell = gt.cell(0, c)
        cell.fill.solid(); cell.fill.fore_color.rgb = WHITE
        cell.margin_left = In(0.06); cell.margin_right = In(0.06)
        cell.margin_top = In(0.05); cell.margin_bottom = In(0.07)
        tf = cell.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]; p.space_after = Pt(0)
        run(p, htxt.upper(), 9.5, True, MUTED, MONO)
    for r, rowdata in enumerate(rows, start=1):
        for c, segs in enumerate(rowdata):
            cell = gt.cell(r, c)
            cell.fill.solid(); cell.fill.fore_color.rgb = WHITE if r % 2 else PANEL
            cell.margin_left = In(0.06); cell.margin_right = In(0.06)
            cell.margin_top = In(0.07); cell.margin_bottom = In(0.07)
            tf = cell.text_frame; tf.word_wrap = True
            p = tf.paragraphs[0]; p.space_after = Pt(0); p.line_spacing = 1.18
            for text, col, bold, mono in segs:
                run(p, text, fsize, bold, col, MONO if mono else BODY)
    return gt


T = lambda t, c=INK2, b=False, m=False: (t, c, b, m)   # table/callout seg
B = lambda t, c=INK2, b=False: (t, c, b)               # bullet seg


# ============================================================ 1. COVER
s = slide()
rect(s, 0, 0, 0.16, H, fill=AMBER, line=None)
tf = tb(s, M + 0.15, 1.45, 9.9, 2.2)
p = para(tf, first=True, space_after=0, line=1.03)
run(p, "Detecting Cloned Voices\non a Phone Call", 46, True, INK, DISP)

rect(s, M + 0.15, 4.05, 0.03, 0.95, fill=AMBER, line=None)
tf = tb(s, M + 0.42, 4.05, 8.6, 0.95)
p = para(tf, first=True, space_after=0, line=1.34)
run(p, "Detectors score ", 16, False, INK2, BODY)
run(p, "1.23%", 16, True, BLUE, MONO)
run(p, " on their own benchmark and ", 16, False, INK2, BODY)
run(p, "37%", 16, True, RED, MONO)
run(p, " on someone else's.\nWe are building one that closes that gap.", 16, False, INK2, BODY)

meta = [("Team", "[names]"), ("Runs on", "The callee's phone, during the call"),
        ("Corpora", "ASVspoof 2019 LA, 2021 LA, In-the-Wild"), ("Date", "September 2026")]
for i, (k, v) in enumerate(meta):
    x = M + 0.15 + i * 3.02
    tf = tb(s, x, 5.70, 2.85, 0.8)
    p = para(tf, first=True, space_after=4)
    run(p, k.upper(), 9.5, True, MUTED, MONO)
    p = para(tf, space_after=0, line=1.2)
    run(p, v, 12, False, INK2, BODY)

tf = tb(s, M + 0.15, 0.55, 8, 0.3)
p = para(tf, first=True, space_after=0)
run(p, "PROPOSAL", 11, True, AMBER, MONO)
run(p, "     |     VISHING CHALLENGE 2026", 11, False, MUTED, MONO)


# ============================================================ 2. THREAT
s = slide()
eyebrow(s, "Act 1", "The threat")
title(s, [("Ninety seconds of public audio is enough.", INK)])

bullets(s, M, 2.35, 6.3, 2.8, [
    [B("An attacker takes a voice from a podcast or a voicemail.")],
    [B("A cloning model copies it. "), B("Minutes of work, no GPU farm.", INK, True)],
    [B("The call reaches a family member, an employee, or a bank.")],
    [B("The victim hears someone they know.")],
], size=16, gap=15)

callout(s, 7.35, 2.35, W - M - 7.35, 2.10,
        "The question this talk answers",
        [T("A human hears a familiar voice and believes it. "),
         T("Can a machine tell that it is synthetic?", RED, True)])

foot(s, [("In a 472-person study, listeners reached 72.8% accuracy where a machine reached 95.5%. "
          "People are the weaker detector.  ", MUTED, False),
         ("arXiv:2107.09667", MUTED, True)])


# ============================================================ 3. STATE OF THE ART
s = slide()
eyebrow(s, "Act 1", "Where the field stands")
title(s, [("Excellent numbers, on ", INK), ("one dataset", BLUE), (".", INK)])

cards = [("Best reported", "1.23%", BLUE, "RawGAT-ST, equal error rate on ASVspoof 2019 LA."),
         ("Benchmark maturity", "4", INK, "ASVspoof challenges since 2015. 54 teams entered the 2021 evaluation."),
         ("Architectures compared", "12", INK, "Re-implemented under one protocol. Raw-waveform models win.")]
cw = (W - 2 * M - 2 * 0.34) / 3
for i, (tag, big, col, body) in enumerate(cards):
    x = M + i * (cw + 0.34)
    tf, _ = panel(s, x, 2.35, cw, 2.10, tag=tag)
    p = para(tf, space_after=10, line=1.0)
    run(p, big, 36, True, col, MONO)
    p = para(tf, space_after=0, line=1.3)
    run(p, body, 13, False, INK2, BODY)

callout(s, M, 4.85, W - 2 * M, 1.45, "The catch",
        [T("Every number here comes from the same corpus the model trained on. Change the dataset and they fall apart. "),
         T("That is the problem we are fixing.", INK, True)])


# ============================================================ 4. THE COLLAPSE
s = slide()
eyebrow(s, "Act 2", "The problem")
title(s, [("Move it off its own dataset and it ", INK), ("stops working", RED), (".", INK)])

BX0, BX1 = 4.55, 12.05
def bx(v): return BX0 + (BX1 - BX0) * v / 60.0
BH = 0.32

# useless zone behind the bars
rect(s, bx(50), 2.30, BX1 - bx(50), 1.72, fill=WASH_R, line=None)
tf = tb(s, bx(50), 2.04, BX1 - bx(50), 0.24, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0)
run(p, "COIN FLIP", 9.5, True, RED, MONO)

tf = tb(s, M, 2.04, 3.6, 0.26)
p = para(tf, first=True, space_after=0)
run(p, "TRAINED ON ASVSPOOF 2019, THEN TESTED ON:", 9.5, True, MUTED, MONO)

bars = [("its own test set", "", 1.23, BLUE, 2.42),
        ("another corpus", "In-the-Wild, new speakers", 37.15, RED, 2.98),
        ("2026 cloned voices", "over a real VoIP call", 50.28, RED, 3.54)]
for label, sub, val, col, y in bars:
    tf = tb(s, M, y + 0.01, 3.6, 0.5)
    p = para(tf, first=True, space_after=1)
    run(p, label, 14, True, INK, BODY)
    if sub:
        p = para(tf, space_after=0)
        run(p, sub, 9.5, False, MUTED, MONO)
    rect(s, BX0, y, max(bx(val) - BX0, 0.03), BH, fill=col, line=None)
    if val >= 45:
        tf = tb(s, bx(val) - 1.25, y + 0.03, 1.1, 0.3, align=PP_ALIGN.RIGHT)
        p = para(tf, first=True, space_after=0)
        run(p, f"{val}%", 17, True, WHITE, MONO)
    else:
        tf = tb(s, bx(val) + 0.16, y + 0.02, 1.4, 0.3)
        p = para(tf, first=True, space_after=0)
        run(p, f"{val}%", 17, True, col, MONO)

# the fix, set apart
line(s, M, 4.22, BX1, 4.22, color=RULE, lw=1.0)
tf = tb(s, M, 4.34, 3.6, 0.5)
p = para(tf, first=True, space_after=1)
run(p, "same test, retrained", 14, True, BLUE, BODY)
p = para(tf, space_after=0)
run(p, "on modern voices", 9.5, False, MUTED, MONO)
rect(s, BX0, 4.33, bx(5.81) - BX0, BH, fill=BLUE, line=None)
tf = tb(s, bx(5.81) + 0.16, 4.35, 2.6, 0.3)
p = para(tf, first=True, space_after=0)
run(p, "5.81%", 17, True, BLUE, MONO)
run(p, "    the problem is fixable", 12, False, MUTED, BODY)

line(s, BX0, 4.80, BX1, 4.80, color=RULE, lw=1.0)
for tick in (0, 15, 30, 45, 60):
    tf = tb(s, bx(tick) - 0.4, 4.86, 0.8, 0.24, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0)
    run(p, f"{tick}%", 10, False, MUTED, MONO)
tf = tb(s, M, 4.86, 3.6, 0.24)
p = para(tf, first=True, space_after=0)
run(p, "equal error rate, lower is better", 9.5, False, MUTED, MONO)

callout(s, M, 5.42, W - 2 * M, 1.12, "The gap is the target",
        [T("A detector at 1% and 37% has a 36-point gap. "),
         T("Closing that gap is the job.", INK, True),
         T(" More ASVspoof data will not do it: 33.9% to 33.1%, because every split comes from the same recordings.")],
        color=BLUE, wash=WASH_B)


# ============================================================ 5. DIAGNOSIS
s = slide()
eyebrow(s, "Act 2", "Why it collapses")
title(s, [("The detector learns the ", INK), ("dataset", RED), (", not the voice.", INK)])

cards = [("Silence alone", "85%", "Accuracy from a classifier given ", "only the length of the opening silence",
          ".", "Müller et al."),
         ("Attack on silence only", "82.2%", "Attack success from changing ", "only the background noise and the silence",
          ", never the voice.", "SiFDetectCracker, ACM MM 2023"),
         ("Where it looks", "0.5–0.6 kHz", "SHAP analysis: the model attends to ", "the gaps between words",
          " and one narrow low band.", "arXiv:2110.03309")]
for i, (tag, big, a, bld, c, cite) in enumerate(cards):
    x = M + i * (cw + 0.34)
    tf, _ = panel(s, x, 2.35, cw, 2.30, tag=tag)
    p = para(tf, space_after=9, line=1.0)
    run(p, big, 30, True, RED, MONO)
    p = para(tf, space_after=6, line=1.3)
    run(p, a, 13, False, INK2, BODY); run(p, bld, 13, True, INK, BODY); run(p, c, 13, False, INK2, BODY)
    p = para(tf, space_after=0)
    run(p, cite, 9.5, False, MUTED, MONO)

callout(s, M, 5.05, W - 2 * M, 1.35, "Which tells us what to fix",
        [T("The model wins on things that belong to the corpus, not to the speech. "),
         T("All of them can be taken away during training.", INK, True)],
        color=BLUE, wash=WASH_B)


# ============================================================ 6. CHANNEL
s = slide()
eyebrow(s, "Act 2", "The second shift")
title(s, [("What survives a phone line?", INK)])

AX0, AX1 = 3.30, 12.30
def fx(hz):
    import math
    lo, hi = math.log10(50), math.log10(20000)
    return AX0 + (AX1 - AX0) * (math.log10(hz) - lo) / (hi - lo)

rect(s, fx(80), 2.15, fx(300) - fx(80), 1.62, fill=WASH_B, line=None)
rect(s, fx(4000), 2.15, AX1 - fx(4000), 1.62, fill=WASH_R, line=None)
tf = tb(s, (fx(80) + fx(300)) / 2 - 0.95, 1.90, 1.9, 0.22, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0); run(p, "PITCH", 9.5, True, BLUE, MONO)
tf = tb(s, (fx(4000) + AX1) / 2 - 1.3, 1.90, 2.6, 0.22, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0); run(p, "SYNTHESIS ARTIFACT", 9.5, True, RED, MONO)

bands = [("Opus / WhatsApp", 50, 20000, BLUE, 2.32),
         ("AMR-WB / VoLTE", 50, 7000, BLUE, 2.85),
         ("G.711 / GSM", 300, 3400, RED, 3.38)]
for name, lo, hi, col, y in bands:
    tf = tb(s, M, y + 0.02, 2.5, 0.3)
    p = para(tf, first=True, space_after=0); run(p, name, 13, True, INK, BODY)
    rect(s, fx(lo), y, fx(hi) - fx(lo), 0.22, fill=col, line=None)

line(s, AX0, 3.80, AX1, 3.80, color=RULE, lw=1.0)
for hz, lbl in [(50, "50"), (300, "300"), (3400, "3.4k"), (7000, "7k"), (20000, "20k Hz")]:
    tf = tb(s, fx(hz) - 0.45, 3.86, 0.9, 0.24, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0); run(p, lbl, 10, False, MUTED, MONO)

callout(s, M, 4.55, W - 2 * M, 1.55, "Good news for the design",
        [T("A phone line throws away the top of the spectrum, where the synthesis artifact lives. "
           "But low-passing to the telephone band "),
         T("improves", BLUE, True),
         T(" codec robustness by about 25% relative, because the high bins are what overfit. And the "),
         T("pitch band alone reaches 1.15% EER", BLUE, True),
         T(". The band the phone keeps is a band we can build on.")],
        color=BLUE, wash=WASH_B)


# ============================================================ 7. HOW WE BUILD IT
s = slide()
eyebrow(s, "Act 3", "Our approach")
title(s, [("How you build a detector that ", INK), ("travels", BLUE), (".", INK)])

table(s, M, 2.30, W - 2 * M, 3.4,
      ["Design decision", "Why"],
      [[[T("Codec and channel augmentation", INK, True)],
        [T("Every top-5 system in ASVspoof 2021 used it. No counterexample.")]],
       [[T("Raw waveform or CQT, never mel", INK, True)],
        [T("Mel is 37% worse on average, all else equal. It throws away the resolution the task needs.")]],
       [[T("Silence masking, VAD-trimmed training", INK, True)],
        [T("Takes away the cue that carries 85% of the decision.")]],
       [[T("Low-pass to the telephone band", INK, True)],
        [T("Costs high frequencies, buys 25% relative EER under codec shift. We test it, not assume it.")]],
       [[T("SSL front-end (wav2vec2)", INK, True)],
        [T("The most robust under attack: 1.89% to 11.6%, where SSNET goes to 61.81%. Also the heaviest.")]],
       [[T("One-class objective", INK, True)],
        [T("Learns what real speech is, instead of which attacks we happened to see.")]]],
      widths=[4.0, 7.89], fsize=12.5)

foot(s, [("None of these is new on its own. The work is making them hold against both shifts at once, "
          "corpus and channel.", MUTED, False)])


# ============================================================ 8. HOW WE PROVE IT
s = slide()
eyebrow(s, "Act 3", "How we measure it")
title(s, [("The only number that matters is the ", INK), ("gap", BLUE), (".", INK)])

hw = (W - 2 * M - 0.34) / 2
tf, _ = panel(s, M, 2.35, hw, 2.35, tag="Train")
p = para(tf, space_after=10, line=1.3)
run(p, "ASVspoof 2019 LA", 13.5, True, INK, BODY)
run(p, ", clean, with our augmentation on top. 25,380 utterances.", 13.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "We hold out one attack family, so unseen attacks are measured before we touch another corpus.", 13.5, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.35, hw, 2.35, tag="Test")
p = para(tf, space_after=10, line=1.3)
run(p, "ASVspoof 2021 LA ", 13.5, True, INK, BODY)
run(p, "for the channel. Real VoIP and PSTN, seven codecs, ", 13.5, False, INK2, BODY)
run(p, "25,938", 13.5, True, INK, MONO)
run(p, " trials each.", 13.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "In-the-Wild ", 13.5, True, INK, BODY)
run(p, "for the corpus. New speakers, new attacks, new recordings. 31,779 clips.", 13.5, False, INK2, BODY)

callout(s, M, 4.95, W - 2 * M, 1.42, "Our headline metric",
        [T("gap  =  out-of-domain EER  −  in-domain EER", INK, True, True),
         T("\nA detector at 1% and 37% has a 36-point gap. We report all three, per codec and per corpus, "
           "never averaged together. The gap is what we optimise.")],
        color=BLUE, wash=WASH_B)


# ============================================================ 9. DEPLOYMENT
s = slide()
eyebrow(s, "Act 4", "Where it runs")
title(s, [("An app on the callee's phone.", INK)])

tf, _ = panel(s, M, 2.35, hw, 2.30, tag="What the setting gives us")
p = para(tf, space_after=10, line=1.3)
run(p, "A workable budget. ", 13.5, True, INK, BODY)
run(p, "A person reads the alarm and needs seconds to react, not 200 milliseconds.", 13.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "False alarms cost more than misses. ", 13.5, True, INK, BODY)
run(p, "An app that cries wolf gets deleted. That sets where we sit on the curve.", 13.5, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.35, hw, 2.30, tag="What we must not hide", tagcol=RED, border=RED)
p = para(tf, space_after=10, line=1.3)
run(p, "Android will not hand call audio to a third-party app. ", 13.5, True, INK, BODY)
run(p, "VOICE_CALL has needed privileged access since Android 10. iOS is closed.", 13.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "So we capture through the speaker and the microphone. That adds a room to the signal: ", 13.5, False, INK2, BODY)
run(p, "4.7% to 18.2%", 13.5, True, RED, MONO)
run(p, " EER under replay.", 13.5, False, INK2, BODY)

callout(s, M, 4.90, W - 2 * M, 1.42, "So we train against it too",
        [T("Re-capture is a third shift, next to corpus and channel, and it is the one a real deployment forces on us. "),
         T("It goes in the augmentation stack, not the limitations section.", BLUE, True)],
        color=BLUE, wash=WASH_B)


# ============================================================ 10. REAL-TIME
s = slide()
eyebrow(s, "Act 4", "Deciding during the call")
title(s, [("One window is not a decision.", INK)])

callout(s, M, 2.30, W - 2 * M, 1.15, "The trap",
        [T("Alarm whenever one window crosses a threshold, at 5% per window and 2-second windows, and a "),
         T("60-second call false-alarms 79% of the time", RED, True),
         T(". Per-window error is the wrong number to report.")])

tf, _ = panel(s, M, 3.72, hw, 2.45, tag="How we decide", tagcol=AMBER, border=AMBER)
p = para(tf, space_after=9, line=1.15)
run(p, "Add the evidence up", 17, True, INK, DISP)
p = para(tf, space_after=9, line=1.3)
run(p, "Accumulate a likelihood ratio across windows and alarm when it crosses a boundary. Wald's sequential "
       "test, with separate raise and clear thresholds and a three-second floor.", 12.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "The decision arrives as soon as the evidence is enough, which is what real-time means here.", 12.5, True, INK, BODY)

tf, _ = panel(s, M + hw + 0.34, 3.72, hw, 2.45, tag="What we report")
p = para(tf, space_after=9, line=1.15)
run(p, "Three numbers, always together", 17, True, INK, DISP)
p = para(tf, space_after=7, line=1.3)
run(p, "False alarms per call-minute", 12.5, True, INK, BODY)
run(p, ", which is the unit that exposes the trap above.", 12.5, False, INK2, BODY)
p = para(tf, space_after=7, line=1.3)
run(p, "Detection rate", 12.5, True, INK, BODY)
run(p, " at that operating point.", 12.5, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "Time to detection", 12.5, True, INK, BODY)
run(p, ", and milliseconds per window on the phone.", 12.5, False, INK2, BODY)


# ============================================================ 11. PIPELINE
s = slide()
eyebrow(s, "Act 4", "The system")
title(s, [("What we will build.", INK)])

nodes = [("Train", "ASVspoof 2019 LA, clean", False),
         ("Ours", "Augmentation: codec, silence, noise, room, re-capture", True),
         ("Front-end", "Raw waveform or CQT", False),
         ("Detector", "RawNet2, then AASIST, SSL, one-class", True),
         ("Decision", "Evidence accumulated over windows", True),
         ("Output", "A risk score, not a verdict", False)]
nw, gap = 1.80, 0.20
total = len(nodes) * nw + (len(nodes) - 1) * gap
x = (W - total) / 2
for i, (tag, body, ours) in enumerate(nodes):
    nx = x + i * (nw + gap)
    rect(s, nx, 2.35, nw, 1.45, fill=WHITE if ours else PANEL,
         line=AMBER if ours else RGBColor(0xE2, 0xE6, 0xEB), lw=1.5 if ours else 1.0)
    tf = tb(s, nx + 0.16, 2.51, nw - 0.32, 1.15)
    p = para(tf, first=True, space_after=6)
    run(p, tag.upper(), 9, True, AMBER if ours else MUTED, MONO)
    p = para(tf, space_after=0, line=1.24)
    run(p, body, 11, False, INK, BODY)
    if i < len(nodes) - 1:
        tf = tb(s, nx + nw, 2.93, gap, 0.3, align=PP_ALIGN.CENTER)
        p = para(tf, first=True, space_after=0)
        run(p, "→", 13, False, RULE, BODY)

tf, _ = panel(s, M, 4.15, hw, 1.95, tag="What we sweep")
p = para(tf, space_after=9, line=1.3)
run(p, "Bandwidth: ", 13, True, INK, BODY)
run(p, "clean 16k, G.722, Opus, a-law, μ-law, GSM, and ", 13, False, INK2, BODY)
run(p, "AMR", 13, True, INK, BODY)
run(p, ", which no ASVspoof edition covers and which is what mobile calls actually use.", 13, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "Window length: ", 13, True, INK, BODY)
run(p, "full, 4 s, 2 s, 1 s. Accuracy against latency.", 13, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 4.15, hw, 1.95, tag="Never in training")
p = para(tf, space_after=9, line=1.3)
run(p, "In-the-Wild, the held-out attack family, and a small probe of modern cloned voices built from our "
       "own consented recordings.", 13, False, INK2, BODY)
p = para(tf, space_after=0, line=1.3)
run(p, "Reported per generator, never pooled.", 13, True, INK, BODY)

foot(s, [("Every codec is already in the ffmpeg build on our machine, and 2021 LA ships the codec label per "
          "trial. The sweep costs us no setup.", MUTED, False)])


# ============================================================ 12. SUCCESS
s = slide()
eyebrow(s, "Act 4", "Conclusion")
title(s, [("What success looks like.", INK)])

tf, _ = panel(s, M, 2.35, hw, 2.45, tag="The target", tagcol=BLUE, border=BLUE)
goals = [("An ", "out-of-domain EER well below the 34 to 37%", " the literature reports on the same held-out data."),
         ("A gap we ", "reduced and can attribute", ". Which decision bought how much."),
         ("A decision ", "within seconds of speech", ", on the phone, with the cost of every window length measured.")]
for a, b, c in goals:
    p = para(tf, space_after=11, line=1.3)
    run(p, a, 13.5, False, INK2, BODY); run(p, b, 13.5, True, INK, BODY); run(p, c, 13.5, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.35, hw, 2.45, tag="What we will not do")
for t in ["Quote one in-domain number as if it described the field.",
          "Average across corpora or codecs to make a result look better.",
          "Say the problem is solved. A smaller gap is not a closed gap."]:
    p = para(tf, space_after=11, line=1.3)
    run(p, t, 13.5, False, INK2, BODY)

callout(s, M, 5.05, W - 2 * M, 1.35, "The position we will defend",
        [T("A detector that travels is worth more than a detector that scores well. "),
         T("We are optimising the number that survives a change of dataset.", BLUE, True)],
        color=BLUE, wash=WASH_B)


import sys
out = sys.argv[1] if len(sys.argv) > 1 else "proposal.pptx"
prs.save(out)
print("saved", out, "12 slides")
