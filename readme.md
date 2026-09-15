# Deepfake Voice Detection for Anti-Vishing Systems

Vishing challenge, Emerging Cybersecurity Challenges 2026.

## Scope

Two-day sprint deliverable: **literature review + proposed solution pipeline**, presented to a panel in 20 min.
Implementation follows over ~3 months.

Problem: Presentation Attack Detection (PAD) for audio, under two constraints that most published work does not jointly satisfy:

1. **Degraded channel** - narrowband telephony codecs, packet loss, transcoding, background noise.
2. **Real-time** - streaming decisions with latency low enough for live call integration.

## Documents

- [docs/brief.md](docs/brief.md) - plain-English project brief, start here
- [docs/literature.md](docs/literature.md) - source matrix and per-paper notes
- [docs/features.md](docs/features.md) - what discriminates synthetic speech, and what survives a phone line
- [docs/attack-side.md](docs/attack-side.md) - should we build the attack side? evidence and decision
- **[slides/anti_vishing_proposal.pptx](slides/anti_vishing_proposal.pptx)** - the deck we are presenting: teammate's design, with our evidence slides merged in (13 slides)
- [slides/proposal.pptx](slides/proposal.pptx) - our earlier deck, kept as a source of material
- **[slides/anti_vishing_proposal.pdf](slides/anti_vishing_proposal.pdf)** - same, as PDF
- [slides/proposal.html](slides/proposal.html) - web version ([live](https://claude.ai/code/artifact/8617113b-c43d-4fc1-8e10-ead79f141e3c))
- [slides/build_deck.py](slides/build_deck.py) - regenerates the pptx; edit and re-run if you'd rather change content in code
- [docs/presentation-plan.md](docs/presentation-plan.md) - proposal presentation: narrative, slides, group meeting agenda
- `docs/pipeline.md` - proposed detection pipeline (Day 2)

## Open decisions

- ~~Deployment point~~ **DECIDED: on-device app on the callee's phone, listening to the live call.** Consequences: generous latency budget (human reads the alarm), false alarms cost more than misses, and an extra acoustic re-capture stage because Android will not hand call audio to a third-party app.
- **Bandwidth as independent variable.** Rather than assuming one channel, report performance across the ladder: clean 16k, G.722/Opus wideband, a-law/mu-law 8k, GSM 13 kbps, AMR-NB/WB.
- ~~Attack side scope~~ **DECIDED: Option A, measurement study.** See [docs/attack-side.md](docs/attack-side.md) §6.
- ~~Alarm rule~~ **DECIDED: sequential evidence accumulation (SPRT-style cumulative LLR)** with raise/clear hysteresis and a 3 s evidence floor; `k`-of-`n` consecutive as the baseline comparator. Report false alarms per call-minute, detection rate, and time-to-detection (median, p90). Never report per-window error as the headline.
- **Dataset.** ASVspoof 2021 LA is the primary candidate: real VoIP/PSTN transmission, 6 codecs, train-clean/test-degraded protocol. Open question is whether to add a second, non-VCTK source (e.g. In-the-Wild) given the cross-corpus generalization collapse documented in ASVspoof 2021 DF.
- **Architecture family.** Ensemble systems win the benchmarks but conflict with the latency requirement. Needs an explicit accuracy/latency tradeoff study.
- **Evaluation protocol.** EER and min t-DCF are utterance-level and offline. A streaming decision needs a per-window metric definition that does not yet exist in the benchmark literature.
