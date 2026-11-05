"""
Diagnostic: compare the published Eh' repair term against the balanced form.

Background
----------
The full model appears in three cells of `supplementary.ipynb`:
    cell 21 -> Figure 17 (baseline + wood-smoke scenarios)
    cell 23 -> Figure 18 (antioxidant parameter scans)
    cell 25 -> Figure 22 (Latin hypercube sampling)

`Ed'` carries the repair term as  e4*(1 + e8*(M2+M2R) + e9*A)*Ed  in cells 21 and 25,
i.e. e8 = M2 enhancement, e9 = A enhancement (the "new" numbering, matching the
parameter comments and the LHS ranges in cell 25).

`Eh'` carries it as  e4*(1 + e9*(M2+M2R) + e10*A)*Ed  in ALL THREE cells, i.e. the
"old" numbering in which e9 = M2 and e10 = A. That line was never renumbered when e8
was inserted ahead of it.

Cell 23 is unaffected because it uses the old numbering consistently on both lines
and never introduces e8 (e8 = 0.0, unused). Cells 21 and 25 are internally
inconsistent: repair leaves Ed under one parameterisation and arrives in Eh under
another, so epithelial cells are not conserved across the repair transition.

This script integrates the cell-21 system in pure Python (no tellurium, no scipy)
under both the published and the balanced Eh' line and reports the divergence in
f_d = Ed/(Eh+Ed), the signal proposed for tissue-layer damage seeding.

Run:  python model/ode/repair_term_check.py
"""

BASE = dict(
    e1=0.0315, e2=0.0001, e3=0.005, e4=0.002, e5=0.1, e6=0.2,
    He1=0.2, He2=0.2, ne1=4, ne2=4,
    m1=50.0, m2=0.1, m4=0.02, m5=0.05, m6=0.2, m7=0.04,
    m8=0.1, m9=0.04, m10=0.04,
    Hm1=0.25, Hm2=0.05, Hm3=0.9, Hm4=1.2,
    nm1=2.5, nm2=4, nm3=2, nm4=2,
    k_c=0.0125, K=1.0, m11=0.2, m3=0.07, smr=0.1, mumr=0.05,
    # cell 21 values
    e8=1.0,    # M2 enhancement of repair
    e9=1.0,    # A enhancement of repair
    e10=0.0,   # declared "baseline A production by healthy epithelial cells"
)

# Species order: Eh, Ed, M1, M2, M0R, M1R, M2R, P, A
Y0 = [1.0, 0.0, 0.001, 0.001, 0.0, 0.0, 0.001, 0.0, 0.0]
NAMES = ["Eh", "Ed", "M1", "M2", "M0R", "M1R", "M2R", "P", "A"]


def ws(t, honor_initial=True):
    """Wood-smoke schedule from the Antimony events (three meals a day).

    Note a quirk of the published events: no trigger covers 0 <= t%24 < 8, so on the
    first day WS retains its initial value of 1.0 for the first 8 hours. Later days
    are switched off at t%24 = 19 and stay off until t%24 = 8. `honor_initial`
    reproduces that unintended opening 8-hour exposure.
    """
    if honor_initial and t < 8.0:
        return 1.0
    h = t % 24.0
    if 8.0 <= h < 9.0 or 13.0 <= h < 14.0 or 18.0 <= h < 19.0:
        return 1.0
    return 0.0


def hill(x, h, n):
    xn = x ** n
    return xn / (h ** n + xn)


def deriv(t, y, p, balanced, honor_initial=True):
    Eh, Ed, M1, M2, M0R, M1R, M2R, P, A = y
    W = ws(t, honor_initial)

    # repair factor as it leaves Ed (correct under the declared parameter comments)
    out_fac = 1.0 + p["e8"] * (M2 + M2R) + p["e9"] * A
    # repair factor as it arrives in Eh
    in_fac = out_fac if balanced else 1.0 + p["e9"] * (M2 + M2R) + p["e10"] * A

    total_E = Eh + Ed
    dEh = (p["e1"] * total_E * (1.0 - total_E / p["K"]) - p["e2"] * Eh
           - p["e3"] * W * Eh + p["e4"] * in_fac * Ed)
    dEd = -p["e2"] * Ed + p["e3"] * W * Eh - p["e4"] * out_fac * Ed

    RM1 = p["m1"] * hill(P, p["Hm1"], p["nm1"]) + p["m11"] * W
    RM2 = p["m2"] * hill(A, p["Hm2"], p["nm2"]) + p["k_c"]
    denom = p["mumr"] + RM1 + RM2

    a_act = hill(A, p["Hm2"], p["nm2"])
    p_act = hill(P, p["Hm1"], p["nm1"])
    a_inh3 = p["Hm3"] ** p["nm3"] / (A ** p["nm3"] + p["Hm3"] ** p["nm3"])
    a_inh4 = p["Hm4"] ** p["nm4"] / (A ** p["nm4"] + p["Hm4"] ** p["nm4"])

    dM1 = W * (p["smr"] * RM1) / denom - p["m5"] * a_act * M1 - p["m4"] * M1
    dM2 = W * (p["smr"] * RM2) / denom + p["m5"] * a_act * M1 - p["m4"] * M2

    totR = M0R + M1R + M2R
    dM0R = (-p["m1"] * p_act * M0R - p["m2"] * a_act * M0R
            + p["m3"] * W * (M1R + M2R) * (1.0 - totR / p["K"]) - p["m4"] * M0R)
    dM1R = p["m1"] * p_act * M0R - p["m5"] * a_act * M1R - p["m4"] * M1R
    dM2R = p["m2"] * a_act * M0R + p["m5"] * a_act * M1R - p["m4"] * M2R

    dP = (p["e5"] * W * hill(Eh, p["He1"], p["ne1"])
          + p["e6"] * W * hill(Ed, p["He2"], p["ne2"])
          + p["m6"] * W * a_inh3 * (M1 + M1R) - p["m7"] * P)
    dA = (p["m8"] * a_inh3 * (M2 + M2R) + p["m9"] * a_inh4 * (M1 + M1R)
          - p["m10"] * A + p["k_c"])

    return [dEh, dEd, dM1, dM2, dM0R, dM1R, dM2R, dP, dA]


def integrate(t_end, dt, p, balanced, honor_initial=True, sample_every=1.0):
    y = list(Y0)
    t = 0.0
    out = [(0.0, list(y))]
    next_sample = sample_every
    n = int(round(t_end / dt))
    for _ in range(n):
        k1 = deriv(t, y, p, balanced, honor_initial)
        y2 = [y[i] + 0.5 * dt * k1[i] for i in range(9)]
        k2 = deriv(t + 0.5 * dt, y2, p, balanced, honor_initial)
        y3 = [y[i] + 0.5 * dt * k2[i] for i in range(9)]
        k3 = deriv(t + 0.5 * dt, y3, p, balanced, honor_initial)
        y4 = [y[i] + dt * k3[i] for i in range(9)]
        k4 = deriv(t + dt, y4, p, balanced, honor_initial)
        y = [y[i] + (dt / 6.0) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
             for i in range(9)]
        t += dt
        if t >= next_sample:
            out.append((t, list(y)))
            next_sample += sample_every
    return out


def summarize(traj, label):
    t, y = traj[-1]
    Eh, Ed = y[0], y[1]
    fd = Ed / (Eh + Ed) if (Eh + Ed) > 0 else float("nan")
    print(f"  {label:22s} t={t:7.1f}  Eh={Eh:.5f}  Ed={Ed:.5f}  "
          f"Eh+Ed={Eh+Ed:.5f}  f_d={fd:.5f}  M2+M2R={y[3]+y[6]:.5f}  A={y[8]:.5f}")
    return fd, Eh + Ed, y[3] + y[6], y[8]


def cycle_means(traj, period=24.0):
    """Mean of f_d, M2_tot, A and A/(A+P) over each 24 h exposure cycle."""
    cyc = {}
    for t, y in traj:
        c = int(t // period)
        Eh, Ed, P, A = y[0], y[1], y[7], y[8]
        fd = Ed / (Eh + Ed) if (Eh + Ed) > 0 else 0.0
        m2 = y[3] + y[6]
        rho = A / (A + P) if (A + P) > 0 else 0.0
        cyc.setdefault(c, []).append((fd, m2, A, rho))
    return {c: tuple(sum(v[i] for v in vals) / len(vals) for i in range(4))
            for c, vals in sorted(cyc.items())}


if __name__ == "__main__":
    print("Step-size convergence check (t=200, published Eh'):")
    prev = None
    for dt in (0.01, 0.005, 0.0025):
        tr = integrate(200.0, dt, BASE, balanced=False)
        fd, tot, m2, a = summarize(tr, f"dt={dt}")
        if prev is not None:
            print(f"      -> change in f_d vs previous dt: {abs(fd - prev):.2e}")
        prev = fd

    dt = 0.005
    print("\n=== t = 200 (the published simulation window) ===")
    pub200 = integrate(200.0, dt, BASE, balanced=False)
    bal200 = integrate(200.0, dt, BASE, balanced=True)
    fdp, totp, _, _ = summarize(pub200, "published Eh'")
    fdb, totb, _, _ = summarize(bal200, "balanced Eh'")
    print(f"  f_d relative difference : {abs(fdp - fdb) / fdb * 100:.2f}%")
    print(f"  Eh+Ed relative diff     : {abs(totp - totb) / totb * 100:.2f}%")

    print("\n=== t = 4000 (~24 weeks, the A11 horizon) ===")
    pub4k = integrate(4000.0, dt, BASE, balanced=False)
    bal4k = integrate(4000.0, dt, BASE, balanced=True)
    fdp4, totp4, m2p4, ap4 = summarize(pub4k, "published Eh'")
    fdb4, totb4, m2b4, ab4 = summarize(bal4k, "balanced Eh'")
    print(f"  f_d relative difference : {abs(fdp4 - fdb4) / fdb4 * 100:.2f}%")
    print(f"  Eh+Ed relative diff     : {abs(totp4 - totb4) / totb4 * 100:.2f}%")

    print("\n=== Does the signal keep drifting? (balanced, cycle means) ===")
    cm = cycle_means(bal4k)
    print(f"  {'cycle':>6} {'day':>5} {'f_d':>10} {'M2_tot':>10} {'A':>10} {'A/(A+P)':>10}")
    keys = sorted(cm)
    for c in [k for k in keys if k in (0, 1, 2, 4, 7, 13, 27, 55, 83, 111, 139, 165)]:
        fd, m2, a, rho = cm[c]
        print(f"  {c:6d} {c:5d} {fd:10.5f} {m2:10.5f} {a:10.5f} {rho:10.5f}")
    last = cm[keys[-1]]
    mid = cm[keys[len(keys) // 2]]
    print(f"\n  M2_tot change over the second half of the run: "
          f"{(last[1] - mid[1]) / mid[1] * 100:+.2f}%")
    print(f"  f_d    change over the second half of the run: "
          f"{(last[0] - mid[0]) / mid[0] * 100:+.2f}%")
