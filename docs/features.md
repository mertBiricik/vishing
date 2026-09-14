# What Actually Discriminates Synthetic Speech, and What Survives a Phone Line

Working note. Two questions the panel will ask: *which features carry the signal*, and *do they survive the channel we care about*.
Evidence is tagged: **[L1]** = ASVspoof 2021 (Liu et al.), **[L4]** = Müller et al. 2022, **[bg]** = established background not sourced from these two papers, **[hyp]** = our hypothesis, untested.

---

## 1. The front-ends used in the literature

| Front-end | What it is | Evidence on performance |
|---|---|---|
| melspec | mel-scaled spectrogram, perceptually weighted | Consistently **worst**. Beaten by cqtspec or logspec for every architecture tested **[L4]** |
| logspec | log-magnitude linear spectrogram, uniform frequency resolution | Strong; second tier **[L4]** |
| cqtspec / CQCC | constant-Q transform, log-spaced bins, better time resolution at high frequency | Best spectral front-end. Swapping melspec for cqtspec gives **+37% average EER improvement, all else constant** **[L4]** |
| LFCC | linear filterbank cepstra, no perceptual warping | Standard ASVspoof baseline (B02, B03); common in top-5 LA systems **[L1]** |
| raw waveform | Sinc / learnable band-pass filters, end-to-end | **Best overall in-domain**: RawGAT-ST 1.23% EER, RawPC 3.09%, RawNet2 3.15% **[L4]** |

### The one-line takeaway
**Perceptually motivated front-ends throw away the evidence.** Mel scaling compresses high-frequency resolution because that is where human hearing is least sensitive. Synthesis artifacts are not where human hearing is sensitive. Every front-end that preserves linear or constant-Q high-frequency detail outperforms mel **[L4]**.

ASVspoof 2021 reaches the same conclusion from the other side: wideband conditions (no codec, G.722, OPUS at 16 kHz) give clearly lower error than narrowband conditions (a-law, μ-law, GSM, PSTN at 8 kHz), which the authors attribute to "the general importance of information at higher frequencies" **[L1]**.

Two independent lines of evidence, one claim: **the discriminative signal is concentrated in the upper band and in fine spectral detail.**

---

## 2. Where the artifact physically comes from

The weak link in a TTS or VC pipeline is the **vocoder**, the component that converts acoustic features back into a waveform. Known artifact families **[bg]**:

- imperfect or inconsistent phase reconstruction
- over-smoothed harmonics and unnatural harmonic-to-noise ratio
- spectral rolloff and missing or synthetic-looking energy in the upper band
- periodic upsampling artifacts from transposed convolutions
- poor modelling of unvoiced, noise-like segments (fricatives, breath, mouth noise)
- absence of natural micro-variation in F0 (jitter, shimmer)

**[L1]** supports the vocoder-centric view empirically: broken down by vocoder family, both neural autoregressive and neural non-autoregressive vocoders produce **higher** EER than traditional vocoders or waveform concatenation, under every codec condition. The artifact is shrinking as vocoders improve, which is the direction commodity voice-cloning tools are moving.

---

## 3. The uncomfortable part: models often learn something else entirely

**Detectors do not necessarily learn the vocoder artifact.** They learn whatever separates the classes in the training set.

**[L1]** ran a hidden subset with non-speech removed by an energy VAD. Performance degraded substantially across LA, PA and DF, worst for TTS attacks. Cause: ASVspoof source audio has long leading and trailing silences; VC attacks reproduce them, TTS attacks do not, so **silence duration and content act as a shortcut cue**. The authors note an adversary can trivially strip silence. **[L4]**'s own prior work (*Speech is Silver, Silence is Golden*) is the dedicated study of this effect.

Consequences for us:
- A measurable share of published EER is a dataset artifact, not voice authenticity.
- The shortcut is **trivially removable by an attacker**, so it is a live attack path against the detector itself.
- It is **absent by construction in our use case**: a live call is continuous audio with real background noise and no studio silence. Any model relying on this cue transfers nothing.

This is a large part of why in-domain numbers do not survive contact with real data.

---

## 4. Does any of it survive a telephone channel?

Short answer: **mostly no, and the reason is structural rather than incidental.** The information the detectors rely on and the information the channel destroys are the same information.

### 4.1 Narrowband coding removes the band, it does not merely attenuate it
G.711 (a-law, μ-law) and GSM operate at 8 kHz sampling, so Nyquist is 4 kHz and the usable PSTN passband is roughly 300 to 3400 Hz **[bg]**. If the artifact lives above 4 kHz it is not degraded, it is **absent**. No amount of model capacity recovers it.

**[L1]** measures exactly this: narrowband C2/C3/C5/C6 are consistently worse than wideband C1/C4/C7, with the worst being C6 (GSM, 13 kbps) and C3 (uncontrolled PSTN transcoding).

### 4.2 Low-bitrate codecs are perceptual codecs, so they are artifact erasers by design
A perceptual codec discards what humans cannot hear. The artifacts that distinguish vocoder output are, by hypothesis, in that same category **[hyp, consistent with L1/L4]**. The codec therefore removes the evidence as a side effect of doing its job well.

### 4.3 The channel adds its own synthesis artifacts, which is worse
**GSM Full Rate is itself an LPC-based vocoder** (RPE-LTP), and Opus contains a linear-prediction mode (SILK) **[bg]**. So genuine human speech transmitted over GSM **has been vocoded**. The detector's core cue, "this waveform shows signs of parametric synthesis", becomes ambiguous: it is now true of bona fide speech too. This predicts a false-alarm problem on genuine callers, not only a miss problem on attacks. Neither paper isolates this, so it is a gap we could actually measure **[hyp]**.

### 4.4 Degradation is attack-selective, not a uniform tax
**[L1]**: attack A18 (non-parallel VC) sits at roughly 0.4 median t-DCF uncoded, rises above 0.8 under PSTN and to about 0.7 under GSM, while other attacks move far less. **The channel preferentially hides the attacks that were already hardest.** Pooled metrics understate operational risk.

### 4.5 Codec effects are not monotonic in bitrate
**[L1]** DF task: ogg Vorbis gives lower EER than mp3 or m4a at any bitrate, and double compression (C8, C9) is only modestly worse than single ogg. Some artifacts survive transcoding. So "more compression is worse" is false as a general rule, and each codec must be measured rather than assumed.

### 4.6 Channel robustness is not the largest error term anyway
**[L1]** Table VI: the same system scores 0.33% EER when bona fide and spoof both come from ASVspoof19, and 23.39% when bona fide comes from VCC18, with codec conditions unchanged.
**[L4]**: RawGAT-ST scores 1.23% in-domain and 37.15% on In-the-Wild found audio; retraining on more ASVspoof data changes nothing (33.1% vs 33.9%), because every ASVspoof split derives from VCTK.

**Corpus and attack generalization dominates codec robustness by a wide margin.** A project that only hardens against codecs is optimizing the second-order term.

---

## 5. What the evidence says to do

Unanimous empirical support:
- **Codec and channel augmentation during training.** Every top-5 LA and DF system in **[L1]** used data augmentation, and all top-5 DF systems used media-codec augmentation specifically. This is the single intervention with no counterexample.
- **Do not use mel.** Use cqtspec, logspec, LFCC, or raw waveform **[L4]**.
- **Prefer raw-waveform end-to-end models.** Best in-domain, and best of a bad lot out-of-domain **[L4]**.

Known limits of those recipes:
- Augmentation buys robustness to **seen** codecs. In **[L1]** the worst conditions were C3 (unknown PSTN transcoding) and the C5-C7 conditions absent from the progress subset. Unseen-channel generalization is unsolved.
- The winning systems are **ensembles fused by score averaging** **[L1]**, which is in direct tension with a latency budget.

---

## 6. Where this leaves the vishing use case

Stated plainly, because the panel will test it: **no published system detects modern neural TTS reliably over narrowband real-time telephony.** The best out-of-domain number in **[L4]** is about 34% EER, which is a coin flip with extra steps, and it was measured on wideband found audio, not on a phone line. Neither paper reports latency at all.

The defensible position is therefore **not** "we will build a reliable authentication gate". It is:

> Audio PAD is a **risk signal with a quantified and honest error rate**, fused into a multi-layer decision alongside caller-ID and signalling checks, account and behavioural context, and challenge-response. It raises attacker cost; it does not by itself authenticate.

This is the framing of reading [2] (Ige et al., multi-layer adaptive framework) and it is the only claim the current evidence supports.

---

## 7. Open hypotheses worth testing (our potential contribution)

Since the upper band is destroyed by the channel, the interesting question is **what discriminative information remains inside 300-3400 Hz and survives LPC-style coding**. Candidates, all **[hyp]**:

1. **Prosodic and temporal cues**: F0 micro-variation, jitter and shimmer, rhythm and phrase timing. Low-frequency, so they survive narrowband. Caution: overlaps with the silence shortcut, so it must be validated with VAD-stripped audio.
2. **Long-horizon consistency** rather than fine spectral detail: does the speaker's channel signature and prosodic behaviour stay coherent across a 30 s call, and does an injected synthetic segment break that coherence.
3. **Physiological residue**: breath intake, mouth noise, and lip smacks that TTS commonly omits, which sit largely below 4 kHz.
4. **Codec-aware modelling**: give the model the codec identity, or train codec-conditional heads, instead of hoping augmentation averages it out.
5. **Explicit false-alarm measurement on vocoded genuine speech** (Section 4.3), which we believe is unmeasured in the current literature.

Items 2, 3 and 5 are the most likely places to find something publishable, and 5 is the cheapest to test.
