"""Compare the per-MCS diagnostic lines of two CC3D run logs (Gate B' smoke-twin regression).

Companion to compare_replicates.py: the summary CSV is one row per run, this checks the run's
whole trajectory. Keeps only the lines whose content must be identical between a switches-off
run and the reference (field G / C stats every 100 MCS, lumen area, sheet yCOM, the 100-MCS
population line, every repair, mitosis and recruitment event, sheet integrity, the ODE line),
drops lines that later phases add (P / MMP / ECM diagnostics), and reports the first differing
lines. Exit 0 identical, 1 different.

Usage:
    python model/cc3d/tools/compare_run_logs.py REFERENCE.log CANDIDATE.log
Reference for the 3k seed-200 twins: results/cc3d/bprime-ref-3k-seed200/run.log (local).
"""
import re
import sys

KEEP = re.compile(
    r"^(MCS= *\d+ (field [GC]:|lumen area:|epithelial sheet yCOM|\| Eh=|epithelial repair|"
    r"fibroblast mitosis|sheet integrity|mesenchymal cells overlapping|field C lumen max|"
    r"R_fib recruited|myofibroblast local_C|interface occupancy|interface myofibroblast|"
    r"epithelial volume/targetVolume|ODE: WS=)|FINAL:|RNG seed)"
)


def filtered(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as fin:
        for line in fin:
            line = line.rstrip("\n")
            if KEEP.match(line):
                out.append(line)
    return out


a, b = filtered(sys.argv[1]), filtered(sys.argv[2])
print(f"{sys.argv[1]}: {len(a)} compared lines; {sys.argv[2]}: {len(b)} compared lines")
n_diff = 0
for i, (la, lb) in enumerate(zip(a, b)):
    if la != lb:
        n_diff += 1
        if n_diff <= 5:
            print(f"DIFF at compared line {i}:\n  A: {la}\n  B: {lb}")
if len(a) != len(b):
    print(f"line counts differ: {len(a)} vs {len(b)}")
    n_diff += 1
print("IDENTICAL" if n_diff == 0 else f"DIFFERENT ({n_diff} differences)")
sys.exit(0 if n_diff == 0 else 1)
