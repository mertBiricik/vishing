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
- `docs/pipeline.md` - proposed detection pipeline (Day 2)

## Open decisions

- **Dataset.** ASVspoof 2021 LA is the primary candidate: real VoIP/PSTN transmission, 6 codecs, train-clean/test-degraded protocol. Open question is whether to add a second, non-VCTK source (e.g. In-the-Wild) given the cross-corpus generalization collapse documented in ASVspoof 2021 DF.
- **Architecture family.** Ensemble systems win the benchmarks but conflict with the latency requirement. Needs an explicit accuracy/latency tradeoff study.
- **Evaluation protocol.** EER and min t-DCF are utterance-level and offline. A streaming decision needs a per-window metric definition that does not yet exist in the benchmark literature.
