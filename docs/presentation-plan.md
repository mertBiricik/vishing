# Proposal Presentation Plan

20 minutes to a panel of experts. ~13 slides plus backup. Every member presents and must be
able to answer about the whole project, not just their section.

---

## The single most important framing decision

**Do not present this as "we will build a detector that works."**

If you promise a detector, the first panel question is "what EER will you achieve?" and every
possible answer is a trap. Promise a low number and you are naive. Promise a high number and
you have proposed a failure.

**Present it as: we will measure where detection breaks, on an axis nobody has measured.**

Under that framing every result is a success. A 50% EER is a finding, not an embarrassment.
This also directly targets the rubric, which weights critical evaluation and explicitly says a
group does not get top marks for describing a technology well.

---

## The narrative arc

Four beats. Everything on every slide serves one of them.

1. **It looks solved.** Published detectors reach 1.23% EER.
2. **It is not solved.** Three independent, published collapses, each an order of magnitude.
3. **And one axis has never been measured at all.** Latency.
4. **So here is what we will measure, and what we will refuse to claim.**

---

## Slide by slide

### 1. Title
Project title, team, course, date. One line under the title: *"A proposal to measure where
audio deepfake detection fails, not to claim it works."* Sets the frame immediately.

### 2. The threat, concretely (60 s)
One specific vishing scenario, told as a story. An attacker clones a voice from public audio
and calls a bank's phone line, or an employee. No statistics on this slide. Make the panel
picture the call. End with the question the rest of the talk answers: *can a machine tell?*

### 3. The field says yes (60 s)
- RawGAT-ST: **1.23% EER**. AASIST: 0.71%.
- Four ASVspoof challenges, 54 teams in 2021 alone.
- Visually: a green, confident slide. You are setting up the reversal.

### 4. Three collapses (3 min) - THE MONEY SLIDE
One table, three rows. Do not rush this slide; it is the heart of the talk.

| Collapse | Evidence | Number |
|---|---|---|
| **Cross-corpus** | Müller et al., Interspeech 2022 | RawGAT-ST 1.23% → **37.15%** EER on real-world found audio. Same model, same weights |
| **Modern generators** | RTCFake (preprint, verify) | ASVspoof2019-trained CM on 2026 TTS over real VoIP: **50.28% EER**. That is chance. Trained on modern attacks: 5.81% |
| **Cheap attack** | Kassis & Hengartner, **IEEE S&P 2023** | 7 basic DSP transforms raise CM acceptance of spoofs from ~2% to **12-66%**. Survives a real Twilio call into Amazon Connect at 8 kHz |

Say out loud: *"These are three different research groups, three different failure modes, and
none of them is a marginal effect."*

Add one line: training on more ASVspoof data does not help (33.9% → 33.1%), because every
split derives from the same VCTK recordings.

### 5. Why: the detector is not learning what we think (2 min)
- Leading-silence duration **alone** classifies at 85% accuracy / 15.1% EER (Müller et al.).
- SHAP analysis: classifiers attend to **non-speech intervals** and a narrow 0.5-0.6 kHz band.
- SiFDetectCracker: **82.2% attack success** touching only background noise and mute segments,
  never the voice itself.

Punchline: *"A meaningful part of published performance is a dataset artifact. An attacker
deletes the silence and it is gone. And a live phone call has no clean silence anyway."*

### 6. The channel: what actually survives a phone line (2 min)
The bandwidth ladder as a figure, not a table if you can draw it.

| Channel | Band | Artifact |
|---|---|---|
| WhatsApp / Teams (Opus) | to 20 kHz | mostly intact |
| VoLTE (AMR-WB) | 50-7000 Hz | mostly intact |
| GSM / PSTN (G.711) | 300-3400 Hz | high-frequency cue gone |

Then the twist, which shows you read past the obvious: low-pass filtering to the telephone band
actually **improves** codec robustness (~25% relative, arXiv:2211.06546), and the F0 sub-band
alone gives 1.15% EER. **What survives narrowband is prosody.** Which is exactly what the cheap
attacks manipulate.

### 7. The axis nobody has measured (90 s)
- Every ASVspoof score is utterance-level and computed offline, over a full recording.
- **Zero** papers in this literature report milliseconds per decision.
- The winning systems are ensembles fused by score averaging, which is structurally
  incompatible with a live-call latency budget.
- There is not even an agreed metric for a streaming decision.

*"The challenge brief asks for real-time. The literature has never measured it."*

### 8. Proposal: the pipeline (2 min)
One diagram. Left to right:

`ASVspoof 2019 LA (clean, train) → degradation harness (codec / silence / noise / RIR) →
front-end (raw waveform or CQT, never mel) → detector → streaming decision every N seconds →
risk score fused into a multi-layer decision`

Call out two boxes explicitly: the **degradation harness** and the **streaming decision**,
because those are ours.

### 9. Proposal: the experiment matrix (2 min)
Independent variables, held-out protocol, and what gets reported.

- **Bandwidth ladder**: clean 16k → G.722/Opus → a-law/μ-law 8k → GSM 13 kbps → AMR-NB/WB
  (AMR is not in ASVspoof; ffmpeg already has it)
- **Front-end**: raw waveform vs CQT vs log-spec (mel excluded, 37% worse)
- **Window length**: full utterance vs 4 s vs 2 s vs 1 s → the latency curve
- **Held-out**: In-the-Wild for cross-corpus; small self-generated modern-attack probe, never
  used in training

### 10. Two contributions nobody has made (2 min)
1. **A latency/accuracy curve for streaming PAD over telephony.** Unmeasured in this field.
   Includes defining the streaming decision metric, which does not currently exist.
2. **False-alarm rate on genuine human speech carried over GSM.** GSM Full Rate is itself an
   LPC vocoder, so real speech arrives already vocoded. The ASVspoof organizers raised this
   concern in **2017** and it has never been quantified. Cheap for us to measure.

Say clearly that (2) was predicted by the organizers, not invented by us. Claiming it as your
own idea is the kind of thing a panel catches.

### 11. How we will report, so we do not fool ourselves (90 s)
This slide is pure rubric points. Three rules:
- **Every EER reported twice**, with and without VAD silence trimming. Given slide 5, a number
  without this is not evidence about voice authenticity.
- **Per generator, never pooled.** Pooling hides the cross-corpus term.
- **Self-generated attacks never enter training.** Removes the circularity objection; ASVspoof
  2019's own A07-A19 eval-only design is the precedent.

### 12. Timeline and risks (90 s)
Phases with milestones. Then name your own risks before the panel does:
- Degradation harness and streaming engineering historically overrun
- Self-generated probe may produce a flat result (1-3% vs 40-55%) with no gradient to study
- Compute is a single laptop GPU (RTX A5000, 16 GB), which is sufficient but serialises runs

### 13. What we will and will not claim (60 s)
Close on the honest conclusion, stated before you are pushed to it:

> Audio PAD is a **risk signal with a measured error rate**, fused with caller-ID and signalling
> checks, account context and challenge-response. It raises attacker cost. It does not
> authenticate anyone by itself.

This is also the framing of the assigned reading (Ige et al., multi-layer adaptive framework),
so you are answering the brief, not dodging it.

---

## Backup slides (Q&A ammunition)

Prepare these. They will be asked.

| Question | Slide to have ready |
|---|---|
| "Why not just use wav2vec2 / SSL front-ends?" | It **is** the most robust in Kassis (1.89% → 11.6% vs SSNET's 61.81%). But it is also the heaviest, which is precisely the latency tradeoff we propose to measure |
| "Why not train on more data?" | Müller: 33.9% → 33.1%. All ASVspoof splits derive from VCTK |
| "Why not ASVspoof 5?" | Newer and includes adversarial attacks, but still 43.71% EER on RTCFake. Same problem |
| "Is this not just reproducing known results?" | Latency is unmeasured; the GSM false-alarm rate is unquantified since 2017; AMR codecs are not in any ASVspoof edition |
| "How do you know your codec simulation is realistic?" | We validate against ASVspoof 2021 LA, which is **real** VoIP and PSTN transmission, not simulation. The paper itself warns that simulated data misled the PA task |
| "Why not build the attack side properly?" | Cost/benefit, plus ethics. See attack-side.md |
| Dataset sizes, GPU, timeline | One logistics slide |

---

## Agenda for tomorrow's group meeting

Four decisions. Nothing else. Do not spend the meeting re-explaining the papers.

1. **Deployment point.** Bank IVR (narrowband PSTN), telco, enterprise Teams/WhatsApp
   (wideband), or victim-side app? Everything downstream depends on this: channel, latency
   budget, false-alarm tolerance. **Decide this first or the rest is unanchored.**
2. **Option A or B** (see attack-side.md §6). Measurement study, or train on modern attacks.
   Recommendation is A.
3. **The streaming metric.** What is the alarm rule? One window, N consecutive windows, or an
   accumulating score? This must be written down before any number is produced.
4. **Speaking order and cross-coverage.** Every member presents, and every member must be able
   to answer about any section. Allocate sections, then rehearse **swapped**: each person
   answers questions on someone else's slides.

## Practical notes

- 20 minutes over ~13 slides is roughly 90 seconds each. Slide 4 gets 3 minutes; take it from
  slides 2 and 12.
- Rehearse once end to end, timed, before the day of.
- Numbers on slides must match the docs. Anything marked preprint in literature.md
  (RTCFake, FoeGlass) should be spoken as "a recent preprint reports", not as settled fact.
  If a panel member knows the field, hedging correctly earns more credit than overclaiming.
