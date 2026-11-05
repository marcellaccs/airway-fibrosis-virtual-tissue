"""Exact regression check between two replicates_summary.csv files (Gate B', criterion 1).

docs/gate_Bprime_plan_2026-10-30.md sec 2: with every B' switch off, the six Gate B4
replicates (commit 434bc94, results/cc3d/v1-gateB-rebaseline20k/replicates_summary.csv) must
reproduce exactly. "Exactly" is checked here, column by column, with tolerance 0 by default,
so the check is a script and not a glance at two tables.

Rows are matched on a key column (iter_count by default; rng_seed if iter_count is empty in
either file) because PSCAN workers finish out of order and the row order in the CSV means
nothing. Every column of the REFERENCE file is compared; columns that exist only in the
CANDIDATE (the B' switch columns, future readouts) are listed as extra and do not fail the
check, so the B4 reference stays the reference as the CSV grows. Numeric cells are compared as
numbers (so "0.0" == "0"), everything else as stripped strings.

Usage:
    python model/cc3d/tools/compare_replicates.py REFERENCE.csv CANDIDATE.csv
        [--key iter_count|rng_seed] [--ignore col[,col...]] [--tol 0.0]

Exit status: 0 identical on every compared cell, 1 any difference (or missing/extra rows),
2 usage or unreadable input. Run it after a switches-off scan:
    python model/cc3d/tools/compare_replicates.py \
        results/cc3d/v1-gateB-rebaseline20k/replicates_summary.csv \
        results/cc3d/bprime-regression-alloff/replicates_summary.csv
"""
import argparse
import csv
import sys
from pathlib import Path


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        rows = list(reader)
        return reader.fieldnames or [], rows


def pick_key(requested, ref_rows, cand_rows):
    if requested != "auto":
        return requested
    for key in ("iter_count", "rng_seed"):
        if all(r.get(key, "").strip() for r in ref_rows + cand_rows):
            return key
    return None


def as_number(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def cells_equal(a, b, tol):
    a, b = (a or "").strip(), (b or "").strip()
    na, nb = as_number(a), as_number(b)
    if na is not None and nb is not None:
        return abs(na - nb) <= tol
    return a == b


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("reference", type=Path)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--key", default="auto",
                    help="row-matching column (default: iter_count, else rng_seed)")
    ap.add_argument("--ignore", default="",
                    help="comma-separated reference columns to skip (default: none)")
    ap.add_argument("--tol", type=float, default=0.0,
                    help="absolute tolerance for numeric cells (default 0: exact)")
    args = ap.parse_args(argv)

    try:
        ref_cols, ref_rows = read_rows(args.reference)
        cand_cols, cand_rows = read_rows(args.candidate)
    except OSError as exc:
        print(f"cannot read input: {exc}", file=sys.stderr)
        return 2
    if not ref_rows:
        print(f"reference {args.reference} has no rows", file=sys.stderr)
        return 2

    key = pick_key(args.key, ref_rows, cand_rows)
    if key is None or key not in ref_cols or key not in cand_cols:
        print("no usable key column (iter_count or rng_seed must be filled in both files; "
              "or pass --key)", file=sys.stderr)
        return 2

    ignore = {c.strip() for c in args.ignore.split(",") if c.strip()}
    compared_cols = [c for c in ref_cols if c not in ignore]
    missing_cols = [c for c in compared_cols if c not in cand_cols]
    extra_cols = [c for c in cand_cols if c not in ref_cols]

    ref_by_key = {r[key].strip(): r for r in ref_rows}
    cand_by_key = {r[key].strip(): r for r in cand_rows}
    if len(ref_by_key) != len(ref_rows) or len(cand_by_key) != len(cand_rows):
        print(f"key column {key!r} is not unique within a file", file=sys.stderr)
        return 2

    failures = []
    for k in sorted(ref_by_key, key=lambda s: (as_number(s) is None, as_number(s) or 0, s)):
        if k not in cand_by_key:
            failures.append(f"row {key}={k}: missing from candidate")
            continue
        r, c = ref_by_key[k], cand_by_key[k]
        for col in compared_cols:
            if col in missing_cols:
                continue
            if not cells_equal(r.get(col), c.get(col), args.tol):
                failures.append(f"row {key}={k}, column {col}: reference {r.get(col)!r} "
                                f"vs candidate {c.get(col)!r}")
    for k in sorted(set(cand_by_key) - set(ref_by_key)):
        failures.append(f"row {key}={k}: extra in candidate (not in reference)")
    for col in missing_cols:
        failures.append(f"column {col}: in reference, missing from candidate")

    n_cells = len(ref_by_key) * (len(compared_cols) - len(missing_cols))
    print(f"reference: {args.reference} ({len(ref_rows)} rows)")
    print(f"candidate: {args.candidate} ({len(cand_rows)} rows)")
    print(f"matched on {key!r}; compared {len(compared_cols) - len(missing_cols)} columns x "
          f"{len(ref_by_key)} rows = {n_cells} cells; tolerance {args.tol}")
    if ignore:
        print(f"ignored columns: {', '.join(sorted(ignore))}")
    if extra_cols:
        print(f"extra candidate columns (not compared): {', '.join(extra_cols)}")
    if failures:
        print(f"FAIL: {len(failures)} difference(s)")
        for f in failures:
            print("  " + f)
        return 1
    print("PASS: candidate reproduces the reference exactly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
