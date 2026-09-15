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



def notes(s, text):
    """Speaker notes. Presenter sees these, the audience does not."""
    tf = s.notes_slide.notes_text_frame
    tf.text = text.strip()
    for par in tf.paragraphs:
        for r in par.runs:
            r.font.size = Pt(12)
    return tf


T = lambda t, c=INK2, b=False, m=False: (t, c, b, m)   # table/callout seg
B = lambda t, c=INK2, b=False: (t, c, b)               # bullet seg


# ============================================================ 1. COVER
s = slide()
rect(s, 0, 0, 0.16, H, fill=AMBER, line=None)
tf = tb(s, M + 0.15, 1.55, 10.2, 2.2)
p = para(tf, first=True, space_after=0, line=1.03)
run(p, "Detecting Cloned Voices\nGon a Phone Call".replace("\nG","\n"), 50, True, INK, DISP)

rect(s, M + 0.15, 4.25, 0.03, 0.95, fill=AMBER, line=None)
tf = tb(s, M + 0.42, 4.25, 9.4, 0.95)
p = para(tf, first=True, space_after=0, line=1.34)
run(p, "1.23%", 19, True, BLUE, MONO)
run(p, " on their own benchmark.   ", 19, False, INK2, BODY)
run(p, "37%", 19, True, RED, MONO)
run(p, " on someone else's.\nWe are building one that closes that gap.", 19, False, INK2, BODY)

tf = tb(s, M + 0.15, 6.10, 10, 0.4)
p = para(tf, first=True, space_after=0)
run(p, "[names]          September 2026", 12, False, MUTED, BODY)

tf = tb(s, M + 0.15, 0.55, 8, 0.3)
p = para(tf, first=True, space_after=0)
run(p, "PROPOSAL", 11, True, AMBER, MONO)
run(p, "     |     VISHING CHALLENGE 2026", 11, False, MUTED, MONO)

notes(s, """
Open with the framing. Do not read the slide.

"Voice cloning is now good enough that a stranger can phone you in your daughter's voice. The
detection research looks solved on paper. It is not. A published detector scores 1.23% error on
its own benchmark and 37% on a different dataset, same model, same weights. We are building one
that closes that gap, and we will prove it with cross-corpus evaluation rather than a single
headline number."

Deployment: an app on the callee's phone, listening during the call.
Corpora: ASVspoof 2019 LA to train, 2021 LA for the channel, In-the-Wild for the corpus shift.
""")


# ============================================================ 2. THREAT
s = slide()
eyebrow(s, "Act 1", "The threat")
title(s, [("Ninety seconds of audio is enough.", INK)])

bullets(s, M, 2.60, 6.6, 2.6, [
    [B("A voice from a podcast or a voicemail.")],
    [B("Cloned in minutes.", INK, True), B(" No GPU farm, no expertise.")],
    [B("A call to a parent, an employee, or a bank.")],
], size=20, gap=22)

callout(s, 7.85, 2.60, W - M - 7.85, 1.90,
        "The question",
        [T("Can a machine tell that it is synthetic?", RED, True)])

notes(s, """
Tell it as a story. Thirty seconds, no statistics. Pick one example and stay in it.

"You get a call. It is your mother's voice and she is upset. Ninety seconds of her speaking in
public is all the attacker needed. A zero-shot cloning model does the rest in minutes, on a
laptop, with no expertise."

Then the pivot: people cannot catch this. In a 472-person study listeners reached 72.8% accuracy
on ASVspoof attacks where a machine reached 95.5%. arXiv:2107.09667. The human is the weaker
detector, which is the whole justification for building the machine one.
""")


# ============================================================ 3. STATE OF THE ART
s = slide()
eyebrow(s, "Act 1", "Where the field stands")
title(s, [("Excellent numbers, on ", INK), ("one dataset", BLUE), (".", INK)])

cards = [("Best reported", "1.23%", BLUE, "RawGAT-ST on ASVspoof 2019 LA"),
         ("Challenges run", "4", INK, "ASVspoof, biennial since 2015"),
         ("Architectures compared", "12", INK, "One protocol, raw waveform wins")]
cw = (W - 2 * M - 2 * 0.34) / 3
for i, (tag, big, col, body) in enumerate(cards):
    x = M + i * (cw + 0.34)
    tf, _ = panel(s, x, 2.50, cw, 1.95, tag=tag)
    p = para(tf, space_after=12, line=1.0)
    run(p, big, 44, True, col, MONO)
    p = para(tf, space_after=0, line=1.3)
    run(p, body, 14, False, INK2, BODY)

callout(s, M, 4.95, W - 2 * M, 1.30, "The catch",
        [T("Every number here is measured on the corpus the model trained on.", INK, True)])

notes(s, """
Deliver this with confidence, as if you believe it. The reversal on the next slide lands harder
if you sell this one first.

Numbers: RawGAT-ST 1.23% EER, AASIST 0.71%. Four ASVspoof challenges since 2015, 54 teams in the
2021 evaluation alone. Mueller et al. re-implemented twelve architectures under one protocol and
raw-waveform models won consistently.

Then the catch, slowly. Every one of those numbers is in-domain: train on ASVspoof, test on
ASVspoof. Nobody is hiding it, that is just how the benchmark is built. What happens when you
move off it is the next slide, and it is the reason this project exists.
""")


# ============================================================ 4. THE COLLAPSE
s = slide()
eyebrow(s, "Act 2", "The problem")
title(s, [("Move it off its own dataset and it ", INK), ("stops working", RED), (".", INK)])

BX0, BX1 = 4.55, 12.05
def bx(v): return BX0 + (BX1 - BX0) * v / 60.0
BH = 0.36

rect(s, bx(50), 2.35, BX1 - bx(50), 1.90, fill=WASH_R, line=None)
tf = tb(s, bx(50), 2.08, BX1 - bx(50), 0.24, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0)
run(p, "COIN FLIP", 10, True, RED, MONO)

tf = tb(s, M, 2.08, 3.8, 0.26)
p = para(tf, first=True, space_after=0)
run(p, "TRAINED ON ASVSPOOF 2019, TESTED ON:", 10, True, MUTED, MONO)

bars = [("its own test set", "", 1.23, BLUE, 2.46),
        ("another corpus", "In-the-Wild", 37.15, RED, 3.06),
        ("2026 cloned voices", "over a real VoIP call", 50.28, RED, 3.66)]
for label, sub, val, col, y in bars:
    tf = tb(s, M, y + 0.01, 3.7, 0.5)
    p = para(tf, first=True, space_after=1)
    run(p, label, 15, True, INK, BODY)
    if sub:
        p = para(tf, space_after=0)
        run(p, sub, 10, False, MUTED, MONO)
    rect(s, BX0, y, max(bx(val) - BX0, 0.03), BH, fill=col, line=None)
    if val >= 45:
        tf = tb(s, bx(val) - 1.30, y + 0.04, 1.15, 0.3, align=PP_ALIGN.RIGHT)
        p = para(tf, first=True, space_after=0)
        run(p, "{}%".format(val), 18, True, WHITE, MONO)
    else:
        tf = tb(s, bx(val) + 0.16, y + 0.03, 1.4, 0.3)
        p = para(tf, first=True, space_after=0)
        run(p, "{}%".format(val), 18, True, col, MONO)

line(s, M, 4.38, BX1, 4.38, color=RULE, lw=1.0)
tf = tb(s, M, 4.52, 3.7, 0.5)
p = para(tf, first=True, space_after=1)
run(p, "same test, retrained", 15, True, BLUE, BODY)
p = para(tf, space_after=0)
run(p, "on modern voices", 10, False, MUTED, MONO)
rect(s, BX0, 4.51, bx(5.81) - BX0, BH, fill=BLUE, line=None)
tf = tb(s, bx(5.81) + 0.16, 4.54, 3.4, 0.3)
p = para(tf, first=True, space_after=0)
run(p, "5.81%", 18, True, BLUE, MONO)
run(p, "    so it can be fixed", 14, False, MUTED, BODY)

line(s, BX0, 5.04, BX1, 5.04, color=RULE, lw=1.0)
for tick in (0, 15, 30, 45, 60):
    tf = tb(s, bx(tick) - 0.4, 5.10, 0.8, 0.24, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0)
    run(p, "{}%".format(tick), 10, False, MUTED, MONO)
tf = tb(s, M, 5.10, 3.7, 0.24)
p = para(tf, first=True, space_after=0)
run(p, "equal error rate, lower is better", 10, False, MUTED, MONO)

callout(s, M, 5.62, W - 2 * M, 0.95, "",
        [T("A 36-point gap. ", INK, True), T("Closing it is the job.", BLUE, True)],
        color=BLUE, wash=WASH_B)

notes(s, """
This is the slide the talk turns on. Take three minutes. Walk the bars top to bottom.

Bar 1: RawGAT-ST, 1.23% EER on ASVspoof 2019 LA eval. The published number.
Bar 2: the SAME model, same weights, nothing retrained, tested on In-the-Wild, a corpus of found
celebrity audio. 37.15%. Say "same weights" out loud, that is the point.
Bar 3: an ASVspoof-trained detector against 2026 cloned voices over a real VoIP call. 50.28%,
a coin flip. Source is RTCFake, a recent preprint. Say "a recent preprint reports". Do not
present it as settled.

Then the blue bar: train the same architecture on modern voices instead and it drops to 5.81%.
So this is not a law of nature, it is a training problem. That is why the project is worth doing.

If asked about more data: measured, does not help, 33.9% to 33.1%. Every ASVspoof split derives
from the same VCTK recordings, so more of it adds no new domain.

EER means equal error rate. 50% is random guessing.
""")


# ============================================================ 5. DIAGNOSIS
s = slide()
eyebrow(s, "Act 2", "Why it collapses")
title(s, [("It learns the ", INK), ("dataset", RED), (", not the voice.", INK)])

cards = [("Silence alone", "85%", "accuracy from the length of the opening silence"),
         ("Attack on silence only", "82.2%", "success without ever touching the voice"),
         ("Where it looks", "0.5-0.6 kHz", "the gaps between words, one narrow band")]
for i, (tag, big, body) in enumerate(cards):
    x = M + i * (cw + 0.34)
    tf, _ = panel(s, x, 2.50, cw, 2.05, tag=tag)
    p = para(tf, space_after=12, line=1.0)
    run(p, big, 38, True, RED, MONO)
    p = para(tf, space_after=0, line=1.32)
    run(p, body, 14, False, INK2, BODY)

callout(s, M, 5.05, W - 2 * M, 1.25, "Which tells us what to fix",
        [T("It wins on what belongs to the corpus, not the speech. "),
         T("All of it can be taken away in training.", INK, True)],
        color=BLUE, wash=WASH_B)

notes(s, """
Three findings, one conclusion. Do not read the cards, explain each in a sentence.

1. Mueller et al. trained a classifier on nothing but the DURATION of the silence at the start of
   the clip. 85% accuracy, 15.1% EER. In ASVspoof, real recordings have longer leading silence
   than fake ones, so silence length leaks the label.
2. SiFDetectCracker, ACM MM 2023. A black-box attack that changes only the background noise and
   the mute segments and never touches the speech. 82.2% success against RawNet2, RawGAT-ST and
   others.
3. SHAP analysis, arXiv:2110.03309. The classifier attends to non-speech intervals and one narrow
   band around 0.5 to 0.6 kHz.

Conclusion, say it out loud: the model is winning on properties of the corpus, not properties of
the voice. That is exactly why it does not travel. And it is good news, because every one of
those cues can be removed during training. Slide 7 is how.

If asked: yes, a chunk of published performance is a dataset artifact, an attacker can strip the
silence trivially, and a live phone call has no clean studio silence anyway.
""")


# ============================================================ 6. CHANNEL
s = slide()
eyebrow(s, "Act 2", "The second shift")
title(s, [("What survives a phone line?", INK)])

AX0, AX1 = 3.30, 12.30
def fx(hz):
    import math
    lo, hi = math.log10(50), math.log10(20000)
    return AX0 + (AX1 - AX0) * (math.log10(hz) - lo) / (hi - lo)

rect(s, fx(80), 2.45, fx(300) - fx(80), 1.80, fill=WASH_B, line=None)
rect(s, fx(4000), 2.45, AX1 - fx(4000), 1.80, fill=WASH_R, line=None)
tf = tb(s, (fx(80) + fx(300)) / 2 - 0.95, 2.18, 1.9, 0.24, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0); run(p, "PITCH", 10, True, BLUE, MONO)
tf = tb(s, (fx(4000) + AX1) / 2 - 1.3, 2.18, 2.6, 0.24, align=PP_ALIGN.CENTER)
p = para(tf, first=True, space_after=0); run(p, "SYNTHESIS ARTIFACT", 10, True, RED, MONO)

bands = [("Opus / WhatsApp", 50, 20000, BLUE, 2.62),
         ("AMR-WB / VoLTE", 50, 7000, BLUE, 3.20),
         ("G.711 / GSM", 300, 3400, RED, 3.78)]
for name, lo, hi, col, y in bands:
    tf = tb(s, M, y + 0.01, 2.5, 0.3)
    p = para(tf, first=True, space_after=0); run(p, name, 15, True, INK, BODY)
    rect(s, fx(lo), y, fx(hi) - fx(lo), 0.26, fill=col, line=None)

line(s, AX0, 4.28, AX1, 4.28, color=RULE, lw=1.0)
for hz, lbl in [(50, "50"), (300, "300"), (3400, "3.4k"), (7000, "7k"), (20000, "20k Hz")]:
    tf = tb(s, fx(hz) - 0.45, 4.34, 0.9, 0.24, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0); run(p, lbl, 10, False, MUTED, MONO)

callout(s, M, 4.95, W - 2 * M, 1.35, "Good news",
        [T("The phone keeps the pitch band. "),
         T("The pitch band alone reaches 1.15% EER.", BLUE, True)],
        color=BLUE, wash=WASH_B)

notes(s, """
Point at the bars as you talk. The picture does the work.

The synthesis artifact lives at the top of the spectrum, above roughly 4 kHz. A WhatsApp or Teams
call over Opus keeps all of it. A VoLTE call over AMR-WB keeps most. A normal phone call through
G.711 or GSM keeps only 300 to 3400 Hz, so the artifact is not damaged, it is gone.

That sounds fatal. We assumed it was. It is not, for two reasons:

1. Shim and Wang, arXiv:2211.06546. Deliberately low-passing to the telephone band IMPROVES codec
   robustness by about 25% relative, because the high-frequency bins are the ones that overfit to
   the clean training condition.
2. The F0 sub-band of the log-power spectrogram ALONE reaches 1.15% EER on ASVspoof 2019 LA.
   arXiv:2208.01214.

So the band the phone keeps is a band we can build on. That is a design decision, not a
consolation prize.

Caveat if pressed: this also means prosody is the load-bearing feature in narrowband, and prosody
is manipulable by an attacker. We know. It is in the report's limitations.
""")


# ============================================================ 7. HOW WE BUILD IT
s = slide()
eyebrow(s, "Act 3", "Our approach")
title(s, [("How you build a detector that ", INK), ("travels", BLUE), (".", INK)])

table(s, M, 2.50, W - 2 * M, 3.1,
      ["Design decision", "Evidence"],
      [[[T("Codec and channel augmentation", INK, True)],
        [T("every top-5 system in 2021 used it", INK2, False, True)]],
       [[T("Raw waveform or CQT, never mel", INK, True)],
        [T("mel is 37% worse", INK2, False, True)]],
       [[T("Silence masking, VAD-trimmed training", INK, True)],
        [T("removes the cue worth 85%", INK2, False, True)]],
       [[T("Low-pass to the telephone band", INK, True)],
        [T("25% better under codec shift", INK2, False, True)]],
       [[T("SSL front-end (wav2vec2)", INK, True)],
        [T("1.89% to 11.6% under attack, but heavy", INK2, False, True)]],
       [[T("One-class objective", INK, True)],
        [T("learns real speech, not known attacks", INK2, False, True)]]],
      widths=[6.0, 5.89], fsize=14)

foot(s, [("None of these is new on its own. The work is making them hold against both shifts at once.", MUTED, False)])

notes(s, """
The "what are you actually going to do" slide. One sentence per row.

1. Codec and channel augmentation. Every top-5 system in ASVspoof 2021 used data augmentation and
   every top-5 deepfake-track system used codec augmentation specifically. No counterexample in
   the literature. The least controversial thing we will do.
2. Front-end. Swapping mel for CQT improves average EER by 37% with everything else held constant.
   Mel compresses high-frequency resolution because it models human hearing, and the artifact is
   not where human hearing is sensitive.
3. Silence masking and VAD-trimmed training. Directly removes the shortcut from slide 5. Proposed
   as mitigation by Zhang et al., TASLP 2023. As far as we found, nobody has combined it with
   channel robustness, which is what we will do.
4. Telephone-band low-pass, from the previous slide. We test it as a condition, we do not assume it.
5. wav2vec2 / SSL front-end. The most robust model under the Kassis attack by a wide margin,
   1.89% to 11.6%, where SSNET goes to 61.81%. Also the heaviest, and the phone has to run it, so
   we measure what it costs in latency.
6. One-class objective. Model what bona fide speech is, instead of memorising which attacks we
   happened to see. The standard answer to unseen-attack generalisation.

Be honest in the closing line: none of these is novel alone. The contribution is combining them
against corpus shift and channel shift at the same time, and measuring the result properly.
""")


# ============================================================ 8. HOW WE PROVE IT
s = slide()
eyebrow(s, "Act 3", "How we measure it")
title(s, [("The only number that matters is the ", INK), ("gap", BLUE), (".", INK)])

hw = (W - 2 * M - 0.34) / 2
tf, _ = panel(s, M, 2.50, hw, 2.05, tag="Train")
p = para(tf, space_after=12, line=1.32)
run(p, "ASVspoof 2019 LA, clean.", 16, True, INK, BODY)
p = para(tf, space_after=0, line=1.32)
run(p, "One attack family held out.", 16, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.50, hw, 2.05, tag="Test")
p = para(tf, space_after=12, line=1.32)
run(p, "ASVspoof 2021 LA", 16, True, INK, BODY)
run(p, "   for the channel", 16, False, INK2, BODY)
p = para(tf, space_after=0, line=1.32)
run(p, "In-the-Wild", 16, True, INK, BODY)
run(p, "   for the corpus", 16, False, INK2, BODY)

callout(s, M, 4.90, W - 2 * M, 1.40, "Our headline metric",
        [T("gap  =  out-of-domain EER  -  in-domain EER", INK, True, True),
         T("\nReported per codec and per corpus. Never averaged together.")],
        color=BLUE, wash=WASH_B)

notes(s, """
Short slide, but it is the one that protects you in questions. If someone asks "what EER are you
targeting", this is the answer.

Train: ASVspoof 2019 LA, clean, 25,380 utterances, with our augmentation stack on top. We hold out
one attack family so unseen-attack performance is measured before we ever touch another corpus.

Test, and each isolates a different shift:
- ASVspoof 2021 LA isolates the CHANNEL. Real VoIP and PSTN transmission, seven codec conditions,
  25,938 trials each, perfectly balanced, and the codec is labelled per trial so we do not have to
  simulate anything.
- In-the-Wild isolates the CORPUS. New speakers, new attacks, different recording provenance,
  31,779 clips. The hardest published case.

The metric: gap equals out-of-domain EER minus in-domain EER. A detector at 1% and 37% has a
36-point gap. We report in-domain, out-of-domain and the gap, per condition, never pooled, and we
optimise the gap rather than the headline number.

Why never pooled: averaging hides exactly the effect we are trying to reduce.
""")


# ============================================================ 9. DEPLOYMENT
s = slide()
eyebrow(s, "Act 4", "Where it runs")
title(s, [("An app on the callee's phone.", INK)])

tf, _ = panel(s, M, 2.50, hw, 2.10, tag="What the setting gives us")
p = para(tf, space_after=13, line=1.32)
run(p, "Seconds, not milliseconds.", 16, True, INK, BODY)
p = para(tf, space_after=0, line=1.32)
run(p, "False alarms cost more than misses.", 16, True, INK, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.50, hw, 2.10, tag="What we must not hide", tagcol=RED, border=RED)
p = para(tf, space_after=13, line=1.32)
run(p, "Android will not give us the call audio.", 16, True, INK, BODY)
p = para(tf, space_after=0, line=1.32)
run(p, "So we capture through the room: ", 16, False, INK2, BODY)
run(p, "4.7% to 18.2%", 16, True, RED, MONO)

callout(s, M, 4.95, W - 2 * M, 1.30, "So we train against it too",
        [T("Re-capture is a third shift, and it is the one a real deployment forces on us.")],
        color=BLUE, wash=WASH_B)

notes(s, """
Say the good part briefly, then spend the time on the honest part. Volunteering the weakness here
buys real credit with a panel.

The good part. A human reads the alarm and needs seconds to react, so our latency budget is
seconds, not the 200 ms an authentication gate would need. And the cost asymmetry is clear: an app
that cries wolf gets deleted, so false alarms cost more than misses. That decides where we sit on
the operating curve, which is why EER alone is not our target.

The honest part, and say it before they ask. Android has required privileged access for the
VOICE_CALL audio source since Android 10, so a third-party app cannot record the downlink. iOS is
closed outright. The realistic capture path is speakerphone into the microphone, which puts a room
between the caller and our model.

That costs real accuracy and it is measured: ReplayDF, Interspeech 2025. W2V2-AASIST goes from
4.7% to 18.2% EER under replay, and is still at 11.0% after retraining with room impulse responses.

Our position: re-capture is simply a third distribution shift alongside corpus and channel, and it
is the one an actual deployment forces on us. So it goes in the augmentation stack, not the
limitations section. No published number accounts for it, which is what makes measuring it worth
doing.
""")


# ============================================================ 10. REAL-TIME
s = slide()
eyebrow(s, "Act 4", "Deciding during the call")
title(s, [("One window is not a decision.", INK)])

callout(s, M, 2.50, W - 2 * M, 1.25, "The trap",
        [T("5% error per window, 2-second windows, and a 60-second call false-alarms "),
         T("79% of the time", RED, True), T(".")])

tf, _ = panel(s, M, 4.05, hw, 2.10, tag="How we decide", tagcol=AMBER, border=AMBER)
p = para(tf, space_after=12, line=1.15)
run(p, "Add the evidence up", 19, True, INK, DISP)
p = para(tf, space_after=0, line=1.32)
run(p, "Alarm when the total crosses a boundary, not when one window does.", 15, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 4.05, hw, 2.10, tag="What we report")
p = para(tf, space_after=12, line=1.15)
run(p, "Per call-minute", 19, True, INK, DISP)
p = para(tf, space_after=0, line=1.32)
run(p, "False alarms, detection rate, time to detection.", 15, False, INK2, BODY)

notes(s, """
The trap first, and do the arithmetic out loud. It is the most convincing thing on the slide.

If you alarm whenever any single window crosses a threshold, and your per-window false-alarm rate
is 5%, and you use 2-second windows, then a 60-second call has 30 windows. One minus 0.95 to the
30th is 79%. Four calls in five raise a false alarm. The app is uninstalled by lunchtime.

That is why per-window error rate is the wrong number to report and why we report false alarms
PER CALL-MINUTE instead.

How we decide: accumulate a calibrated log-likelihood ratio across windows and alarm when the
running total crosses a boundary. This is Wald's sequential probability ratio test. We add
separate raise and clear thresholds for hysteresis, and a three-second evidence floor so it
cannot fire on the first syllable.

Why SPRT specifically: it is the classical optimum for "decide as soon as the evidence is
sufficient", so the time-to-decision versus error-rate tradeoff falls out of it directly. We
inherit the metric from sequential detection theory instead of inventing one. We compare against
a plain k-of-n consecutive-window rule as a baseline.

Three reported quantities, always together: false alarms per call-minute, detection rate at that
operating point, and time to detection at median and 90th percentile. Plus milliseconds per window
on the actual phone.

Honest caveat if asked: adjacent windows are correlated, which violates the independence
assumption. We calibrate an effective sample size empirically rather than pretending it holds.
""")


# ============================================================ 11. PIPELINE
s = slide()
eyebrow(s, "Act 4", "The system")
title(s, [("What we will build.", INK)])

nodes = [("Train", "ASVspoof 2019 LA", False),
         ("Ours", "Augmentation: codec, silence, room", True),
         ("Front-end", "Raw waveform or CQT", False),
         ("Detector", "RawNet2, AASIST, SSL", True),
         ("Decision", "Evidence over windows", True),
         ("Output", "A risk score", False)]
nw, gap = 1.80, 0.20
total = len(nodes) * nw + (len(nodes) - 1) * gap
x = (W - total) / 2
for i, (tag, body, ours) in enumerate(nodes):
    nx = x + i * (nw + gap)
    rect(s, nx, 2.70, nw, 1.55, fill=WHITE if ours else PANEL,
         line=AMBER if ours else RGBColor(0xE2, 0xE6, 0xEB), lw=1.5 if ours else 1.0)
    tf = tb(s, nx + 0.16, 2.90, nw - 0.32, 1.2)
    p = para(tf, first=True, space_after=7)
    run(p, tag.upper(), 9.5, True, AMBER if ours else MUTED, MONO)
    p = para(tf, space_after=0, line=1.26)
    run(p, body, 12.5, False, INK, BODY)
    if i < len(nodes) - 1:
        tf = tb(s, nx + nw, 3.35, gap, 0.3, align=PP_ALIGN.CENTER)
        p = para(tf, first=True, space_after=0)
        run(p, "→", 14, False, RULE, BODY)

tf, _ = panel(s, M, 4.72, hw, 1.82, tag="What we sweep")
p = para(tf, space_after=0, line=1.34)
run(p, "Seven codecs plus ", 16, False, INK2, BODY)
run(p, "AMR", 16, True, INK, BODY)
run(p, ", which no ASVspoof edition covers.\nWindow length: full, 4 s, 2 s, 1 s.", 16, False, INK2, BODY)

tf, _ = panel(s, M + hw + 0.34, 4.72, hw, 1.82, tag="Never in training")
p = para(tf, space_after=0, line=1.34)
run(p, "In-the-Wild, the held-out attacks, and a small probe of modern cloned voices.", 16, False, INK2, BODY)

notes(s, """
Walk left to right once, then stop. The two amber boxes are the parts that are ours.

Train on ASVspoof 2019 LA, clean. Our augmentation stack sits between the data and the model:
codec chains, silence manipulation, additive noise, room impulse responses, and the speakerphone
re-capture from the last slide. Front-end is raw waveform or CQT, never mel. Detector starts as
RawNet2 to establish the baseline, then AASIST, an SSL front-end and a one-class variant for
comparison. The decision layer accumulates evidence over windows. The output is a risk score that
feeds a multi-layer decision, not a verdict on its own.

What we sweep: the bandwidth ladder, clean 16k through G.722, Opus, a-law, mu-law, GSM, plus
AMR-NB and AMR-WB. AMR matters because it is what mobile calls actually use and no ASVspoof
edition includes it. Window length full, 4 s, 2 s, 1 s, which gives the accuracy-against-latency
curve.

Held out and never trained on: In-the-Wild, the held-out attack family, and a few hundred modern
cloned utterances made only from our own consented recordings, reported per generator.

Practical point worth making: every codec is already in the ffmpeg build on our laptop, and
ASVspoof 2021 ships the codec label per trial, so the sweep costs no setup time. Training fits one
16 GB laptop GPU at roughly 1.5 to 3 hours per run.
""")


# ============================================================ 12. TIMELINE
s = slide()
eyebrow(s, "Act 4", "Plan")
title(s, [("Twelve weeks.", INK)])

TX0 = M
TW = (W - 2 * M) / 12.0          # one week

phases = [("Proposal", 1, 1, PANEL, MUTED, ""),
          ("Baseline", 2, 4, WASH_B, BLUE, "reproduce published EER"),
          ("Augmentation", 5, 7, AMBER, WHITE, "gap measured per codec"),
          ("Generalisation", 8, 9, AMBER, WHITE, "gap reduced"),
          ("Streaming", 10, 11, WASH_B, BLUE, "latency curve"),
          ("Write-up", 12, 12, PANEL, MUTED, "")]

for name, w0, w1, fill, txt, milestone in phases:
    x = TX0 + (w0 - 1) * TW
    wide = (w1 - w0 + 1) * TW

    tf = tb(s, x, 3.28, wide, 0.24, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0)
    label = "WEEK {}".format(w0) if w0 == w1 else "WEEKS {}-{}".format(w0, w1)
    run(p, label, 9.5, False, MUTED, MONO)

    rect(s, x + 0.03, 3.60, wide - 0.06, 1.15, fill=fill, line=None)
    tf = tb(s, x + 0.10, 4.00, wide - 0.20, 0.4, align=PP_ALIGN.CENTER)
    p = para(tf, first=True, space_after=0)
    run(p, name, 14.5, True, txt, BODY)

    if milestone:
        tf = tb(s, x + 0.06, 4.90, wide - 0.12, 0.5, align=PP_ALIGN.CENTER)
        p = para(tf, first=True, space_after=0, line=1.25)
        run(p, milestone, 12, False, INK2, BODY)

notes(s, """
Keep this short, maybe sixty seconds. It exists so the panel knows we have thought about time.

Week 1 is this proposal.

Weeks 2 to 4, baseline. Get RawNet2 training on ASVspoof 2019 LA and reproduce the published
clean-condition EER. This is not research, it proves our setup is correct. We can validate
against the official baseline score files that ship with the 2021 keys, so if our number does not
match, the bug is ours and we find it in week 3 rather than week 10.

Weeks 5 to 7, the augmentation stack. Codec chains, silence manipulation, noise, room impulse
responses, speakerphone re-capture. Then measure the gap per codec across the bandwidth ladder.

Weeks 8 to 9, the generalisation push. Silence masking, the one-class objective, the SSL
front-end, compared on the gap rather than on in-domain EER. This is the core contribution.

Weeks 10 to 11, streaming and the modern-attack probe. SPRT decision rule, latency on the device,
a few hundred cloned utterances from our own consented voices.

Week 12, write-up and defence.

Say the risk out loud: weeks 5 to 9 are where we expect to slip, because building a degradation
pipeline and chasing generalisation both historically overrun. We are saying it now rather than
in week 11. Compute is one 16 GB laptop GPU, roughly 1.5 to 3 hours per training run, which
serialises our experiments and is the main reason the middle phases are the risk.
""")


# ============================================================ 12. SUCCESS
s = slide()
eyebrow(s, "Act 4", "Conclusion")
title(s, [("What success looks like.", INK)])

tf, _ = panel(s, M, 2.50, hw, 2.30, tag="The target", tagcol=BLUE, border=BLUE)
for a, b in [("Out-of-domain EER ", "well below 34%."),
             ("A gap we ", "reduced, and can explain."),
             ("A decision ", "in seconds, on the phone.")]:
    p = para(tf, space_after=14, line=1.3)
    run(p, a, 16, False, INK2, BODY); run(p, b, 16, True, INK, BODY)

tf, _ = panel(s, M + hw + 0.34, 2.50, hw, 2.30, tag="What we will not do")
for t in ["Quote one in-domain number.",
          "Average across corpora or codecs.",
          "Say the problem is solved."]:
    p = para(tf, space_after=14, line=1.3)
    run(p, t, 16, False, INK2, BODY)

callout(s, M, 5.15, W - 2 * M, 1.20, "The position we will defend",
        [T("A detector that travels is worth more than a detector that scores well.", BLUE, True)],
        color=BLUE, wash=WASH_B)

notes(s, """
Close on the claim, not on a summary. Say it as a position you are prepared to argue.

The target, concretely:
- An out-of-domain EER well below the 34 to 37% the literature reports on the same held-out data.
  That is the number we will be judged on.
- A generalisation gap we reduced AND can attribute, so we can say which design decision bought
  how much. An ablation, not a single result.
- A decision within seconds of speech, running on the phone, with the latency cost of every window
  length measured.

What we will not do, and say this deliberately because the panel will respect it:
- Quote one in-domain EER as if it described field performance.
- Average across corpora or codecs to make a result look better than it is.
- Claim the problem is solved. A smaller gap is not a closed gap.

Final line: a detector that travels is worth more than a detector that scores well. We are
optimising the number that survives a change of dataset.

If pushed on "will it work in production": it is a risk signal with a measured error rate, fused
with caller-ID checks, account context and challenge-response. It raises attacker cost. It does
not authenticate anyone on its own. That is also the framing of the assigned Ige et al. reading on
multi-layer defence.
""")


import sys
out = sys.argv[1] if len(sys.argv) > 1 else "proposal.pptx"
prs.save(out)
print("saved", out, "12 slides with speaker notes")
