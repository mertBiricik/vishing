"""Equal error rate, broken down by condition.

Run it against the official baseline scores first. If the numbers match the
published ones, the evaluation code is correct and every number it produces
later can be trusted.

    python src/eval.py --validate
    python src/eval.py --scores my_scores.txt --keys data/keys/LA/CM/trial_metadata.txt --by codec
"""
import argparse
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
LABELS = {"bonafide", "spoof"}


def compute_eer(bonafide, spoof):
    """Equal error rate. Higher score must mean 'more bonafide'.

    This is the ASVspoof reference implementation, kept verbatim so our numbers
    are comparable with published ones.
    """
    n = bonafide.size + spoof.size
    scores = np.concatenate((bonafide, spoof))
    labels = np.concatenate((np.ones(bonafide.size), np.zeros(spoof.size)))
    order = np.argsort(scores, kind="mergesort")
    labels = labels[order]

    tar_sums = np.cumsum(labels)
    non_sums = spoof.size - (np.arange(1, n + 1) - tar_sums)
    frr = np.concatenate((np.atleast_1d(0), tar_sums / bonafide.size))
    far = np.concatenate((np.atleast_1d(1), non_sums / spoof.size))
    thr = np.concatenate((np.atleast_1d(scores[order[0]] - 1e-3), scores[order]))

    i = np.argmin(np.abs(frr - far))
    return float(np.mean((frr[i], far[i]))), float(thr[i])


def read_scores(path):
    out = {}
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 2:
                continue
            try:
                out[parts[0]] = float(parts[-1])
            except ValueError:
                continue
    return out


def read_keys(path):
    """Parse a protocol / metadata file without hard-coding its column order.

    2019 protocol:  speaker utt - attack label
    2021 metadata:  speaker utt codec transmission attack label trim subset

    The label column is found by looking for bonafide/spoof, and the remaining
    columns are named by position relative to it.
    """
    rows = []
    label_col = None
    with open(path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 3:
                continue
            if label_col is None:
                for i, p in enumerate(parts):
                    if p in LABELS:
                        label_col = i
                        break
                if label_col is None:
                    continue
            rows.append(parts)
    if not rows:
        sys.exit(f"no usable rows in {path}")

    ncol = len(rows[0])
    names = {}
    if ncol >= 8:                       # ASVspoof 2021 metadata
        names = {2: "codec", 3: "transmission", 4: "attack", 6: "trim", 7: "subset"}
    elif ncol >= 5:                     # ASVspoof 2019 protocol
        names = {3: "attack"}

    keys = {}
    for parts in rows:
        meta = {"label": parts[label_col]}
        for idx, name in names.items():
            if idx < len(parts):
                meta[name] = parts[idx]
        keys[parts[1]] = meta
    return keys


def eer_for(pairs):
    """pairs: list of (score, label)."""
    bona = np.array([s for s, l in pairs if l == "bonafide"])
    spoof = np.array([s for s, l in pairs if l == "spoof"])
    if bona.size == 0 or spoof.size == 0:
        return None, len(pairs)
    eer, _ = compute_eer(bona, spoof)
    return eer * 100.0, len(pairs)


def evaluate(scores, keys, by=None, subset=None, quiet=False):
    matched, missing = [], 0
    for utt, meta in keys.items():
        if subset and meta.get("subset") != subset:
            continue
        s = scores.get(utt)
        if s is None:
            missing += 1
            continue
        matched.append((s, meta))

    if not matched:
        sys.exit("no overlap between score file and key file")

    overall, n = eer_for([(s, m["label"]) for s, m in matched])
    if not quiet:
        print(f"  trials scored {n:,}" + (f"   (missing {missing:,})" if missing else ""))
        print(f"  EER  {overall:6.2f} %")

    breakdown = {}
    if by:
        groups = {}
        for s, m in matched:
            g = m.get(by)
            if g is None:
                continue
            groups.setdefault(g, []).append((s, m["label"]))
        if not groups:
            print(f"  (no '{by}' column in this key file)")
        else:
            print(f"\n  by {by}")
            for g in sorted(groups):
                e, cnt = eer_for(groups[g])
                breakdown[g] = e
                shown = f"{e:6.2f} %" if e is not None else "     -  "
                print(f"    {g:<14} {shown}   n={cnt:,}")
    return overall, breakdown


def validate():
    """Score the four official ASVspoof 2021 LA baselines.

    These are the organisers' own system outputs. If our EER differs from the
    published baseline numbers, the bug is in this file, not in a model.
    """
    keys_path = ROOT / "data/keys/LA/CM/trial_metadata.txt"
    if not keys_path.exists():
        sys.exit(f"missing {keys_path}")
    keys = read_keys(keys_path)
    print(f"keys: {len(keys):,} trials\n")

    for name in ["CQCC-GMM", "LFCC-GMM", "LFCC-LCNN", "RawNet2"]:
        sp = ROOT / f"data/keys/LA/CM/{name}/score.txt"
        if not sp.exists():
            print(f"{name}: score file not found, skipped")
            continue
        print(f"=== {name} ===")
        evaluate(read_scores(sp), keys, by="codec", subset="eval")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scores", help="score file: <utt_id> <score>, higher = more bonafide")
    ap.add_argument("--keys", help="protocol or metadata file")
    ap.add_argument("--by", help="break down by this column (codec, attack, trim, transmission)")
    ap.add_argument("--subset", help="restrict to a subset, e.g. eval")
    ap.add_argument("--validate", action="store_true",
                    help="score the official baselines to check this code")
    a = ap.parse_args()

    if a.validate:
        validate()
        return
    if not (a.scores and a.keys):
        ap.error("--scores and --keys are required unless --validate is given")
    evaluate(read_scores(a.scores), read_keys(a.keys), by=a.by, subset=a.subset)


if __name__ == "__main__":
    main()
