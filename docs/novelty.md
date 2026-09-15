# What is actually novel here, and what is not

Written after a targeted literature check that killed two claims we had been ready to make.
Read this before anyone says "nobody has done this" in front of a panel.

## The two claims we tested

**Claim 1.** Nobody has crossed degraded telephony channels with modern (2024+) generators.
Reasoning: ASVspoof 2021 LA has real telephony but 2019-era attacks (A07-A19); SONAR has modern
generators but clean audio. So the cross is open.

**Claim 2.** Nobody has tested whether the foundation-model generalization advantage survives
narrowband telephony. Reasoning: wav2vec2, WavLM and Whisper are pretrained on 16 kHz wideband.
Feeding them 8 kHz GSM-decoded audio is out of distribution for the **backbone**, not just the
classifier head, so the SSL advantage might collapse disproportionately.

Both were wrong in their broad form.

---

## Claim 1: dead in its broad form

**ASVspoof 5** (Wang, Delgado, Tak et al., arXiv:2408.08739, ASVspoof Workshop 2024).
Evaluation attacks A17-A32 include **A28 = YourTTS and A29 = XTTS, both zero-shot**, plus ZMM-TTS,
ToucanTTS+BigVGAN, DiffVC and Malafide/Malacopula adversarial variants. The eval set applies
**12 codec conditions**: C08 opus 8 kHz, **C09 AMR-NB 8 kHz at 4.75-12.20 kbps**, C10 speex 8 kHz,
C11 varied 8 kHz. Narrowband data is downsampled to 8 kHz, codec-processed, and upsampled. Track 2
is explicitly framed as telephony. 54 teams competed on exactly this cross.

**Delgado et al., "On Deepfake Voice Detection: It's All in the Presentation", ICASSP 2026**
(arXiv:2509.26471, Microsoft). This is our threat model, published. Switchboard and MLS voices
cloned with **ElevenLabs, Play.ht, OpenAI Voice Engine, Mars5, YourTTS**, then physically presented
into a call-centre path (Bluetooth digital injection, analog injection, loudspeaker) across
**16 calling device types, everything at 8 kHz**.

Also relevant: RTCFake (arXiv:2604.23742, ACL 2026) puts 600 h of modern TTS through real RTC
platforms, but wideband rather than PSTN. ADD-C / MGAA (arXiv:2504.12423, 2508.01467, preprints)
use six VoLTE/VoIP codecs but at 16 kHz with legacy generators.

### What survives

The **open-source 2024-2026 generation** is not covered. ASVspoof 5's newest generator is XTTS
(2023). Delgado's generators are 2024 but all **commercial APIs**. Nobody has run F5-TTS,
CosyVoice 2/3, IndexTTS-2, Seed-VC, VibeVoice or Qwen3-TTS through narrowband codecs.

This is more than a version bump, for three reasons:

1. **Threat relevance is inverted.** Commercial APIs carry safeguards, usage logging, cost and in
   some cases watermarking. A real attacker uses a local open model precisely because it is free,
   unlogged and unrestricted. So the generators the literature covers are the ones an attacker
   would avoid.
2. **The architecture family changed.** XTTS and YourTTS are one generation. F5-TTS is
   flow-matching, CosyVoice is LLM plus flow. Different generation mechanisms leave different
   artifacts. Codecfake made exactly this argument for neural-codec generation.
3. **The result is a decay rate.** Showing that an ASVspoof 5-trained detector holds on
   XTTS-over-AMR but drops on F5-TTS-over-AMR quantifies how fast a benchmark rots. Incremental,
   but useful and honest.

---

## Claim 2: mostly dead, and the answer is already partly known

**Tak et al., Odyssey 2022 (arXiv:2202.12233), Table 5** is the measurement we thought was missing.
ASVspoof 2021 LA per-codec EER:

| System | C1 clean | C3 PSTN + mu-law | C6 GSM 8k | Pooled |
|---|---|---|---|---|
| Sinc front-end (traditional) | 6.36 | 15.64 | 10.40 | 11.47 |
| wav2vec 2.0, no augmentation | 2.06 | **19.09** | 7.55 | 6.15 |
| wav2vec 2.0 + SA + DA (RawBoost) | 0.30 | **0.56** | 0.81 | 0.82 |

Our hypothesis is confirmed and neutralised in one table. Unaugmented wav2vec2 degrades 9.3x from
clean to PSTN and is **beaten in absolute terms by the traditional front-end** there. But
augmentation flattens the slope completely. **So the collapse is a training-data problem, not a
backbone out-of-distribution ceiling.**

Counter-evidence against our direction: **VoxENES 2026** (arXiv:2607.11706, preprint) Table 6,
`resample_8k` vs original EER: W2V-DF 53.9 to 42.0, W2V-Large 39.9 to 34.3, W2V-AASIST 41.0 to
37.5, while AASIST2 goes 54.4 to **59.1** and RawNet2 51.3 to **55.6**. SSL improved at 8 kHz,
traditional models got worse. Shim & Wang (arXiv:2211.06546) similarly found low-pass to the
telephone band helps.

### What survives

A controlled **degradation-slope sweep that separates backbone OOD from classifier OOD**: training
fixed, bandwidth swept, same head, comparing a 16 kHz-pretrained backbone against a
bandwidth-matched one. Nobody has isolated that. It is the mechanism question, not the existence
question. Sharper than Claim 1's remnant, but heavier on compute.

---

## The finding that matters most for our deck

**Delgado et al. (ICASSP 2026)** compared **WavLM Large (316M)** against a lightweight
**logmel-ResNet-CoT (3.55M)**, both at 8 kHz. The small model "remains competitive" and **beats
WavLM on real-world injection: 89.4% vs 88.2% detection at FAR = 1%**.

This cuts against a one-sided "foundation models are the bet" slide. SONAR's finding (foundation
models generalize better across generators) and Delgado's finding (a small model is competitive in
the real telephony path) are both true and are about different axes. Our deck has to say both, or a
panel member who knows Delgado will take the slide apart.

---

## How to frame it, in one paragraph

Do not say: "nobody has measured modern generators over telephony." It is false and easy to catch.

Say instead: published telephony evaluations use either commercial APIs (Delgado) or 2023-era open
models (ASVspoof 5). The generators a real attacker can run locally for free are not covered. We
measure how fast the benchmark decays against them, we test whether the known fix (codec
augmentation, which took wav2vec2 from 19.09% to 0.56% on PSTN) still holds, and we report whether
the foundation-model advantage survives the channel or whether a small model is enough.

Cite ASVspoof 5 and Delgado as the work we build on, not as competition.

## Note on grading

The rubric weights originality at **10%**. Technical depth is 20%, quality of the proposed solution
15%, source quality 15%. An honest incremental contribution scores better than an overclaim that
collapses under one question.

## Sources
- ASVspoof 5: https://arxiv.org/abs/2408.08739 (workshop, peer-reviewed)
- Delgado et al., ICASSP 2026: https://arxiv.org/abs/2509.26471
- Tak et al., Odyssey 2022: https://arxiv.org/abs/2202.12233
- Shim & Wang: https://arxiv.org/abs/2211.06546
- VoxENES 2026: https://arxiv.org/html/2607.11706v1 (preprint, verify before citing)
- RTCFake: https://arxiv.org/abs/2604.23742 (preprint)
- SONAR / Li, Chen & Wei: https://arxiv.org/abs/2410.04324 (v4, March 2025)
