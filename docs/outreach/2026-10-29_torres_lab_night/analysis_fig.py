"""Proposed-analysis handout: the same measurements on a real trichrome section and on a model frame.

usage: python analysis_fig.py <zou_fig4_png> <model_vtk> <out_png>

Top row: Zou et al. 2014 Fig 4 panels (a) control and (c) wood smoke (CC BY 4.0), with
  - collagen (trichrome blue) mask in a 60 um band around the lumen -> collagen area fraction
  - wall thickness along 24 rays from the lumen centroid -> median (IQR)
Bottom row: model frame (cells + collagen burden) with the same two readouts, and Ripley's K
  for myofibroblast centres against complete spatial randomness.
"""
import sys, re
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else ".")
from make_frames import parse_vtk, COL, LUMEN_MIN_Y, UM_PER_PX

# ---------------- histology ----------------
def panel_crops(fig4):
    """Panels a (control) and c (wood smoke) of the trichrome row, insets masked out."""
    w, h = fig4.size
    # panel boxes measured on the 3142x2156 PLOS image (fractions of width/height)
    boxes = {"control": (0.030, 0.027, 0.340, 0.300), "wood smoke": (0.681, 0.027, 0.993, 0.300)}
    out = {}
    for k, (x0, y0, x1, y1) in boxes.items():
        im = fig4.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))).convert("RGB")
        a = np.asarray(im).astype(float)
        inset = np.zeros(a.shape[:2], bool)
        hh, ww = inset.shape
        inset[: int(0.53 * hh), int(0.55 * ww):] = True  # the high-magnification inset box
        out[k] = (a, inset)
    return out


def scale_bar_px(a):
    """Length in px of the black 50 um scale bar in the bottom-left of a panel (longest dark horizontal run)."""
    hh, ww, _ = a.shape
    sub = a[int(0.85 * hh):, : int(0.3 * ww)].mean(axis=2) < 60
    best = 0
    for row in sub:
        run = 0
        for v in row:
            run = run + 1 if v else 0
            best = max(best, run)
    return best


def collagen_mask(a):
    """Trichrome blue/cyan: blue channel dominant over red, not too dark, not white."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (b > r + 25) & (b > 90) & ((r + g + b) < 690)


def lumen_mask(a, inset):
    bright = (a.min(axis=2) > 225) & ~inset
    lab, n = ndi.label(bright)
    hh, ww = bright.shape
    # the lumen is the bright component containing the panel's central region
    cy, cx = hh // 2, ww // 2
    best, bestsize = 0, 0
    for i in range(1, n + 1):
        comp = lab == i
        size = comp.sum()
        if size > bestsize and comp[int(0.3 * hh):int(0.7 * hh), int(0.3 * ww):int(0.7 * ww)].any():
            best, bestsize = i, size
    lum = lab == best
    lum = ndi.binary_fill_holes(lum)
    return lum


def wall_thickness(a, lum, inset, px_per_um, n_rays=24):
    """Along rays from the lumen centroid: distance from the lumen edge to the first run of open space."""
    hh, ww = lum.shape
    cy, cx = ndi.center_of_mass(lum)
    open_space = (a.min(axis=2) > 225)
    tissue = ~open_space
    res = []
    segs = []
    for th in np.linspace(0, 2 * np.pi, n_rays, endpoint=False):
        dx, dy = np.cos(th), np.sin(th)
        r = 0.0
        # march out of the lumen
        while True:
            x, y = int(round(cx + r * dx)), int(round(cy + r * dy))
            if not (0 <= x < ww and 0 <= y < hh):
                break
            if not lum[y, x]:
                break
            r += 1
        r0 = r
        if not (0 <= x < ww and 0 <= y < hh) or inset[y, x]:
            continue
        gap = 0
        while True:
            x, y = int(round(cx + r * dx)), int(round(cy + r * dy))
            if not (0 <= x < ww and 0 <= y < hh) or inset[y, x]:
                r = None
                break
            gap = gap + 1 if open_space[y, x] else 0
            if gap >= 10:
                r = r - gap
                break
            r += 1
        if r is None:
            continue
        t = (r - r0) / px_per_um
        res.append(t)
        segs.append(((cx + r0 * dx, cy + r0 * dy), (cx + r * dx, cy + r * dy)))
    return np.array(res), segs, (cx, cy)


def analyze_panel(a, inset, band_um=60, px_per_um=None):
    bar = scale_bar_px(a)
    if px_per_um is None:
        px_per_um = bar / 50.0 if bar > 40 else 1.76
    lum = lumen_mask(a, inset)
    dist = ndi.distance_transform_edt(~lum)
    band = (dist > 0) & (dist <= band_um * px_per_um) & ~inset
    col = collagen_mask(a) & band
    caf = col.sum() / band.sum()
    th, segs, c = wall_thickness(a, lum, inset, px_per_um)
    return dict(px_per_um=px_per_um, lumen=lum, band=band, collagen=col, caf=caf, thick=th, segs=segs, centre=c, bar=bar)


# ---------------- model ----------------
def ripley_k(points, area_w, area_h, radii):
    n = len(points)
    if n < 3:
        return np.zeros_like(radii)
    d = np.sqrt(((points[:, None, :] - points[None, :, :]) ** 2).sum(-1))
    A = area_w * area_h
    K = []
    for r in radii:
        K.append(A / (n * (n - 1)) * ((d < r).sum() - n))
    return np.array(K)


def model_panel(vtk):
    arrs = parse_vtk(vtk)
    ct = arrs["CellType"].astype(int); cid = arrs["CellId"].astype(int); C = arrs["C"]
    rgb = np.zeros(ct.shape + (3,), float)
    for t, c in COL.items():
        rgb[ct == t] = c
    cn = C / (C + 20.0)
    sub = (ct == 0) & (np.arange(ct.shape[0])[:, None] < LUMEN_MIN_Y)
    a = np.where(sub, np.clip(cn * 2.2, 0, 0.85), 0)[..., None]
    rgb = rgb * (1 - a) + np.array([196, 150, 40]) * a
    # readouts
    coll_px = (sub & (cn > 0.05))
    subepi_rows = slice(4, 72)
    band_px = sub[subepi_rows].sum() + ((ct[subepi_rows] == 3) | (ct[subepi_rows] == 4)).sum()
    caf = coll_px[subepi_rows].sum() / band_px
    # wall thickness per column: from the wall top (row 4) to the bottom of the epithelial sheet
    th = []
    for x in range(ct.shape[1]):
        col = ct[:, x]
        epi = np.nonzero((col == 1) | (col == 2))[0]
        if epi.size:
            th.append((epi.min() - 4) * UM_PER_PX)
    th = np.array(th)
    # myofibroblast centres for Ripley's K
    pts = []
    for i in np.unique(cid[ct == 4]):
        ys, xs = np.nonzero(cid == i)
        pts.append((xs.mean(), ys.mean()))
    pts = np.array(pts) if pts else np.zeros((0, 2))
    return np.flipud(rgb).astype(np.uint8), caf, th, pts, ct


def main():
    fig4_path, vtk, out = sys.argv[1:4]
    fig4 = Image.open(fig4_path)
    panels = panel_crops(fig4)
    # one scale bar (50 um, panel a) serves the whole row: same magnification per the legend
    a0, i0 = panels["control"]
    ppu = scale_bar_px(a0) / 50.0
    res = {k: analyze_panel(a, ins, px_per_um=ppu) for k, (a, ins) in panels.items()}
    img, caf_m, th_m, pts, ct = model_panel(vtk)
    mcs = int(re.search(r"(\d+)\.vtk$", vtk).group(1))

    fig = plt.figure(figsize=(16, 11), dpi=150)
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.0], hspace=0.32, wspace=0.18)
    for j, k in enumerate(panels):
        a, ins = panels[k]; r = res[k]
        ax = fig.add_subplot(gs[0, j])
        ax.imshow(a.astype(np.uint8))
        ov = np.zeros(a.shape[:2] + (4,))
        ov[r["band"]] = (1, 1, 0, 0.12)
        ov[r["collagen"]] = (0, 0.35, 1, 0.75)
        ax.imshow(ov)
        for (p0, p1) in r["segs"][::2]:
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#e76f51", lw=1.6)
        hh, ww = a.shape[:2]
        ax.add_patch(Rectangle((int(0.55 * ww), 0), ww - int(0.55 * ww), int(0.53 * hh), fill=True, color="white", alpha=0.85, lw=0))
        ax.text(0.57 * ww, 0.06 * hh, "inset masked", fontsize=8, color="#666")
        med, q1, q3 = np.median(r["thick"]), np.percentile(r["thick"], 25), np.percentile(r["thick"], 75)
        ax.set_title(f"Rat small airway, {k} (7 months)\nMasson's trichrome; Zou et al. 2014 Fig 4, CC BY 4.0", fontsize=10)
        ax.text(0.02, 0.03, f"collagen area fraction, 60 µm band: {100*r['caf']:.0f}%\n"
                            f"wall thickness along rays: {med:.0f} µm (IQR {q1:.0f}–{q3:.0f}), n = {len(r['thick'])}",
                transform=ax.transAxes, fontsize=9.5, va="bottom", bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))
        ax.set_xticks([]); ax.set_yticks([])
    # top-right: explanation
    ax = fig.add_subplot(gs[0, 2]); ax.axis("off")
    ax.text(0, 1, "How the overlays are made", fontsize=13, weight="bold", va="top")
    ax.text(0, 0.9, ("1. Find the airway lumen: the large bright region\n   in the middle of the field.\n"
                     "2. Draw a 60 µm band around it (pale yellow):\n   that is the airway wall we score.\n"
                     "3. Collagen = trichrome blue pixels inside the\n   band (blue overlay). Area fraction = blue / band.\n"
                     "4. Wall thickness = distance from the lumen edge\n   to the first open air space, along rays\n   (orange lines). Report the median and IQR.\n"
                     "5. Scale from the 50 µm bar in each panel.\n\n"
                     "The same four numbers come out of the model\n(below) by counting pixels, so model and tissue\ncan be compared on equal terms.\n\n"
                     "These overlays are a demonstration of the method\non a published figure, not a re-analysis of the\nstudy; Zou et al. report their own morphometry."),
            fontsize=10.5, va="top", linespacing=1.45)

    # bottom-left: model frame
    ax = fig.add_subplot(gs[1, :2])
    ax.imshow(img, interpolation="nearest", aspect="equal")
    ax.axhline(100 - LUMEN_MIN_Y, color="#1f4e79", lw=1, ls="--")
    ax.text(2, 100 - LUMEN_MIN_Y - 2, "lumen at day 0", fontsize=8, color="#1f4e79")
    days = mcs * 62.4 / 86400
    ax.set_title(f"Virtual tissue, day {days:.1f} (step {mcs:,}); 1 px = 1.25 µm, 250 × 125 µm shown", fontsize=10)
    ax.text(0.01, 0.04, f"collagen area fraction, subepithelial band: {100*caf_m:.0f}%\n"
                        f"wall thickness (outer wall to lining): {np.median(th_m):.0f} µm (IQR {np.percentile(th_m,25):.0f}–{np.percentile(th_m,75):.0f})\n"
                        f"myofibroblasts: {len(pts)}; damaged epithelial cells: {len(np.unique(ct[ct==2]))}",
            transform=ax.transAxes, fontsize=9.5, va="bottom", bbox=dict(facecolor="white", alpha=0.9, edgecolor="none"))
    ax.set_xticks([]); ax.set_yticks([])

    # bottom-right: Ripley's K
    ax = fig.add_subplot(gs[1, 2])
    radii = np.linspace(2, 60, 30)
    K = ripley_k(pts, 200, 68, radii)
    L = np.sqrt(K / np.pi) - radii
    rng = np.random.default_rng(1)
    env = []
    for _ in range(199):
        q = np.column_stack([rng.uniform(0, 200, len(pts)), rng.uniform(4, 72, len(pts))])
        Kq = ripley_k(q, 200, 68, radii)
        env.append(np.sqrt(Kq / np.pi) - radii)
    env = np.array(env)
    ax.fill_between(radii * UM_PER_PX, np.percentile(env, 2.5, 0), np.percentile(env, 97.5, 0), color="#cbd5e1", label="same number of cells placed at random (95% band)")
    ax.plot(radii * UM_PER_PX, L, color="#8e44ad", lw=2.2, label="myofibroblasts in this frame")
    ax.set_xlabel("distance r (µm)"); ax.set_ylabel("L(r) − r   (above the grey band = clustered)")
    ax.set_title("Ripley's K on myofibroblast centres", fontsize=10)
    ax.legend(fontsize=8, loc="upper left")
    fig.suptitle("Proposed analysis: the same measurements on a real section and on the virtual tissue", fontsize=15, weight="bold", y=0.98)
    fig.savefig(out, bbox_inches="tight")
    print("saved", out, {k: (round(100 * r["caf"], 1), round(float(np.median(r["thick"])), 1), r["bar"]) for k, r in res.items()}, "model", round(100 * caf_m, 1), round(float(np.median(th_m)), 1), len(pts))


if __name__ == "__main__":
    main()
