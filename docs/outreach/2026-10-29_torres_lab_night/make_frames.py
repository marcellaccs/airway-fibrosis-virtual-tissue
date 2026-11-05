"""Render CC3D VTK snapshots of the subepithelial-fibrosis model into annotated PNG frames.

usage: python make_frames.py <LatticeData dir> <out dir> [--every N] [--scale S]

Each frame: left panel = cells (type colours, cell outlines, collagen burden tinted in the
subepithelial space); right panel = growth-factor field G. A header strip carries the clock
(MCS -> days at 62.4 s/MCS) and the live readouts (lumen area, cell counts).
"""
import sys, os, re, glob, csv, argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFont

UM_PER_PX = 1.25
S_PER_MCS = 62.4
NX, NY = 200, 100
LUMEN_MIN_Y = 80

# cell-type colours (RGB)
COL = {
    0: (247, 250, 253),   # Medium / lumen
    1: (111, 190, 160),   # EpithelialHealthy  (green-teal)
    2: (232, 98, 60),     # EpitheliumDamaged  (orange-red)
    3: (74, 128, 196),    # Fibroblast         (blue)
    4: (142, 68, 173),    # Myofibroblast      (purple)
    5: (90, 90, 90),      # OuterBoundary      (dark grey)
}
NAMES = {1: "healthy epithelium", 2: "damaged epithelium", 3: "fibroblast", 4: "myofibroblast", 5: "outer wall"}
COLLAGEN = np.array([196, 150, 40], dtype=float)  # amber tint for C in the subepithelial space


def parse_vtk(path):
    """Parse the ASCII structured-points VTK that CC3D writes. Returns dict name -> (NY, NX) array."""
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"DIMENSIONS\s+(\d+)\s+(\d+)\s+(\d+)", txt)
    nx, ny, nz = map(int, m.groups())
    n = nx * ny * nz
    out = {}
    for mm in re.finditer(r"\n(\w+)\s+(\d+)\s+(\d+)\s+(unsigned_char|int|float|double|long|short)\s*\n", txt):
        name, ncomp, ntup, typ = mm.group(1), int(mm.group(2)), int(mm.group(3)), mm.group(4)
        if ntup != n:
            continue
        start = mm.end()
        # grab exactly ncomp*ntup numbers after the header
        vals = np.fromstring(txt[start:start + 32 * ncomp * ntup], sep=" ", count=ncomp * ntup)
        if vals.size != ncomp * ntup:
            # slower fallback
            toks = txt[start:].split()[: ncomp * ntup]
            vals = np.array([float(t) for t in toks])
        out[name] = vals.reshape(ny, nx) if ncomp == 1 else vals.reshape(ny, nx, ncomp)
    return out


def lumen_area(ct):
    """Open airway above the sheet: Medium pixels counted from the top of each column down to the first cell."""
    total = 0
    for x in range(ct.shape[1]):
        col = ct[::-1, x]  # top row first
        nz = np.nonzero(col)[0]
        total += int(nz[0]) if nz.size else col.size
    return total


def render(arrs, mcs, scale, font, font_small, lumen0):
    ct = arrs["CellType"].astype(int)
    cid = arrs["CellId"].astype(int)
    G = arrs.get("G", np.zeros_like(ct, dtype=float))
    C = arrs.get("C", np.zeros_like(ct, dtype=float))

    # ---------- left panel: cells ----------
    rgb = np.zeros((NY, NX, 3), dtype=float)
    for t, c in COL.items():
        rgb[ct == t] = c
    # collagen burden tint on Medium pixels of the subepithelial space (y < LUMEN_MIN_Y)
    cnorm = C / (C + 20.0)   # the model's own saturating c_norm
    alpha = np.clip(cnorm * 2.2, 0, 0.85)
    mask = (ct == 0) & (np.arange(NY)[:, None] < LUMEN_MIN_Y)
    a = np.where(mask, alpha, 0.0)[..., None]
    rgb = rgb * (1 - a) + COLLAGEN * a
    # cell outlines: pixel whose right or upper neighbour belongs to a different cell
    edge = np.zeros((NY, NX), dtype=bool)
    edge[:, :-1] |= (cid[:, :-1] != cid[:, 1:]) & ((ct[:, :-1] > 0) | (ct[:, 1:] > 0))
    edge[:-1, :] |= (cid[:-1, :] != cid[1:, :]) & ((ct[:-1, :] > 0) | (ct[1:, :] > 0))
    rgb[edge] = rgb[edge] * 0.55
    left = Image.fromarray(np.flipud(rgb).astype(np.uint8)).resize((NX * scale, NY * scale), Image.NEAREST)

    # ---------- right panel: growth-factor field ----------
    g = np.clip(G / 4.0, 0, 1)
    # white -> amber -> deep red colour ramp
    ramp = np.array([[250, 250, 250], [253, 212, 120], [227, 110, 45], [140, 20, 30]], dtype=float)
    idx = g * (len(ramp) - 1)
    lo = np.floor(idx).astype(int)
    hi = np.minimum(lo + 1, len(ramp) - 1)
    frac = (idx - lo)[..., None]
    grgb = ramp[lo] * (1 - frac) + ramp[hi] * frac
    grgb[ct == 5] = (90, 90, 90)
    grgb[(ct == 1) | (ct == 2)] = grgb[(ct == 1) | (ct == 2)] * 0.5 + np.array(COL[1]) * 0.5
    grgb[ct == 2] = np.array(COL[2])
    grgb[edge & ((ct == 3) | (ct == 4))] = grgb[edge & ((ct == 3) | (ct == 4))] * 0.5
    right = Image.fromarray(np.flipud(grgb).astype(np.uint8)).resize((NX * scale, NY * scale), Image.NEAREST)

    # ---------- compose ----------
    pad = 2 * scale
    header = int(13 * scale)
    footer = int(9 * scale)
    W = 2 * NX * scale + 3 * pad
    H = header + NY * scale + footer
    img = Image.new("RGB", (W, H), (255, 255, 255))
    img.paste(left, (pad, header))
    img.paste(right, (2 * pad + NX * scale, header))
    d = ImageDraw.Draw(img)

    days = mcs * S_PER_MCS / 86400.0
    la = lumen_area(ct)
    pct = 100.0 * (la - lumen0) / lumen0
    n = {t: len(np.unique(cid[ct == t])) for t in (1, 2, 3, 4)}

    d.text((pad, int(1.5 * scale)), f"Day {days:4.1f} of 14.4   (MCS {mcs:,})", fill=(30, 30, 30), font=font)
    d.text((pad, int(7.5 * scale)),
           f"Lumen area {pct:+.1f}%    healthy {n[1]}  damaged {n[2]}  fibroblasts {n[3]}  myofibroblasts {n[4]}",
           fill=(70, 70, 70), font=font_small)
    d.text((2 * pad + NX * scale, int(1.5 * scale)), "Growth-factor field G (TGF-\u03b2-like)", fill=(30, 30, 30), font=font)
    d.text((2 * pad + NX * scale, int(7.5 * scale)), "pale = low,  dark red = high;  fibroblasts climb this gradient",
           fill=(70, 70, 70), font=font_small)

    # legend in footer
    y = header + NY * scale + int(2 * scale)
    x = pad
    for t in (1, 2, 3, 4):
        d.rectangle([x, y, x + int(4 * scale), y + int(4 * scale)], fill=COL[t], outline=(60, 60, 60))
        d.text((x + int(5 * scale), y - int(0.5 * scale)), NAMES[t], fill=(50, 50, 50), font=font_small)
        x += int(5 * scale) + int(len(NAMES[t]) * 2.6 * scale) + int(4 * scale)
    d.rectangle([x, y, x + int(4 * scale), y + int(4 * scale)], fill=tuple(int(v) for v in COLLAGEN), outline=(60, 60, 60))
    d.text((x + int(5 * scale), y - int(0.5 * scale)), "collagen (ECM) burden", fill=(50, 50, 50), font=font_small)
    note = f"airway lumen at top;  1 px = {UM_PER_PX} \u00b5m,  1 MCS = {S_PER_MCS} s"
    tw = d.textlength(note, font=font_small)
    d.text((W - pad - tw, y - int(0.5 * scale)), note, fill=(50, 50, 50), font=font_small)
    return img, dict(mcs=mcs, day=round(days, 3), lumen_px=la, lumen_pct=round(pct, 2),
                     n_healthy=n[1], n_damaged=n[2], n_fib=n[3], n_myo=n[4],
                     meanG_sub=round(float(G[4:LUMEN_MIN_Y - 8].mean()), 4),
                     meanC_sub=round(float(C[4:LUMEN_MIN_Y - 8].mean()), 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lattice_dir"); ap.add_argument("out_dir")
    ap.add_argument("--every", type=int, default=1); ap.add_argument("--scale", type=int, default=6)
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.lattice_dir, "Step_*.vtk")), key=lambda p: int(re.search(r"(\d+)\.vtk$", p).group(1)))
    files = files[:: a.every]
    if a.max:
        files = files[: a.max]
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(4.6 * a.scale))
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", int(3.4 * a.scale))
    except Exception:
        font = font_small = ImageFont.load_default()
    rows = []
    lumen0 = None
    for i, f in enumerate(files):
        mcs = int(re.search(r"(\d+)\.vtk$", f).group(1))
        arrs = parse_vtk(f)
        if lumen0 is None:
            lumen0 = lumen_area(arrs["CellType"].astype(int))
        img, stats = render(arrs, mcs, a.scale, font, font_small, lumen0)
        img.save(os.path.join(a.out_dir, f"frame_{i:04d}.png"))
        rows.append(stats)
        if i % 25 == 0:
            print(i, f, stats)
    with open(os.path.join(a.out_dir, "frame_stats.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print("frames:", len(rows), "size:", img.size)


if __name__ == "__main__":
    main()
