# Literature Matrix - Deepfake Voice Detection for Anti-Vishing

Working document. One row per source in the matrix, one detailed note per source below.
Target: 8–12 high-quality sources (peer-reviewed, challenge reports, standards).

## Matrix

| # | Source | Venue / Year | Data | Front-end | Classifier | Headline result | Channel degradation | Latency reported? | Relevance to us |
|---|--------|--------------|------|-----------|------------|-----------------|---------------------|-------------------|-----------------|
| L1 | Liu et al., *ASVspoof 2021: Towards Spoofed and Deepfake Speech Detection in the Wild* | IEEE/ACM TASLP 2023 (10.1109/TASLP.2023.3285283) | ASVspoof 2021 LA / PA / DF | varied (raw waveform, LFCC, CQT, mel, linear FB) | varied (ResNet, LCNN, SENet, TDNN, GMM) | LA top systems near ASV floor; DF eval EER ≥15% for **all** 33 systems | **Yes** - real VoIP + PSTN, 6 codecs (LA); 3 media codecs + transcoding (DF) | **No** | Defines the benchmark, the degraded-channel protocol, and the generalization failure our project targets |
| L2 | Li & Chen, *Where are we in audio deepfake detection? A systematic analysis over generative and detection models* | arXiv:2410.04324, 2024 | - | - | - | - | - | - | Given reading [1]; survey framing |
| L3 | Ige, Kiekintveld & Piplai, *Deep Learning-Based Speech and Vision Synthesis to Improve Phishing Attack Detection through a Multi-layer Adaptive Framework* | arXiv:2402.17249, 2024 | - | - | - | - | - | - | Given reading [2]; multi-layer defense framing |

*(rows L4+ to be added: RawNet2, AASIST, ASVspoof 5, In-the-Wild dataset, streaming/low-latency CM work, wav2vec2-based CMs)*

---

## L1 - ASVspoof 2021 (Liu et al., TASLP 2023)

### What it is
Summary and post-hoc analysis of the ASVspoof 2021 challenge, 54 teams in the evaluation phase.
Three independent sub-challenges:

- **LA (Logical Access)** - detect VC/TTS attacks after transmission over **real** telephony (VoIP via Asterisk PBX, and PSTN). Tandem CM + ASV.
- **PA (Physical Access)** - detect replay attacks recorded in **real** physical rooms (train data is simulated).
- **DF (Deepfake, new in 2021)** - detect VC/TTS in **compressed** media audio, no ASV, standalone CM.

The stated purpose of the 2021 edition is to move from clean lab audio toward "in the wild" conditions. This is exactly the premise of our challenge brief.

### Protocol detail that matters most
**No new training data was released.** Participants had to train on the ASVspoof 2019 LA train/dev partitions, which are **clean** (no codec, no transmission), and were evaluated on encoded/transmitted audio. External speech data was forbidden; external *non-speech* resources (noise, impulse responses, codec software) were explicitly allowed for augmentation.

So ASVspoof 2021 is structurally a **train-clean / test-degraded generalization benchmark**. That is the same setting a real anti-vishing deployment faces.

### LA evaluation conditions (Table II)

| Cond. | Codec | Sampling rate | Transmission | Bitrate |
|-------|-------|---------------|--------------|---------|
| C1 | none | 16 kHz | none | 250 kbps |
| C2 | a-law | 8 kHz | VoIP | 64 kbps |
| C3 | unknown + μ-law | 8 kHz | PSTN + VoIP | unknown / 64 kbps |
| C4 | G.722 | 16 kHz | VoIP | 64 kbps |
| C5 | μ-law | 8 kHz | VoIP | 64 kbps |
| C6 | GSM FR 6.10 | 8 kHz | VoIP | 13 kbps |
| C7 | OPUS | 16 kHz | VoIP | VBR 16 kbps |

Spoofed trials use 13 VC/TTS/hybrid algorithms (A07–A19) from ASVspoof 2019 LA. Source speech is VCTK.
Trials: LA eval = 14,816 bona fide / 133,360 spoofed, 37 F + 30 M speakers.

### DF evaluation conditions (Table IV)
C1 uncompressed 256 kbps; C2/C3 low/high mp3; C4/C5 low/high m4a (AAC); C6/C7 low/high ogg Vorbis; C8 mp3→m4a; C9 ogg→m4a (transcoding).
Source data from **three** corpora: ASVspoof 2019 LA eval (VCTK), VCC 2018 (DAPS), VCC 2020 (EMIME). >100 attack algorithms.
DF eval = 14,869 bona fide / 519,059 spoofed.

### Findings we should build on

**1. Bandwidth, not transmission route, drives LA degradation.**
Wideband conditions (C1 no codec, C4 G.722, C7 OPUS) give clearly lower min t-DCF than narrowband (C2 a-law, C3 PSTN, C5 μ-law, C6 GSM). The authors read this as evidence that CMs depend on **high-frequency information**, which narrowband telephony codecs discard. Worst conditions are C6 (GSM, 13 kbps) and C3 (uncontrolled PSTN transcoding).
Meanwhile transmission route (LAN vs. France→Italy vs. France→Singapore) had essentially **no** effect. Implication for our degradation simulator: prioritize codec and bandwidth modelling; network path/jitter modelling is low-value.

**2. Attack difficulty interacts with the channel.**
A18 (non-parallel VC), already hard in clean conditions (median t-DCF ≈0.4 at C1), becomes disproportionately harder after low-bandwidth encoding (>0.8 at C3, ≈0.7 at C6). Degradation is **not** a uniform accuracy tax; it selectively hides certain attack families.

**3. The DF task is a generalization failure, and the numbers are stark.**
23 of 33 systems scored <10% EER on the progress subset; the best was <1%. On the evaluation subset **every** system exceeded 15% EER.
Table VI makes the cause explicit for the top systems:

| Bona fide / spoof source | T23 | T20 | T08 | B04 (RawNet2) |
|---|---|---|---|---|
| ASV19 / ASV19 | 0.33% | 2.41% | 3.75% | 6.21% |
| VCC18 / all | 23.39% | 27.64% | 31.03% | 34.44% |
| all / all | 15.63% | 16.04% | 18.29% | 22.38% |

Same system, same codecs: **0.33% → 23.39% EER** purely from changing the source corpus. Cross-corpus generalization, not codec robustness, is the dominant error term. Any single-dataset EER we report is close to meaningless on its own.

**4. Neural vocoders are harder to detect than traditional ones** across every codec condition (Fig. 6). Relevant because current commodity voice-cloning tools used in real vishing are neural.

**5. Compression ordering is counterintuitive.** ogg Vorbis gave *lower* EER than mp3 or m4a regardless of bitrate, and double compression (C8/C9) was only modestly worse than single ogg. Some spoofing artifacts survive transcoding.

**6. Non-speech leakage - the most important limitation for us.**
A hidden subset had non-speech segments removed with an energy VAD. Performance degraded substantially on LA, PA and DF, worst for **TTS** attacks. Explanation: LA source audio has long leading/trailing silences; VC attacks reproduce them, TTS attacks do not, so silence duration acts as a shortcut cue. The authors note an adversary can trivially strip silence.
For a deployed anti-vishing system this is a direct attack path against the detector, and it means reported ASVspoof EERs are optimistic.

**7. Simulated evaluation data misleads (PA).** Top-10 systems performed much worse on the hidden *simulated* replay subset than on real recordings; four of ten had min t-DCF >0.99. The authors caution against using simulation to estimate real-environment performance. Our project intends to simulate codec degradation - this is the direct argument for validating against real transmitted audio (ASVspoof 2021 LA is real VoIP/PSTN, so it serves as that check).

**8. What the top systems actually did** (Table V): every top-5 LA and DF system used **data augmentation** (transmission codec and/or media codec augmentation, RIR, MUSAN); almost all were **ensembles** fused by score averaging; classifiers were mostly ResNet/LCNN/SENet variants over short-term spectral features or raw waveform.
Baselines: B01 CQCC-GMM, B02 LFCC-GMM, B03 LFCC-LCNN-LSTM, B04 RawNet2.

### Gaps this paper leaves open (our project's opening)

- **No latency or real-time analysis anywhere.** ASVspoof scores are utterance-level, offline, computed over full recordings. Streaming/chunked inference and per-decision latency are simply not part of the benchmark. Our brief requires exactly this, so it is a genuine gap, not a re-implementation.
- **No additive noise in LA 2021** - the paper states this was deferred to a future edition. Real vishing calls include room noise, mobile handsets and background speech.
- **Ensembles + score averaging** are the winning recipe, which directly conflicts with a low-latency requirement. The accuracy/latency tradeoff is under-explored.
- **Silence-based shortcut learning** is documented but not solved.

### Open items
- Paper text reviewed here covers Sections I–IV. Sections V+ (limitations, roadmap, post-challenge results survey) still to be read - the roadmap section likely names successor work (ASVspoof 5) we should cite.
