# Should We Build the Attack Side? Evidence and Decision

The supervisor suggested the team should also generate deepfake voices, "humanize" them, and
then try to detect them. This note records what the evidence says.

**Verdict in one line: the supervisor is right in direction, wrong in the expensive way.
Build a post-processing and channel harness, not a voice-cloning workstream.**

---

## 1. A hypothesis we held, and its refutation

We initially reasoned: *humanization makes audio convincing to humans, but detectors key on
low-level vocoder artifacts, so humanization is orthogonal to defeating a detector.*

This was tested adversarially through three independent lenses. **All three refuted it.**
The refutation rests on splitting "humanization" in two:

- **(A1) in-speech prosody**: emotion, pacing, intonation, disfluencies inside voiced regions.
- **(A2) the non-speech envelope**: leading and trailing silence, pause structure, room tone,
  background noise, reverberation, re-recording, tempo.

For **(A1)** the orthogonality claim partly survives; the evidence is confounded (see §4).
For **(A2)** it fails outright, and in practice humanization is mostly an (A2) operation.

---

## 2. The non-speech envelope is the detector's highest-weight feature

| Evidence | Result |
|---|---|
| Müller et al., *Speech is Silver, Silence is Golden* (arXiv:2106.12914) | A classifier fed **leading-silence duration alone** reaches 85% accuracy / 15.1% EER. Trimming silence moves RawNet2 from 3.61% to 15.50% EER (2019 LA eval) and 10.38% to 27.39% (2021 LA) |
| Zhang et al., *The Impact of Silence on Speech Anti-Spoofing*, IEEE/ACM TASLP 2023 (arXiv:2309.11827) | Not only silence *duration* but silence *content* differs per waveform generator. Both are primary decision bases. "Silence attacks are easy to implement and difficult to defend against" |
| Ge, Todisco, Evans, SHAP analysis (arXiv:2110.03309) | Classifiers focus on **non-speech intervals** and a narrow low sub-band around 0.5-0.6 kHz |
| SiFDetectCracker, ACM MM 2023 (10.1145/3581783.3613841) | Black-box attack perturbing **only** background noise and mute segments, leaving the voice untouched: **82.2% average success** against RawNet2, RawGAT-ST, RawPC-DARTS, Deep4SNet |

So an attack that restructures pauses and splices genuine room tone into the non-speech
regions is attacking the detector's strongest feature head-on. That is the opposite of
orthogonal.

## 3. The strongest published attack is cheap DSP, not adversarial ML

**Kassis & Hengartner, *Breaking Security-Critical Voice Authentication*, IEEE S&P 2023.**
Seven transformations, fully black-box, real-time, no queries to the target:

> F1 replace leading/trailing silence with silence copied from a bona fide sample of the same
> speaker; F2 remove inter-word silence with WebRTC VAD; F3 boost 1-6 kHz by 1.5x
> (order-20 Butterworth); F4 synthetic local echo (1 ms shifted copies over 100 ms);
> F5 pre-emphasis coefficient 0.5 instead of 0.97; F6 noise reduction; F7 an ASV-side layer.

CM acceptance of spoofs, baseline to full attack:

| CM | Baseline | Attacked |
|---|---|---|
| SSNET | 2.74% | **61.81%** |
| MCG | 1.90% | **65.82%** |
| AIR | 2.32% | 58.02% |
| AASIST | 2.32% | 24.89% |
| RawGAT-ST | 3.16% | 12.03% |
| wav2vec (most robust) | 1.89% | 11.6% |

F1 alone, silence replacement, already moves LCNN from 3.16% to 13.71%.

**It survives a real phone line.** Calls placed with Twilio into an Amazon Connect instance
at 8 kHz. Only 8 of 14 CMs were even usable at 8 kHz. Acceptance spoof to attack:
SSNET 13.8% to 57.46%, AASIST 8.67% to 26.54%, RawGAT-ST 8.09% to 22.15%,
wav2vec 1.52% to 6.03%. The channel blunts the attack but does not stop it.

Gradient-based attacks also exist (**Malafide**, Interspeech 2023, arXiv:2306.07655: an
optimised LTI filter drives RawNet2 3.29% to 23.93% EER, AASIST 0.71% to 13.87% white-box),
but Kassis explicitly concludes that transfer-based adversarial examples are *not* a viable
strategy against CMs. **The cheap attack is the strong one.** ASVspoof 5 includes Malafide
and Malacopula as three fixed adversarial evaluation attacks (A18, A27, A30).

## 4. Where (A1) prosody stands: contested, and that is the opening

- *Can Emotion Fool Anti-spoofing?* (EmoSpoof-TTS, arXiv:2505.23962) holds TTS, vocoder and
  channel fixed and varies only emotion: pre-trained RawNet2 on StyleTTS2 moves from 39.0%
  EER (neutral) to 45.00% (happiness) and 46.75% (sadness). A 5-8 point swing from prosody
  alone. But the neutral baseline is already near chance, so the emotion delta is small next
  to the system-shift delta.
- **No paper cleanly isolates prosody with synthesiser and vocoder held fixed.** Both
  emotional-attack datasets vary emotion *across* different TTS systems.

**This is a real gap and it is small enough to fit our timeline**: one TTS system, one
vocoder, prosody varied, EER measured. That is a controlled experiment nobody has run.

## 5. The number that dominates everything: generator staleness

**RTCFake (arXiv:2604.23742)** is almost exactly this project's setting: modern TTS
(F5-TTS, IndexTTS2, CosyVoice, ChatterboxVC, LLaSA) transmitted through **real RTC/VoIP
platforms**. Detectors trained on legacy corpora, tested there:

| Training corpus | Avg EER on modern TTS over real VoIP |
|---|---|
| ASVspoof 2019 | **50.28%** (chance) |
| DFADD | 47.71% |
| ASVspoof 5 | 43.71% |
| CodecFake | 41.90% |
| CD-ADD (best legacy) | 33.95% |
| **Authors' own generated + transmitted data** | **5.81 - 7.33%** |

**Codecfake** (arXiv:2405.04880, TASLP 2025) shows the same cleanly with no humanization at
all: W2V2-AASIST 0.122% EER in-domain, 41.583% on codec/ALM audio.

**FoeGlass** (arXiv:2606.05101, ICML 2026) searches only the TTS *input* space (transcript,
speed, temperature, style, voice), no signal-level perturbation at all, and drives false
negative rate from 2.24% to 80.72% on XTTS-v2.

Generator modernity alone, prosody held constant, is worth roughly **40 EER points**. That
dwarfs codec robustness, which we had been treating as the main axis.

---

## 6. The honest counter-argument against the cheap plan

Scoping generation as "a small held-out eval set" has a predicted outcome:
**1-3% EER on ASVspoof LA eval, 40-55% EER on self-generated modern attacks.** A flat
result with no gradient and no ablation to run. The only way to produce a gradient is to put
generated attacks *into training*, which by definition makes generation the main workstream.

**This is a genuine fork and the group must choose:**

- **Option A (measurement study).** Accept the 40-point gap as *the* finding. Report per
  generator, never pooled. Defensible, cheap, reproducible, and it answers the field's
  strongest published criticism. Risk: a panel may read it as "you did not build anything."
- **Option B (train on modern attacks).** Generation becomes a main workstream. Produces a
  gradient and an improvement story. Risk: consumes a quarter of the project, carries the
  circularity objection, and needs careful leave-one-generator-out protocol.

Recommendation: **Option A**, because the effect size is enormous and a negative result with
a 40-point effect is not a null result. Revisit if Phase 2 finishes early.

## 7. Circularity: a real risk with a standard, citable mitigation

Generating your own attacks is **standard practice**, not a trap, provided self-generated
data stays out of training. ASVspoof 2019 puts A01-A06 in train/dev and A07-A19 in evaluation
only. ASVspoof 5 has 32 attacks built by external TTS/VC experts on disjoint MLS partitions,
with 16 systems plus 7 adversarial attacks appearing only in evaluation. Generator
fingerprints are trivially learnable: residual-fingerprint attribution identifies which of 5
generators produced a clip at 92-98% accuracy.

**Rule: never put a self-generated sample in the training set.** That one rule removes the
circularity objection entirely, and ASVspoof's own eval-only design is the precedent to cite.

The ASVspoof 2017 organizers made the point directly: they sourced attacks from the synthesis
community specifically to keep them independent of countermeasure developers, because a
priori attack knowledge is unrepresentative of deployment. In the known-attack condition, 12
of 16 ASVspoof 2015 systems scored under 1% EER, best 0.003%. One unseen attack (S10) took
the same systems to 8-46% EER.

---

## 8. Decision

**Cut:** voice cloning as a workstream; perceptual realism work (A1 breath, fillers, emotional
prosody). It buys ground against humans, who are already the weaker detector
(472 participants reach 72.8% accuracy where an ML detector reaches 95.5%, arXiv:2107.09667),
and it carries the heaviest consent and ethics overhead. Public corpora (ASVspoof 5, MLAAD,
SpoofCeleb, RTCFake) already contain more synthesiser diversity than five students can
produce.

**Build, roughly 1-2 weeks, consuming existing corpora rather than synthesising new ones:**
a post-processing and channel harness applying each as a controlled independent condition:

1. VAD trimming and silence-duration manipulation
2. Splicing genuine recorded room tone into non-speech regions
3. Additive noise at fixed SNRs (babble, street, white)
4. RIR convolution at RT60 0.3 / 0.6 / 0.9 s
5. The narrowband codec chain (a-law, mu-law, GSM at 8 kHz vs G.722, Opus at 16 kHz), plus
   AMR-NB and AMR-WB, which ASVspoof does not cover
6. Time stretch and pitch shift
7. Optionally one physical re-record loop, laptop speaker into phone mic

**Build, roughly 1 student-week:** a held-out modern-attack probe. 200-500 utterances from
2-3 permissively licensed systems (CosyVoice 2, IndexTTS-2, Fish-Speech), using **only team
members' own recorded voices**, pushed through the same codec chain. Never used in training.
Reported per generator.

**Mandatory reporting rule:** every EER in the report appears **twice, with and without VAD
silence trimming**. Given §2, any number that does not do this is not evidence about voice
authenticity, and the panel can say so.

### Ethics and licensing guardrails
- Clone only team members' own voices, with recorded consent. No real third parties.
- No calls to real people. Lab only.
- No distribution of generated samples.
- Check weights licences: F5-TTS and XTTS-v2 weights are non-commercial. **Avoid Chatterbox**
  unless its PerTh watermark is explicitly controlled for, since a watermark is learnable as
  a shortcut cue and would silently invalidate results.

---

## 9. Caveats on the evidence above

- The additive-noise evidence is **contradictory**. The laundering paper (arXiv:2408.14712)
  reports large degradation from babble/white/street noise; the real-world-corruption
  benchmark (arXiv:2503.17577) calls noise surprisingly benign except at 5 dB SNR. Different
  SNR ranges and protocols. Do not quote a single noise number as settled.
- SiFDetectCracker's 82.2% is against detectors trained on ASVspoof 2019 LA, the corpus with
  the known silence artifact. Against a CM trained with silence masking it would likely be
  lower. It shows current detectors are breakable this way, not that the surface is permanent.
- RTCFake, FoeGlass, AffectDF, ProSDD and the corruption benchmark are **recent preprints**.
  Verify numbers against the source tables before putting any of them in a submitted document.
- SMIA (arXiv:2509.07677) claims 96-100% attack success but is an unrefereed preprint on a
  *simulated* channel, and reports a roughly 6x unexplained gap over the peer-reviewed
  Kassis baseline on the same CMs. **Do not cite it.**
