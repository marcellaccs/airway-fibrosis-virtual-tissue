# Signal generation options for the tissue layer (ODE → CC3D)

Design options for the v1 interface, written against the published full model
(`model/ode/supplementary.ipynb` cell 21, JTB supplementary, Figure 17) and the v1 scope in
`docs/model_assumptions_for_slides.md` (A7–A18).

Status: proposal. Nothing here is decided yet. §1 reports two numerical findings that do bear on
A11 and A14: the interface signal **saturates** rather than drifting, and the antioxidant
intervention moves the damage and M2 channels in **opposite directions**.

## 1. What the ODE actually offers

State variables, all dimensionless fractions of carrying capacity `K = 1`:

| Symbol | Meaning | Behaviour under recurring exposure |
|---|---|---|
| `Eh`, `Ed` | healthy / damaged epithelium | `Ed` rises to a plateau set by `e3·WS` vs `e4` |
| `M1`, `M2` | recruited macrophages | `M1` spikes per meal, decays; `M2` accumulates |
| `M0R`, `M1R`, `M2R` | resident macrophages | slow, `WS`-dependent proliferation |
| `P` | pro-inflammatory | spikes per meal, τ = 1/`m7` = 25 |
| `A` | anti-inflammatory | ratchets up, floor set by `k_c` = 0.0125 |

Exposure is `WS ∈ {0,1}` on a `time % 24` schedule (three meals: 8–9, 13–14, 18–19), so
**the ODE time unit is hours** and the published runs (`t` = 0–200) cover about 8 days.

Derived quantities available for coupling, none of which require touching the ODE:

- `f_d = Ed / (Eh + Ed)` — fraction of epithelium damaged. Your seeding signal.
- `M2_tot = M2 + M2R`, `M1_tot = M1 + M1R` — polarization pools.
- `A`, `P`, and bounded combinations of them.
- `∫WS dt`, `∫M2_tot dt`, `∫A dt` — cumulative burden clocks.

### Repair-term parameter numbering: real, but benign (checked numerically 2026-08-04)

An earlier draft of this doc claimed the repair term was a blocking bug. **It is not.** Quantified
with `model/ode/repair_term_check.py` (pure-Python RK4, no tellurium needed), the effect on every
quantity we care about is under 2%, and on `f_d` it is essentially zero. The published results
stand. What follows is recorded so nobody re-derives the alarm later.

**What is actually inconsistent.** `Ed'` carries the repair term as
`e4*(1 + e8*(M2+M2R) + e9*A)*Ed`, matching the declared comments (`e8` = M2 enhancement, `e9` = A
enhancement). `Eh'` carries it as `e4*(1 + e9*(M2+M2R) + e10*A)*Ed` in all three full-model cells,
i.e. the older numbering in which `e9` = M2 and `e10` = A. That line was never renumbered when
`e8` was inserted ahead of it. So repair leaves `Ed` under one parameterisation and arrives in
`Eh` under another.

Cell 23 (Figure 18, antioxidant scans) is **fully consistent**: it uses the old numbering on both
lines, never introduces `e8` (left at 0.0), and the scan code sets `r.e9`/`r.e10` accordingly.

**Why it does not matter.** `Ed'` is the correct line, and `Ed` sits at a quasi-steady value
`≈ e3·WS·Eh / (e2 + e4·out_fac)`. The mismatch perturbs `Eh` only, the logistic proliferation term
`e1·(Eh+Ed)·(1 − (Eh+Ed)/K)` absorbs the perturbation, and `Eh` and `Ed` shift together, so the
*ratio* is preserved almost exactly:

| | `f_d` published | `f_d` balanced | rel. diff | `Eh+Ed` rel. diff |
|---|---|---|---|---|
| cell 21 params, t = 200 | 0.08562 | 0.08544 | 0.21% | 0.51% |
| cell 21 params, t = 4000 | 0.11414 | 0.11414 | 0.00% | 0.68% |

Cell 25 (Figure 22) samples `e8` and `e9` independently over (1, 100), so it is where a large
imbalance could appear. Tested at the corners:

| `e8` | `e9` | `f_d` rel. diff | `Eh+Ed` rel. diff |
|---|---|---|---|
| 50 | 2 | 0.00% | 1.71% |
| 2 | 50 | 0.02% | 0.98% |
| 100 | 1 | 0.02% | 1.83% |
| 1 | 100 | 0.04% | 1.01% |

Worst case across the sampled range: 1.8% on total epithelium, 0.04% on `f_d`. **`f_d` is safe to
use as the tissue-layer damage signal as published.** Renumbering the `Eh'` line is a tidy-up for
readability, not a correction.

### Two genuine errors, both in working notebooks rather than the published one

Neither affects `supplementary.ipynb`, which is the JTB artifact and the copy of record.

- **`e8`, `e9`, `e10` used but never declared** in `Full model.ipynb` cells 4, 6 and 7. Those cells
  cannot have produced valid output. Cell 9 declares them.
- **Unparseable copy-paste error** in `Full model parameter scans.ipynb` cell 2:
  `Eh' = ... + e4*(1 + e9*(M2+M2R) + e10*A)*Ed + e9*(M2 + M2R) + e10*A)*Ed`. The fragment is
  duplicated and the parentheses do not balance.

Recommend deleting or clearly marking both notebooks as superseded scratch, and treating
`supplementary.ipynb` as the single source of the model. **`supplementary.ipynb` cell 21 is the
canonical full model for the tissue coupling** (Figure 17, baseline plus wood-smoke scenarios).

### The finding that does change the design

**The signal does not drift. It saturates.** Integrating cell 21 out to `t` = 4000 h (~24 weeks,
the A11 horizon) under the published three-meals-a-day schedule, cycle means are:

| cycle (day) | `f_d` | `M2_tot` | `A` | `A/(A+P)` |
|---|---|---|---|---|
| 0 | 0.0369 | 0.1998 | 0.342 | 0.227 |
| 2 | 0.0609 | 0.4995 | 0.970 | 0.645 |
| 7 | 0.0858 | 0.4528 | 0.956 | 0.714 |
| 27 | 0.1113 | 0.4464 | 0.950 | 0.694 |
| 83 | 0.1133 | 0.4464 | 0.950 | 0.692 |
| 165 | 0.1133 | 0.4464 | 0.950 | 0.692 |

`M2_tot` and `A` overshoot around day 2 and are flat to five decimals from about day 27. `f_d`
settles a little later, by about day 83, on the slower epithelial timescale (`1/e4` = 500 h ≈ 21
days). Over the second half of the run `M2_tot` moves −0.28% and `f_d` −0.65%. **There is no slow
upward drift at the remodeling horizon.**

This is expected in hindsight and it is structural, not a parameter accident: the exposure
schedule is exactly periodic and **the ODE contains no state variable that ratchets**. Every
species is a birth–death balance that relaxes to a periodic attractor. The published 200 h window
shows only the rising limb, which is why A11 reads it as "progressive M2 accumulation."

Three consequences, each of which simplifies the build:

1. **A11's principal technical risk largely evaporates.** There is no slow drift to homogenize.
   Average over one 24 h cycle at the attractor and the reduction is done. No averaging argument,
   no multi-scale asymptotics.
2. **The ODE→tissue interface is a constant per exposure scenario, not a time series.** `S_M2`,
   `R_fib` and `f_d` are three numbers per condition. The signal table in §5 is a handful of rows,
   not thousands.
3. **A14's "known failure mode" cannot happen by drift.** `S_M2` will not climb across the
   fibroblast differentiation threshold on its own, so the focal→diffuse transition has to be
   located by *scanning* `S_M2` (exposure intensity, schedule, antioxidant condition) rather than
   by running longer. That is a better experiment anyway: it is a controlled sweep instead of
   waiting for a threshold crossing.

And it confirms the fallback flagged in §4: **progression in the tissue layer must come from the
ECM field integrating a sustained source, not from a rising signal.** The collagen field is the
only ratchet in the coupled system. This is an independent argument for A14's burden-not-density
decision.

### The antioxidant intervention pushes the two channels in opposite directions

Running the cell 23 antioxidant scaling to the attractor:

| condition | `f_d` | `M2_tot` | `A` | `A/(A+P)` |
|---|---|---|---|---|
| baseline (untreated) | 0.1141 | 0.4558 | 0.955 | 0.684 |
| 5× pro down / 5× anti up | 0.0200 | 0.5363 | 2.434 | 0.974 |
| 10× / 10× | 0.0068 | 0.6062 | 3.894 | 0.992 |
| 20× / 20× | 0.0012 | 0.6252 | 6.786 | 0.998 |

Epithelial damage collapses by a factor of ~90, but `M2_tot` rises 37% and `A` rises sevenfold.
**Whether the antioxidant experiment makes fibrosis better or worse in the tissue layer depends
entirely on which signal the interface carries.** Damage seeding alone says strongly protective;
an `S_M2` pedestal alone says mildly profibrotic; a Hill gain on `A` says strongly profibrotic.

This is not a modelling artifact to be tuned away. It is the framing mismatch between the two
models made numerical: in the published ODE the endpoint is resolution of inflammation and
epithelial repair, so "more A, more M2" reads as recovery. In a fibrosis model "more A, more M2"
is the pathogenic direction (A-block: "persistent M2 dominance being pro-fibrotic"). Note also
that the intervention is *defined* in cell 23 as scaling anti-inflammatory production up, and it
scales the repair-enhancement parameters `e9`/`e10` up as well, so part of the `f_d` collapse is
by construction.

**This has to be resolved before the antioxidant experiment is run, because the interface choice
sets the sign of the headline result.** Options: (i) carry both channels and report the
decomposition honestly, which is the defensible move and makes the tension the finding; (ii)
redefine the intervention to reduce epithelial damage (`e3`) rather than boost anti-inflammatory
production, which matches "antioxidant" more literally; (iii) restrict the claim to the damage
channel and state the omission. Recommend (i), with (ii) as a second arm.

## 2. Options for the damage signal (your idea 1)

### Option A — `f_d` sets a target damaged fraction, placement rule sets the pattern

Each tissue update: compute target count `N_target = round(f_d · N_epithelial)`, compare to the
current count of `DAMAGED` cells, convert the difference.

The important consequence: **the placement rule is not an implementation detail, it is the
independent variable of the headline experiment.** A7/A18 already commit us to "at matched total
injury, does focal vs diffuse damage change the lesion?" — that experiment *is* two placement
rules driven by the same `f_d`:

- *Diffuse arm*: choose conversion targets uniformly at random over the epithelium.
- *Focal arm*: seed `k` foci once at `t = 0`, then convert preferentially among neighbours of
  already-damaged cells (probability ∝ number of damaged neighbours, or a fixed radius).

Both arms consume identical ODE output, so total injury is matched by construction and
`spatial_stats.py` scores the difference. This is the cleanest version of the design.

**One trap to avoid.** A pure "location randomizer" re-drawn each step makes damage flicker: the
set of damaged cells is resampled, so the growth-factor source jumps around and never establishes
a stable focus. Fix: make `DAMAGED` a **persistent per-cell state** with transition
*probabilities* tuned so the population mean tracks `f_d`, rather than re-drawing membership.
Concretely, per epithelial cell per step, `P(healthy → damaged) = max(0, (f_d − f_current)/(1 − f_current))`
and the symmetric repair probability. Cheap, and it preserves focus identity.

**Decide explicitly whether cell *number* is conserved.** The ODE lets `Eh + Ed` fall. A9/A16
geometry needs an intact epithelial sheet bordering the lumen. Recommend v1 holds the epithelial
cell count fixed and uses only the *ratio* `f_d`; denudation and epithelial loss are a v2 feature
(and are entangled with EMT, deferred under A17).

### Option B — two-way coupling, tissue `f_d` written back into the ODE

Your note ends "then update the ODE with the new % damaged." Recommend **not** in v1, for a
specific reason rather than a general one: under A13/A17 nothing in the v1 tissue layer changes
epithelial damage. There is no EMT, no mechanical feedback, no macrophage killing. So the tissue's
damaged count would be a resampled copy of the ODE's own `Ed`, fed back in as if it were new
information. Worse, overwriting `Ed` each tissue step replaces the ODE's integration of `Ed` with
an externally imposed value, which breaks the cycle-averaging argument in A11 (you cannot average
a fast variable over a cycle and simultaneously overwrite it from the slow layer).

Write down the criterion for when it becomes worth doing, so it is a decision and not an
oversight: **two-way coupling earns its cost as soon as the tissue layer contains a mechanism that
changes epithelial damage independently of the ODE.** That is EMT (v2), stiffness-driven epithelial
stress, or epithelial cell loss. Any one of those makes the return path carry information.

## 3. Options for the fibrotic drive (your idea 2, plus the recruitment field)

### Option C — additive uniform pedestal `S_M2` (current A14/A15)

`S_M2 = s0 · ⟨M2_tot⟩_cycle`, added to every lattice site of the growth-factor field. Gives the
two orthogonal controls A14 is built on: `S_M2` sets how close the whole wall is to tipping, the
damage pattern sets where it tips first. Requires explicit decay `λ` (a uniform source with no
decay diverges) and Neumann lateral boundaries.

### Option D — multiplicative gain on cell-based secretion (your A/P scaling idea)

`secretion_rate = k_cell · ρ`, where `ρ` is a polarization scalar. Preserves spatial structure,
directly implements "polarization balance as the master signal."

**Do not use raw `A/P`.** `P` decays to near zero between meals (τ = 25 h) while `A` ratchets up,
so the ratio is unbounded and spikes on the gaps in the exposure schedule, not on the exposure.
Use a bounded form. Two candidates:

- `ρ = A / (A + P + ε)` ∈ [0,1] — keeps the competitive reading of the A/P idea.
- `ρ = ⟨A⟩ⁿ / (H^n + ⟨A⟩ⁿ)` — a Hill function of cycle-averaged `A`, matching the idiom used
  everywhere else in the ODE, and monotone by construction.

Recommend the Hill form for v1 and the ratio form as a sensitivity check, because a
non-monotone driver would make the focal-to-diffuse threshold hard to interpret.

### Option E — do both, and make additive-vs-multiplicative a parameter scan

This is the suggestion I would push hardest. The two are separable in one field equation:

```
∂G/∂t = D∇²G − λG + S_M2 + ρ·( k_E·1[damaged epithelium] + k_F·1[fibroblast] )
```

Setting `ρ = const` recovers pure Option C; setting `S_M2 = 0` recovers pure Option D. A14
currently commits to additive for v1 and calls multiplicative the v2 refinement, but the extra
implementation cost of carrying both is roughly one multiplication. Doing so converts a
commitment into a measurable: does the tipping-point behaviour survive when the M2 contribution
is co-located with cells instead of homogenised? That is the complementary-experiment argument
A14 already makes against Islam et al. (2023), made *within* one build rather than across two.

### Option F — fibroblast recruitment, three variants

A15 currently specifies `R_fib` as a scalar boundary influx rate. Three ways to spend it:

1. **Uniform influx (A15 as written).** New fibroblasts appear at random sites in the
   subepithelial compartment at rate `R_fib`. Simplest, no new machinery.
2. **GF-biased placement.** Place new fibroblasts with probability ∝ local `G`. No new field, no
   new PDE, one line of code. Gives spatially focal recruitment for free.
3. **Separate recruitment/chemokine field.** A distinct field sourced by damaged epithelium and an
   M1-derived scalar, with fibroblasts chemotaxing up it. Biologically this is the PDGF/CXCL arm,
   genuinely distinct from TGF-β (You et al., 2023; Nguyen et al., 2024). Costs a second PDE solve
   and about three new parameters.

Recommend **(2) for v1**. It changes *where* recruits land, not *how many*, so the A15 interface
contract stays exactly two scalars and the "highest-value reusable artifact" claim survives
intact. Variant (3) is a clean v2 addition and is also the natural home for the bidirectional
fibroblast–macrophage loop flagged as an open question in the assumptions doc.

Note that (1) vs (2) vs a fixed pool with no recruitment is a three-arm experiment on whether
`R_fib` earns its place at all, scored against Hoshino et al. (1998), rs = 0.88 between
subepithelial thickness and fibroblast number. A null result there is publishable.

## 4. The timescale question, and a way around it

A11 calls the ODE-to-tissue timescale reduction the principal technical risk. Sharpening it:

The published runs stop at `t` = 200 h; the Li et al. (2024) 4-week vs 24-week gap needs roughly
`t` = 4000 h. §1 now answers what happens in between: **the signal saturates by about day 27 and
`f_d` by about day 83.** So the reduction is simpler than A11 anticipated.

- Options C and D take a **constant** `S_M2` and `ρ` per exposure scenario, read off the
  attractor. No ramp, no drift, no averaging argument.
- Progression comes from the ECM field integrating that constant source. **The collagen field is
  the only ratchet in the coupled system.**
- A `∫M2_tot dt` burden clock is still the right *framing* for A15's "cumulative exposure", but
  with a saturating integrand it reduces to `S_M2 · t`, i.e. a linear clock. Worth writing it as
  an integral anyway so a non-periodic exposure schedule drops in without restructuring.

The one thing that *would* restore genuine drift is a slowly accumulating state in the ODE
(senescence, irreversible epithelial loss, a fibroblast pool that grows). None exists today. If
the 24-week progression needs to come from the signal rather than from the ECM integrator, that is
the ODE-side change to make, and it is a v2 question.

Verified with `model/ode/repair_term_check.py`, which reimplements cell 21 in pure Python (RK4,
`dt` = 0.005, converged: changing `dt` by 4× moves `f_d` by 7e-7). Runs in the sandbox with no
tellurium and no scipy, so it is usable for quick interface sweeps without touching the `cc3d` or
`tox-ode` environments. Confirm against Tellurium host-side before anything goes in a manuscript.

**One schedule quirk found while reimplementing.** No event covers `0 <= time % 24 < 8`, so on the
first day `WS` keeps its initial value of 1.0 for the first 8 hours: the simulation opens with an
unintended 8-hour continuous exposure before the three-meal pattern starts. On later days `WS` is
switched off at `time % 24` = 19 and nothing turns it on until 8, so those days are correct. It
affects the transient, not the attractor, so nothing above changes, but the Figure 17 opening
transient is not the intended dosing.

## 5. How the signal physically reaches CC3D

Two routes, and the choice has a practical consequence.

**Route 1 — precomputed lookup table (recommended for v1).** Run the ODE once host-side, export
`data/processed/ode_signal_table.csv` with one row per exposure cycle: `cycle, f_d, S_M2, R_fib,
rho`. The steppable reads the CSV at `start()` and indexes it by cycle. Advantages:

- **No Tellurium in the `cc3d` environment.** `CLAUDE.md` explicitly warns that installing extra
  packages into `cc3d` can break libRoadRunner and force a reinstall. This route never touches it.
- Parameter scans over tissue parameters do not re-solve the ODE.
- Runs are exactly reproducible from a committed artifact, and the CSV is small enough to track.
- The signal is inspectable and plottable before a single CC3D step is run.

**Route 2 — live SBML inside CC3D.** `add_free_floating_antimony(...)` plus `timestep_sbml()`.
Already demonstrated to work in `model/cc3d/M1_M2_antimony/Simulation/TelluriumSteppables.py`, so
this is a proven path, not a gamble. It is the required route the moment two-way coupling
(Option B) arrives.

Recommend Route 1 for v1 with the steppable written against a `get_signal(cycle)` accessor, so
swapping in Route 2 later is a one-function change rather than a rewrite.

## 6. Three further options worth a moment

- **Per-region deposition instead of uniform `WS`.** Make exposure spatially non-uniform (PM
  deposits preferentially at bifurcations and impaction sites). This would make the focal arm
  *mechanistic* rather than stipulated, which is a materially stronger answer to "why is the
  damage clustered?" Costs a deposition submodel. Flag as v2, but it is the most attractive v2
  item on this list.
- **Threshold vs graded fibroblast differentiation.** A14 assumes a concentration threshold. Keep
  it for v1 precisely because it makes the focal-to-diffuse transition sharp and locatable; a
  graded Hill response smears the very quantity we are trying to measure. State it as a posit.
- **Latent vs active growth factor as a gate on `S_M2`.** The assumptions doc keeps the activation
  term separable for exactly this. If the pedestal is written as `S_M2 = a(G_ECM) · s0 · ⟨M2_tot⟩`
  with `a ≡ 1` in v1, the stiffness feedback loop drops in later with no restructuring.

## 7. Suggested v1 stack

1. Signal source: a small CSV of **attractor values, one row per exposure/treatment scenario**
   (Route 1), not a per-cycle time series. §1 shows the signal is constant after ~day 27.
2. Damage: `f_d` → persistent per-cell `DAMAGED` state, with the placement rule as the
   focal/diffuse experimental arm (Option A).
3. Drive: single growth-factor field carrying both an additive pedestal and a multiplicative gain
   (Option E), with `ρ` a Hill function of `A`.
4. Recruitment: scalar `R_fib` from the interface, GF-biased placement (Option F.2).
5. Coupling direction: one-way, with the Option B trigger condition written into the assumptions.
6. Progression: from the ECM field integrating a sustained source. The collagen field is the
   ratchet; the signal is not.
7. Focal→diffuse threshold: located by **scanning** `S_M2` across scenarios, not by running longer.
8. Readout: collagen burden field → area fraction and Ripley's K via `model/analysis/spatial_stats.py`.

This keeps the A15 interface at exactly two scalars plus one bounded gain, which is still small
enough to be the reusable artifact the deck claims it is. If anything the saturation result makes
it a stronger artifact: the interface is a lookup table with a handful of rows.

## Open items

- **Decide how the antioxidant experiment is defined and which channels the interface carries.**
  This sets the sign of the headline result (§1). Blocking for the intervention experiment,
  not for the build.
- Renumber the `Eh'` repair term for readability (cosmetic, changes results by <2%).
- Delete or mark superseded: `Full model.ipynb`, `Full model parameter scans.ipynb`. Two of the
  errors in §1 live only there.
- Decide whether the epithelial cell count is conserved in the tissue layer (recommend yes for v1).
- Confirm the saturation result against Tellurium host-side before it goes in a manuscript;
  `repair_term_check.py` is an independent reimplementation, which is a check but not a proof.
- Consider whether the opening 8-hour exposure quirk (§4) should be fixed in the published events.
- Citation needed for spatially non-uniform PM deposition in small airways, to support the §6
  per-region exposure option. Not yet in `literature/references.bib`.
