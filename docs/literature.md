# Literature Matrix - Deepfake Voice Detection for Anti-Vishing

Working document. One row per source in the matrix, one detailed note per source below.
Target: 8–12 high-quality sources (peer-reviewed, challenge reports, standards).

## Matrix

| # | Source | Venue / Year | Data | Front-end | Classifier | Headline result | Channel degradation | Latency reported? | Relevance to us |
|---|--------|--------------|------|-----------|------------|-----------------|---------------------|-------------------|-----------------|
| L1 | Liu et al., *ASVspoof 2021: Towards Spoofed and Deepfake Speech Detection in the Wild* | IEEE/ACM TASLP 2023 (10.1109/TASLP.2023.3285283) | ASVspoof 2021 LA / PA / DF | varied (raw waveform, LFCC, CQT, mel, linear FB) | varied (ResNet, LCNN, SENet, TDNN, GMM) | LA top systems near ASV floor; DF eval EER ≥15% for **all** 33 systems | **Yes** - real VoIP + PSTN, 6 codecs (LA); 3 media codecs + transcoding (DF) | **No** | Defines the benchmark, the degraded-channel protocol, and the generalization failure our project targets |
| L2 | Li & Chen, *Where are we in audio deepfake detection? A systematic analysis over generative and detection models* | arXiv:2410.04324, 2024 | - | - | - | - | - | - | Given reading [1]; survey framing |
| L3 | Ige, Kiekintveld & Piplai, *Deep Learning-Based Speech and Vision Synthesis to Improve Phishing Attack Detection through a Multi-layer Adaptive Framework* | arXiv:2402.17249, 2024 | - | - | - | - | - | - | Given reading [2]; multi-layer defense framing |
| L4 | Müller, Czempin, Dieckmann, Froghyar & Böttinger, *Does Audio Deepfake Detection Generalize?* | Interspeech 2022 (arXiv:2203.16263) | train: ASVspoof19 LA train+dev; eval: ASVspoof19 LA eval + new **In-the-Wild** set (37.9 h, 58 speakers) | cqtspec / logspec / melspec / raw waveform | 12 architectures re-implemented (LCNN family, MesoNet, MesoInception, ResNet18, Transformer, LSTM, CRNNSpoof, RawNet2, RawPC, RawGAT-ST) | RawGAT-ST 1.23% EER in-domain vs. best 33.9% out-of-domain | Partial: found audio with media compression, **not** telephony | **No** | Quantifies cross-domain collapse, ranks front-ends, and measures the cost of fixed-length windows |
| L5 | Wu et al., *ASVspoof: The Automatic Speaker Verification Spoofing and Countermeasures Challenge* | IEEE JSTSP (in `docs/` pile) | ASVspoof 2015/2017 | CQCC, LFCC | GMM, varied | Known-attack condition: 12/16 systems under 1% EER, best 0.003%; one unseen attack (S10) took the same systems to 8-46% EER | Discusses codec/transmission concerns | No | **Canonical challenge report.** States the "codec is itself a vocoder, genuine speech may be scored spoofed" concern we wrongly claimed as our own. Also the citable precedent for eval-only attack partitions |
| L6 | Kassis & Hengartner, *Breaking Security-Critical Voice Authentication* | **IEEE S&P 2023** | ASVspoof 2019 LA + real Twilio/Amazon Connect calls | n/a (attack paper) | attacks 14 CMs incl. AASIST, RawGAT-ST, wav2vec | 7 cheap DSP transforms raise CM acceptance from ~2-4% to **12-66%**; survives real 8 kHz telephony (AASIST 8.67% to 26.54%) | **Yes, real phone calls** | Real-time, no queries | **The single most important paper for our threat model.** Top-tier security venue, code released |
| L7 | Müller et al., *Speech is Silver, Silence is Golden* | ASVspoof 2021 workshop (arXiv:2106.12914) | ASVspoof 2019/2021 LA | varied | RawNet2, ResNet, CNN, LSTM | Leading-silence duration **alone** gives 85% acc / 15.1% EER; trimming silence moves RawNet2 3.61% to 15.50% | No | No | Quantifies the silence shortcut. Basis for our mandatory VAD-trimmed reporting rule |
| L8 | Zhang et al., *The Impact of Silence on Speech Anti-Spoofing* | IEEE/ACM TASLP 31:3374, 2023 (arXiv:2309.11827) | ASVspoof | varied | varied | Silence *duration* and silence *content* are both primary CM decision bases; proposes silence masking + low-pass as mitigation | No | No | The mitigation we should test in Phase 4 |
| L9 | Shim, Wang et al., *Low Pass Filtering and Bandwidth Extension ... Against Codec Variabilities* | arXiv:2211.06546 | ASVspoof + codecs | low-passed spectral | varied | Low-pass to telephone band **improves** codec robustness, up to 25% relative EER reduction | **Yes** | No | **Overturns our "narrowband destroys everything" reasoning.** High-frequency bins overfit |
| L10 | RTCFake | arXiv:2604.23742 (**preprint, verify**) | modern TTS over real RTC/VoIP platforms | varied | varied | ASVspoof2019-trained CM = **50.28% EER (chance)**; trained on modern attacks = 5.81-7.33% | **Yes, real VoIP** | Partly | The decisive generator-staleness number. Closest published setting to ours |
| L11 | Jones et al. | Information & Computer Security, 2021 (in `docs/` pile) | n/a | n/a | n/a | n/a | n/a | n/a | Only rigorous source covering the **vishing / social-engineering** angle. Zero signal processing, but needed for threat model and multi-layer framing |

*(rows L12+ to be added: AASIST, ASVspoof 5 (arXiv:2601.03944), RawNet2 (ICASSP 2021), Malafide (arXiv:2306.07655), SiFDetectCracker (ACM MM 2023), Codecfake (arXiv:2405.04880), wav2vec2/SSL-based CMs, streaming and low-latency CM work)*

### Reviewed and rejected
- **Dsouza et al., IEEE Access 2025** (`docs/Multi-Modal_Comparative_Analysis...pdf`): methodologically broken. **Do not cite as evidence for anything.**
- **Griffin & Rackley, InfoSecCD 2008** (`docs/1456625.1456635.pdf`): three pages, pre-deepfake, broken reference list. Usable only as a one-line "vishing toolchain is cheap" citation.
- **SMIA, arXiv:2509.07677**: unrefereed preprint, simulated channel, ~6x unexplained gap over the peer-reviewed Kassis baseline on the same CMs. Do not cite.

*(placeholder)*

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

---

## L4 - Does Audio Deepfake Detection Generalize? (Müller et al., Interspeech 2022)

### What it is
Fraunhofer AISEC + TU Munich. Two contributions:

1. A **controlled ablation**: twelve architectures from related work re-implemented and trained under one common protocol, so that performance can be attributed to architecture vs. front-end vs. input handling rather than to inconsistent tuning.
2. A new **out-of-domain evaluation set, "In-the-Wild"**: 37.9 h of found audio from 58 English-speaking celebrities and politicians, 17.2 h spoofed and 20.7 h bona fide, average clip 4.3 s, 16 kHz. Fakes are segmented from 219 publicly available clips that advertise themselves as deepfakes; bona fide material is collected separately from podcasts and speeches by the same speakers. Published as an evaluation-only set.

All models train on ASVspoof 2019 LA train+dev, matching standard practice.

### Result 1: front-end choice dominates, and mel is the wrong scale
Across every architecture, melspec is beaten by either cqtspec or logspec. Replacing melspec with cqtspec improves average performance by **37% EER, all other factors constant**.

Reading: the mel scale compresses high-frequency resolution because it models human perception. Synthesis artifacts are not located where human hearing is most sensitive, so a perceptually motivated front-end discards exactly the evidence the task depends on.

This is the same conclusion ASVspoof 2021 reaches from the opposite direction (narrowband conditions degrade CMs because high-frequency information is lost). Two independent lines of evidence, one claim: **discriminative information is concentrated in the upper band and in fine spectral detail.**

### Result 2: raw waveform end-to-end models win in-domain
Best ASVspoof19 eval EER by family (full-length input):

| Model | Front-end | EER % | t-DCF |
|---|---|---|---|
| RawGAT-ST | raw | **1.23** | 0.036 |
| RawPC | raw | 3.09 | 0.071 |
| RawNet2 | raw | 3.15 | 0.078 |
| LCNN-LSTM | cqtspec | 6.23 | 0.113 |
| LCNN | cqtspec | 6.35 | 0.174 |
| ResNet18 | cqtspec | 6.55 | 0.140 |

Raw models use learnable band-pass (Sinc) layers and reach finer feature resolution than fixed spectrogram front-ends.

### Result 3: fixed 4 s windows cost roughly half the performance in-domain

| Input length | ASVspoof19 EER % | t-DCF | In-the-Wild EER % |
|---|---|---|---|
| Full | 9.85 | 0.22 | 60.10 |
| 4 s | 18.89 | 0.39 | 67.25 |

The authors recommend feeding unabridged audio and argue that work using fixed-length inputs sacrifices performance unnecessarily.

**This conflicts directly with our real-time requirement**, and it is the single most important number for our project: it is a first estimate of the accuracy tax of streaming inference.

**But the averaged table hides a reversal.** On In-the-Wild data several models do *better* with 4 s input than with full-length:

| Model | Full EER % | 4 s EER % |
|---|---|---|
| RawNet2 (raw) | 37.82 | **33.94** |
| CRNNSpoof (raw) | 44.50 | **41.71** |
| Transformer (logspec) | 64.79 | **44.41** |
| MesoInception (melspec) | 62.00 | **51.98** |

The best In-the-Wild result in the entire paper is RawNet2 at **4 s**, not full length. So "longer is better" may be an artifact of ASVspoof, where full-length input also exposes more of the silence cue. Under domain shift the advantage partly disappears. **The latency tax may be far smaller in realistic conditions than Table 2 implies, and this is directly testable.** We should test it rather than inherit the paper's recommendation.

### Result 4: the out-of-domain collapse
EER degrades by roughly **200% to 1000%** on In-the-Wild data. Many models approach random guessing; several exceed 50% EER (LCNN logspec 4 s reaches 91.1%, i.e. systematically inverted, not merely uninformative, which indicates severe distribution shift rather than mere noise).

Best In-the-Wild results are ~34-38% EER (RawNet2, RawGAT-ST, MesoInception logspec). For context, RawGAT-ST scores 1.23% in-domain and 37.15% out-of-domain on the same trained model.

### Result 5: more in-domain data does not fix it
Retraining the best In-the-Wild model (RawNet2, 4 s) on ASVspoof 2019 train+dev+eval gives 33.1 ± 0.2% EER, i.e. **no improvement**. All ASVspoof splits derive from the same VCTK source, so additional data adds no information relevant to real-world generalization.

Implication: scaling the existing benchmark is not a path to field performance. Domain diversity is.

### Critical caveats (for our evaluation section)
- Re-implementations score 2-4% EER worse than originally published numbers; the authors state they did not tune hyperparameters. **Relative** comparisons are the contribution, absolute numbers are conservative.
- **Selection bias in In-the-Wild fakes.** Clips were chosen because they *advertise* themselves as deepfakes, and the speakers "talk absurdly and out-of-character". That is a prosodic and semantic domain shift on top of the synthesis artifact, so "deepfake detection" is partly confounded with "unusual speech detection".
- **Provenance asymmetry between classes.** Fake clips come from deepfake showcase videos, bona fide clips from podcasts and speeches, collected separately. Despite manual matching, channel and recording provenance may differ systematically between the two classes. This cuts both ways: it could inflate or deflate measured performance.
- In-the-Wild is **not a telephony corpus**. Its degradation is media compression and heterogeneous recording, not narrowband coding. It tests corpus, speaker and attack generalization, **not** our channel.
- Evaluation-only, 58 speakers, English only.
- The paper's own reference [28] (Müller et al., *Speech is Silver, Silence is Golden*) is the silence-artifact study, corroborating the ASVspoof 2021 non-speech hidden-subset finding in L1. Worth citing directly.

### How L1 and L4 divide the evaluation problem
- **L1 (ASVspoof 2021 LA)** gives us the *channel* axis: real VoIP and PSTN, six codecs, controlled and balanced.
- **L4 (In-the-Wild)** gives us the *domain* axis: unseen speakers, unseen attacks, unseen provenance.

Neither covers the other. Using both, and reporting them separately rather than pooled, resolves the open dataset question in the project readme.
