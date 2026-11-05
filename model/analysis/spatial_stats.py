"""
Spatial statistics for the collagen/ECM field: scoring focal vs diffuse lesions.

Why this exists
---------------
The focal-vs-diffuse experiment (A18, docs/validation_targets.md §3.6) holds *total*
epithelial injury fixed and varies only its spatial clustering. A scalar collagen area
fraction therefore cannot separate the two conditions by construction -- both arms are
designed to produce a similar burden. The discriminating quantity is the spatial
arrangement of the deposited matrix.

Precedent: Roop et al. (2026) applied Ripley's K to AI-segmented preclinical lung fibrosis
and separated samples with *similar* Ashcroft scores and *similar* total fibrosis content
by spatial distribution alone. Cogno et al. (2022) used ECM density distribution histograms
for the same matched-total, different-shape comparison.

Design notes
------------
- Post-processing, not a CC3D steppable. It runs on saved fields so it can be re-tuned and
  re-run without re-running the simulation, and it has no CompuCell3D dependency (numpy +
  scipy only -- installable into `tox-ode`, so `cc3d` is left alone per CLAUDE.md).
- Field-based, not point-based. Ripley's K is classically defined on a point pattern; our
  ECM is a scalar field on a lattice. Two routes are provided:
    * `ripleys_k_weighted`   -- treats field mass as marks (no thresholding, uses all the data)
    * `ripleys_k_points`     -- thresholds to a binary mask and uses site centroids
  Report both. If they disagree, the result is threshold-sensitive and should be said so.
- Edge correction is by the translation/border method: only points at least r from the
  boundary are used as centres. This is deliberately the conservative choice; a fixed outer
  boundary (A8) plus Neumann lateral boundaries (A14) mean edge artefacts are a live risk.

Reference for interpretation
----------------------------
    L(r) - r  >  0   clustered (focal)
    L(r) - r == 0    complete spatial randomness (diffuse / uniform)
    L(r) - r  <  0   regular / dispersed

The A14 focal->diffuse threshold is operationalised as the smallest `S_M2` at which
max_r (L(r) - r) for the exposed condition falls inside the CSR envelope.

Usage
-----
    python spatial_stats.py --fields results/cc3d/run-A/collagen_*.npy --label focal \\
                            --out results/analysis/run-A_spatial.csv

    from spatial_stats import compare_conditions
    verdict = compare_conditions(focal_fields, diffuse_fields)
"""

from __future__ import annotations

import argparse
import glob
import json
from dataclasses import dataclass, asdict

import numpy as np

# numpy only, deliberately. scipy is not assumed to be present, and per CLAUDE.md we do not
# install extra packages into the `cc3d` env. Neighbour counting is done by FFT convolution
# with a disc kernel, which is exact on a lattice and O(N log N).


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_field(path: str) -> np.ndarray:
    """Load a 2D scalar field from .npy, .csv or .txt. Returns float64 array."""
    if path.endswith(".npy"):
        arr = np.load(path)
    else:
        arr = np.loadtxt(path, delimiter="," if path.endswith(".csv") else None)
    arr = np.asarray(arr, dtype=np.float64)
    if arr.ndim != 2:
        raise ValueError(f"{path}: expected a 2D field, got shape {arr.shape}")
    return arr


# ---------------------------------------------------------------------------
# Scalar burden (the quantity that should NOT separate the conditions)
# ---------------------------------------------------------------------------

def area_fraction(field: np.ndarray, threshold: float, mask: np.ndarray | None = None) -> float:
    """Fraction of tissue sites whose ECM exceeds `threshold`.

    `mask` is the tissue domain (exclude lumen and the outer boundary, A8/A16), so the
    denominator matches a histological 'percent of wall area'. Flagged in
    docs/validation_targets.md §6: our denominator must match Islam et al. (2023) for the
    2-40% band comparison to mean anything.
    """
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    if m.sum() == 0:
        return float("nan")
    return float((field[m] > threshold).sum() / m.sum())


def total_burden(field: np.ndarray, mask: np.ndarray | None = None) -> float:
    """Summed ECM mass per tissue site. Burden, not density -- see the open question in
    A14 raised by Teitz-Tennenbaum et al. (2025), who found fiber number up but fiber
    density unchanged."""
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    if m.sum() == 0:
        return float("nan")
    return float(field[m].sum() / m.sum())


# ---------------------------------------------------------------------------
# Ripley's K / L
# ---------------------------------------------------------------------------

def _radii(max_r: float, n_r: int) -> np.ndarray:
    return np.linspace(max_r / n_r, max_r, n_r)


def mean_cell_diameter(cell_id_field: np.ndarray, ignore: tuple = (0,)) -> float:
    """Characteristic length of the lattice: the equal-area disc diameter of the mean cell.

    Pass a lattice of CC3D cell IDs (0 = medium by default). Returns
    d = 2 * sqrt(mean_cell_area / pi), in lattice units.

    Why this exists
    ---------------
    Ripley's K carries units of distance, but A7 commits the model to no lattice-site-to-um
    mapping. So a K curve from the model and a K curve from histology are not directly
    comparable: they live on different rulers. The fix is to express radius in units of a
    length that is well defined on BOTH sides, and mean epithelial cell diameter is the
    natural choice -- it is measurable on the lattice and measurable in a stained section.

    Report K(r/d) rather than K(r) whenever the comparison target is real tissue.
    """
    ids = cell_id_field.ravel()
    ids = ids[~np.isin(ids, ignore)]
    if ids.size == 0:
        return float("nan")
    _, counts = np.unique(ids, return_counts=True)
    return float(2.0 * np.sqrt(counts.mean() / np.pi))


def _apply_norm(radii: np.ndarray, K: np.ndarray, norm_length: float | None):
    """Rescale a (radii, K) pair into units of `norm_length`.

    K has units of area, so K scales by 1/d**2 while r scales by 1/d. Under this pair of
    rescalings Besag's L(r) - r transforms as (L(r) - r) / d, i.e. it stays a length and
    simply changes ruler -- which is what makes the normalised curve comparable to one
    computed from histology at a different physical resolution.

    Note the CSR test is INVARIANT to this: observed and simulated statistics rescale by
    the same factor, so the p-value is unchanged. Normalisation changes the reported
    magnitude, never the verdict.
    """
    if norm_length is None or not np.isfinite(norm_length) or norm_length <= 0:
        return radii, K
    return radii / norm_length, K / (norm_length ** 2)


def ripleys_k_points(
    field: np.ndarray,
    threshold: float,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    norm_length: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Ripley's K on supra-threshold lattice sites, treated as a point pattern.

    Border-corrected: only sites at least r from the domain edge act as centres.
    Equivalent to the mark-weighted estimator with all marks set to 1, so it shares the
    FFT neighbour count and needs no spatial-index library.

    `max_r` is always given in LATTICE units. `norm_length` (see `mean_cell_diameter`)
    rescales only the returned curve, so radii come back in units of that length.
    Returns (radii, K).
    """
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    binary = ((field > threshold) & m).astype(np.float64)
    if binary.sum() < 2:
        ny, nx = field.shape
        if max_r is None:
            max_r = min(ny, nx) / 4.0
        return _apply_norm(_radii(max_r, n_r), np.full(n_r, np.nan), norm_length)
    return ripleys_k_weighted(binary, max_r=max_r, n_r=n_r, mask=m,
                              norm_length=norm_length)


def ripleys_k_weighted(
    field: np.ndarray,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    norm_length: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Mark-weighted K: uses ECM mass directly, no threshold.

    K(r) = (1/(lam * W)) * sum_i w_i * (sum_{j != i, d<r} w_j),
    with lam the mean mass per site and W the total weight of the border-corrected centres.
    Computed by FFT convolution with a disc kernel, so it is O(N log N) per radius and fine
    on a lattice.
    """
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    f = np.where(m, field, 0.0)
    ny, nx = f.shape
    if max_r is None:
        max_r = min(ny, nx) / 4.0
    radii = _radii(max_r, n_r)

    total = f.sum()
    area = float(m.sum())
    if total <= 0:
        return _apply_norm(radii, np.full_like(radii, np.nan), norm_length)
    lam = total / area

    K = np.empty_like(radii)
    for i, r in enumerate(radii):
        neigh = _disc_convolve(f, r)
        inner = np.zeros_like(m)
        ri = int(np.ceil(r))
        inner[ri:ny - ri, ri:nx - ri] = True
        inner &= m
        w = f[inner]
        W = w.sum()
        if W <= 0:
            K[i] = np.nan
            continue
        # subtract each site's own mass from its neighbourhood sum
        K[i] = float((w * (neigh[inner] - w)).sum() / (W * lam))

    return _apply_norm(radii, K, norm_length)


def _disc_convolve(f: np.ndarray, r: float) -> np.ndarray:
    """Sum of f over a disc of radius r centred on each site, via FFT."""
    ri = int(np.ceil(r))
    yy, xx = np.mgrid[-ri:ri + 1, -ri:ri + 1]
    kernel = ((yy ** 2 + xx ** 2) <= r ** 2).astype(np.float64)

    ny, nx = f.shape
    sy, sx = ny + 2 * ri, nx + 2 * ri
    F = np.fft.rfft2(f, s=(sy, sx))
    Kf = np.fft.rfft2(kernel, s=(sy, sx))
    conv = np.fft.irfft2(F * Kf, s=(sy, sx))
    return conv[ri:ri + ny, ri:ri + nx]


def besag_l(radii: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Besag's variance-stabilised L(r) - r. Positive means clustered."""
    with np.errstate(invalid="ignore"):
        return np.sqrt(np.maximum(K, 0.0) / np.pi) - radii


# ---------------------------------------------------------------------------
# CSR envelope (the null the diffuse arm should sit inside)
# ---------------------------------------------------------------------------

def csr_envelope(
    field: np.ndarray,
    threshold: float,
    n_sim: int = 99,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Monte-Carlo envelope under complete spatial randomness, holding the number of
    supra-threshold sites fixed. This is the right null: it preserves total burden and
    randomises only arrangement, exactly the comparison the experiment is built on.

    Returns (radii, lo, hi) as pointwise 2.5/97.5 percentiles of L(r) - r.
    """
    rng = np.random.default_rng(seed)
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    n_pts = int(((field > threshold) & m).sum())
    idx = np.argwhere(m)

    curves = []
    for _ in range(n_sim):
        sim = np.zeros_like(field)
        pick = rng.choice(len(idx), size=min(n_pts, len(idx)), replace=False)
        sim[idx[pick][:, 0], idx[pick][:, 1]] = threshold + 1.0
        radii, K = ripleys_k_points(sim, threshold, max_r=max_r, n_r=n_r, mask=m)
        curves.append(besag_l(radii, K))

    arr = np.vstack(curves)
    return radii, np.nanpercentile(arr, 2.5, axis=0), np.nanpercentile(arr, 97.5, axis=0)


def csr_test(
    field: np.ndarray,
    threshold: float,
    n_sim: int = 99,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    seed: int = 0,
    norm_length: float | None = None,
) -> dict:
    """GLOBAL (rank-based) Monte-Carlo test against complete spatial randomness.

    Use this rather than checking whether the observed curve stays inside the pointwise
    2.5/97.5 envelope from `csr_envelope`. A pointwise envelope has a 5% exceedance rate
    *at each radius*, so across ~20 radii a genuinely random field escapes it most of the
    time -- the classic multiple-comparisons trap in Ripley's K, and it will make a
    correctly diffuse lesion look clustered.

    The statistic is the maximum absolute deviation of L(r) - r over the radius range,
    compared against the same statistic from `n_sim` CSR realisations. The p-value is
    rank-based and exact: p = (1 + #{sim >= obs}) / (1 + n_sim).
    """
    rng = np.random.default_rng(seed)
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    n_pts = int(((field > threshold) & m).sum())
    idx = np.argwhere(m)

    radii, K_obs = ripleys_k_points(field, threshold, max_r=max_r, n_r=n_r, mask=m,
                                    norm_length=norm_length)
    obs = float(np.nanmax(np.abs(besag_l(radii, K_obs))))

    sims = np.empty(n_sim)
    for s in range(n_sim):
        sim = np.zeros_like(field)
        pick = rng.choice(len(idx), size=min(n_pts, len(idx)), replace=False)
        sim[idx[pick][:, 0], idx[pick][:, 1]] = threshold + 1.0
        _, K = ripleys_k_points(sim, threshold, max_r=max_r, n_r=n_r, mask=m,
                                norm_length=norm_length)
        sims[s] = np.nanmax(np.abs(besag_l(radii, K)))

    p = (1.0 + int((sims >= obs).sum())) / (1.0 + n_sim)
    return {
        "max_abs_L_minus_r": obs,
        "csr_mean": float(sims.mean()),
        "csr_95th": float(np.percentile(sims, 95)),
        "p_value": p,
        "clustered": bool(p < 0.05),
    }


# ---------------------------------------------------------------------------
# Secondary descriptors
# ---------------------------------------------------------------------------

def patch_size_distribution(
    field: np.ndarray, threshold: float, mask: np.ndarray | None = None
) -> np.ndarray:
    """Sizes of 4-connected supra-threshold patches, descending.

    A focal lesion is a few large patches; a diffuse one is many small patches. Cheap,
    interpretable, and it is the quantity Cogno et al. (2022) were effectively reporting
    as ECM density histograms.
    """
    m = np.ones_like(field, dtype=bool) if mask is None else mask.astype(bool)
    binary = (field > threshold) & m
    labels = _label_4connected(binary)
    if labels.max() == 0:
        return np.array([], dtype=int)
    sizes = np.bincount(labels.ravel())[1:]
    return np.sort(sizes)[::-1]


def _label_4connected(binary: np.ndarray) -> np.ndarray:
    """Union-find connected components. Avoids a scipy.ndimage dependency."""
    ny, nx = binary.shape
    labels = np.zeros((ny, nx), dtype=np.int64)
    parent: dict[int, int] = {}

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    nxt = 1
    for y in range(ny):
        for x in range(nx):
            if not binary[y, x]:
                continue
            up = labels[y - 1, x] if y > 0 else 0
            left = labels[y, x - 1] if x > 0 else 0
            if up and left:
                labels[y, x] = min(up, left)
                union(up, left)
            elif up or left:
                labels[y, x] = up or left
            else:
                labels[y, x] = nxt
                parent[nxt] = nxt
                nxt += 1

    remap: dict[int, int] = {}
    out = np.zeros_like(labels)
    for y in range(ny):
        for x in range(nx):
            v = labels[y, x]
            if v:
                r = find(v)
                if r not in remap:
                    remap[r] = len(remap) + 1
                out[y, x] = remap[r]
    return out


def radial_profile(field: np.ndarray, epithelium_row: int) -> np.ndarray:
    """Mean ECM as a function of distance from the epithelial layer.

    Tests A9/A16 directly: deposition should peak immediately subepithelially and decay
    outward, not appear in the lumen. This is the Tier 1 sanity check.

    Returns a (2, ny) array: row 0 is the signed row offset from `epithelium_row` (negative
    on the lumen side), row 1 is the mean ECM at that offset.
    """
    ny = field.shape[0]
    offsets = np.arange(ny) - epithelium_row
    return np.vstack([offsets, field.mean(axis=1)])


# ---------------------------------------------------------------------------
# Condition comparison
# ---------------------------------------------------------------------------

@dataclass
class ConditionSummary:
    label: str
    n_replicates: int
    area_fraction_mean: float
    area_fraction_sd: float
    burden_mean: float
    max_L_minus_r_mean: float
    max_L_minus_r_sd: float
    largest_patch_frac_mean: float
    n_patches_mean: float


def summarise(
    fields: list[np.ndarray],
    label: str,
    threshold: float,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    norm_length: float | None = None,
) -> ConditionSummary:
    afs, burdens, maxls, bigpatch, npatch = [], [], [], [], []
    for f in fields:
        afs.append(area_fraction(f, threshold, mask))
        burdens.append(total_burden(f, mask))
        radii, K = ripleys_k_points(f, threshold, max_r=max_r, n_r=n_r, mask=mask,
                                    norm_length=norm_length)
        maxls.append(np.nanmax(besag_l(radii, K)))
        sizes = patch_size_distribution(f, threshold, mask)
        bigpatch.append(sizes[0] / sizes.sum() if sizes.size else np.nan)
        npatch.append(len(sizes))
    return ConditionSummary(
        label=label,
        n_replicates=len(fields),
        area_fraction_mean=float(np.nanmean(afs)),
        area_fraction_sd=float(np.nanstd(afs, ddof=1)) if len(afs) > 1 else 0.0,
        burden_mean=float(np.nanmean(burdens)),
        max_L_minus_r_mean=float(np.nanmean(maxls)),
        max_L_minus_r_sd=float(np.nanstd(maxls, ddof=1)) if len(maxls) > 1 else 0.0,
        largest_patch_frac_mean=float(np.nanmean(bigpatch)),
        n_patches_mean=float(np.nanmean(npatch)),
    )


def compare_conditions(
    focal_fields: list[np.ndarray],
    diffuse_fields: list[np.ndarray],
    threshold: float,
    max_r: float | None = None,
    n_r: int = 20,
    mask: np.ndarray | None = None,
    norm_length: float | None = None,
) -> dict:
    """The headline test.

    The model PASSES when the two arms separate on the spatial statistic while their
    collagen area fractions are statistically indistinguishable. Separating on area
    fraction instead means the injury patterns were not burden-matched and the experiment
    needs re-seeding, not reinterpreting.
    """
    a = summarise(focal_fields, "focal", threshold, max_r, n_r, mask, norm_length)
    b = summarise(diffuse_fields, "diffuse", threshold, max_r, n_r, mask, norm_length)

    def welch(m1, s1, n1, m2, s2, n2):
        """Welch t. Zero pooled SE is a real case here, not an error: the burden-matched
        design can make every replicate land on exactly the same area fraction. Identical
        means with zero spread is perfect agreement (t=0), not infinite disagreement."""
        if n1 < 2 or n2 < 2:
            return float("nan")
        se = np.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
        if se == 0:
            return 0.0 if np.isclose(m1, m2) else float("inf")
        return float((m1 - m2) / se)

    t_af = welch(a.area_fraction_mean, a.area_fraction_sd, a.n_replicates,
                 b.area_fraction_mean, b.area_fraction_sd, b.n_replicates)
    t_sp = welch(a.max_L_minus_r_mean, a.max_L_minus_r_sd, a.n_replicates,
                 b.max_L_minus_r_mean, b.max_L_minus_r_sd, b.n_replicates)

    burden_matched = abs(t_af) < 2.0
    spatially_separated = abs(t_sp) > 2.0

    if burden_matched and spatially_separated:
        verdict = "PASS: matched burden, separated spatial signature"
    elif not burden_matched:
        verdict = "INVALID: arms are not burden-matched; re-seed the injury patterns"
    else:
        verdict = "FAIL: no spatial separation; the CPM justification does not hold here"

    return {
        "focal": asdict(a),
        "diffuse": asdict(b),
        "t_area_fraction": t_af,
        "t_spatial": t_sp,
        "burden_matched": burden_matched,
        "spatially_separated": spatially_separated,
        "verdict": verdict,
        "norm_length": norm_length,
        "radius_units": "lattice sites" if not norm_length else "mean cell diameters",
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def self_test() -> bool:
    """Synthetic controls. Run before trusting this on real output: `--self-test`.

    Builds focal (few compact blobs) and diffuse (uniform random) fields with *identical*
    total burden, and checks the three outcomes that matter:
      1. burden-matched + clustered  -> PASS
      2. two diffuse arms            -> FAIL (must not invent separation)
      3. mismatched burden           -> INVALID (must not be reported as PASS)
    plus that the global CSR test calls diffuse random and focal clustered.
    """
    N, TOTAL = 100, 800

    def focal(seed):
        r = np.random.default_rng(seed)
        f = np.zeros((N, N))
        placed = 0
        while placed < TOTAL:
            cy, cx = r.integers(15, N - 15, 2)
            rad = r.integers(6, 10)
            yy, xx = np.mgrid[0:N, 0:N]
            new = ((yy - cy) ** 2 + (xx - cx) ** 2 <= rad ** 2) & (f == 0)
            idx = np.argwhere(new)[: TOTAL - placed]
            f[idx[:, 0], idx[:, 1]] = 1.0
            placed += len(idx)
        return f

    def diffuse(seed, total=TOTAL):
        r = np.random.default_rng(seed)
        f = np.zeros((N, N))
        f.ravel()[r.choice(N * N, total, replace=False)] = 1.0
        return f

    F = [focal(s) for s in range(5)]
    D = [diffuse(s) for s in range(100, 105)]
    kw = dict(threshold=0.5, max_r=20, n_r=10)

    checks = [
        ("focal vs diffuse -> PASS",
         compare_conditions(F, D, **kw)["verdict"].startswith("PASS")),
        ("diffuse vs diffuse -> FAIL",
         compare_conditions(D, [diffuse(s) for s in range(200, 205)], **kw)["verdict"].startswith("FAIL")),
        ("mismatched burden -> INVALID",
         compare_conditions(F, [diffuse(s, 1600) for s in range(300, 305)], **kw)["verdict"].startswith("INVALID")),
        ("CSR: diffuse not clustered",
         not csr_test(D[0], 0.5, n_sim=99, max_r=20, n_r=10, seed=7)["clustered"]),
        ("CSR: focal clustered",
         csr_test(F[0], 0.5, n_sim=99, max_r=20, n_r=10, seed=7)["clustered"]),
    ]
    ok = True
    for name, passed in checks:
        print(f"  [{'ok' if passed else 'FAIL'}] {name}")
        ok &= passed
    print("self-test:", "all passed" if ok else "FAILURES ABOVE")
    return ok


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--self-test", action="store_true",
                   help="run synthetic controls and exit")
    p.add_argument("--focal", nargs="+", help="glob(s) for focal-arm fields")
    p.add_argument("--diffuse", nargs="+", help="glob(s) for diffuse-arm fields")
    p.add_argument("--threshold", type=float, default=0.5,
                   help="ECM value above which a site counts as collagen-positive")
    p.add_argument("--max-r", type=float, default=None)
    p.add_argument("--n-r", type=int, default=20)
    p.add_argument("--mask", default=None, help="optional .npy tissue mask")
    p.add_argument("--cell-ids", default=None,
                   help="optional .npy lattice of CC3D cell IDs; sets --norm-length "
                        "automatically to the mean cell diameter")
    p.add_argument("--norm-length", type=float, default=None,
                   help="express radii in units of this length (see mean_cell_diameter). "
                        "Required for any comparison against histology, since A7 fixes no "
                        "lattice-to-um mapping.")
    p.add_argument("--out", default=None, help="write the result dict as JSON here")
    args = p.parse_args()

    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if not args.focal or not args.diffuse:
        raise SystemExit("--focal and --diffuse are required (or use --self-test)")

    def expand(pats):
        out = []
        for pat in pats:
            out.extend(sorted(glob.glob(pat)))
        if not out:
            raise SystemExit(f"no files matched: {pats}")
        return [load_field(q) for q in out]

    mask = np.load(args.mask).astype(bool) if args.mask else None
    norm = args.norm_length
    if args.cell_ids:
        norm = mean_cell_diameter(np.load(args.cell_ids))
        print(f"mean cell diameter = {norm:.3f} lattice sites; radii normalised by it")
    res = compare_conditions(expand(args.focal), expand(args.diffuse),
                             args.threshold, args.max_r, args.n_r, mask, norm)

    print(json.dumps(res, indent=2))
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(res, fh, indent=2)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
