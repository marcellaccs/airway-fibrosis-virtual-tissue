"""
Summarize a PSCAN replicate table (replicates_summary.csv, written by
DiagnosticsSteppable.write_replicate_summary) and compare lumen narrowing against a
standing baseline -- Gate B4 of docs/roadmap_revision_2026-10-27.md.

Usage (any Python with numpy; scipy optional for the p-value):
    python model/analysis/rebaseline_summary.py results/cc3d/<scan>/replicates_summary.csv
    python model/analysis/rebaseline_summary.py <csv> --baseline -8.6 -12.6 -13.7 -10.7 -10.9 -17.2

The default --baseline is the 2026-09-26 pinned n = 6 (seeds 101-106,
results/cc3d/v1-epi64-reps20k, lab-notebook/2026/2026-09-18.md): -8.6 % to -17.2 %,
mean -12.3 %, SD 3.0. Nothing from before 2026-09-18 is comparable and nothing older is
offered here.

Reports: per-replicate rows; mean, SD (n-1), min, max of lumen_pct_change; the Tier 1
checks (every replicate negative, fragmented = isolated = overlap = 0, lumen_C_max = 0);
Welch's t against the baseline with the Welch-Satterthwaite df and, if scipy is present,
the two-sided p. With n = 6 vs 6 this is a coarse instrument -- say so when quoting it.
"""
import argparse
import csv
import math
import sys
from pathlib import Path

BASELINE_2026_09_26 = [-8.6, -12.6, -13.7, -10.7, -10.9, -17.2]


def mean_sd(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")
    return m, sd


def welch(a, b):
    ma, sa = mean_sd(a)
    mb, sb = mean_sd(b)
    na, nb = len(a), len(b)
    va, vb = sa ** 2 / na, sb ** 2 / nb
    t = (ma - mb) / math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (na - 1) + vb ** 2 / (nb - 1))
    try:
        from scipy import stats
        p = 2 * stats.t.sf(abs(t), df)
    except ImportError:
        p = None
    return t, df, p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", type=Path)
    ap.add_argument("--baseline", type=float, nargs="+", default=BASELINE_2026_09_26,
                    help="baseline lumen_pct_change values (default: the 2026-09-26 pinned n = 6)")
    args = ap.parse_args()

    with args.csv.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"{args.csv}: no rows")

    cols = ["scan_iteration", "iter_count", "rng_seed", "final_mcs", "lumen_area_px", "lumen_pct_change",
            "n_Eh", "n_Ed", "n_Fib", "n_MyoF", "mean_G_subepithelial", "mean_C_subepithelial",
            "repair_events", "fibroblast_divisions", "fragmented", "isolated", "mesenchymal_overlap",
            "lumen_C_max"]
    print(" | ".join(cols))
    for r in sorted(rows, key=lambda r: int(r["scan_iteration"] or 0)):
        print(" | ".join(str(r.get(c, "")) for c in cols))

    pct = [float(r["lumen_pct_change"]) for r in rows]
    m, sd = mean_sd(pct)
    print()
    print(f"n = {len(pct)} replicates, project FIBROBLAST_INITIAL_NUMBER = "
          f"{sorted({r.get('fibroblast_initial_number', '?') for r in rows})}, "
          f"repair enhancement carried = {sorted({r.get('repair_enhancement_carried', '?') for r in rows})}")
    print(f"lumen narrowing at MCS {sorted({r['final_mcs'] for r in rows})}: "
          f"{min(pct):+.1f}% to {max(pct):+.1f}% (mean {m:+.1f}%, SD {sd:.1f})")

    tier1 = all(x < 0 for x in pct)
    clean = all(int(r["fragmented"]) == 0 and int(r["isolated"]) == 0 and int(r["mesenchymal_overlap"]) == 0
                and float(r["lumen_C_max"]) == 0.0 for r in rows)
    print(f"Tier 1 (every replicate narrows): {'PASS' if tier1 else 'FAIL'}; "
          f"clean-run checks (no fragmentation/isolation/overlap, no lumen collagen): {'PASS' if clean else 'FAIL'}")
    repairs = [int(r.get("repair_events", 0)) for r in rows]
    print(f"repair events per replicate: {repairs} (B1 criterion i: every replicate >= 1 -> "
          f"{'PASS' if all(x >= 1 for x in repairs) else 'FAIL'})")

    bm, bsd = mean_sd(args.baseline)
    t, df, p = welch(pct, args.baseline)
    print()
    print(f"baseline: {min(args.baseline):+.1f}% to {max(args.baseline):+.1f}% "
          f"(mean {bm:+.1f}%, SD {bsd:.1f}, n = {len(args.baseline)})")
    print(f"difference of means (new - baseline): {m - bm:+.1f} points; "
          f"Welch t = {t:+.2f}, df = {df:.1f}" + (f", two-sided p = {p:.3f}" if p is not None else
                                                    " (scipy not available: no p-value)"))


if __name__ == "__main__":
    main()
