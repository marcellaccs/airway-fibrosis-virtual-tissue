# Connecting the Tellurium ODE to CC3D, step by step

How Route 2 of `docs/ode_tissue_coupling_options.md` §5 was implemented for
`model/cc3d/subepithelial_fibrosis_draft/` (2026-08-08) — the ODE integrating
inside CC3D every MCS via `libRoadRunner`, instead of Route 1's frozen
precomputed scalar. **Status: working and verified over a full 20,000-MCS run.**
`ODESignalSteppable` loads `TISSUE_SIGNAL_MODEL` and drives the `S_M2` pedestal
from it live. Getting here took two real numerical fixes beyond the basic
wiring — both documented below, because they're the part worth remembering.

## 1. Find the real model, don't retype it

The canonical model is `model/ode/supplementary.ipynb` **cell 21** (per
`docs/ode_tissue_coupling_options.md` §1). Extracted with a small Python
script that parses the notebook JSON and prints one cell's source —
`model/ode/repair_term_check.py` is a *reimplementation* used for cross-checks,
not the source of truth, and it uses a "balanced" parameter numbering that
differs slightly from the published one. Copy-paste from the notebook, don't
transcribe from the Python version.

## 2. Copy the Antimony string in verbatim, published numbering and all

`Subepithelial_FibrosisSteppables.py`'s `TISSUE_SIGNAL_MODEL` is the notebook's
`model = '''...'''` string — same 9 species (`Eh, Ed, M1, M2, M0R, M1R, M2R, P,
A`), same parameters. Includes the known real (but `docs/ode_tissue_coupling_options.md`
§1: "safe to use as published", <2% effect) numbering mismatch between `Eh'`
and `Ed'`'s repair terms — kept as published rather than "corrected," because
fidelity to the canonical model mattered more here than the tidy-up. The one
piece *not* copied verbatim is the `WS` exposure schedule — see step 6.

## 3. Decide the MCS-to-hours conversion — the one real design decision

`docs/model_assumptions_for_slides.md` A7 leaves this uncommitted for v1 in
general. For this specific coupling it can't stay uncommitted, because
`step_size` (how much ODE time one MCS advances) has to be a number. Chose
`ODE_STEP_SIZE = 1.0` (1 MCS = 1 ODE hour): simplest possible ratio, and with
20,000 MCS that integrates to t=20,000h (~833 days) — far past the ~83-day
point where `f_d` saturates (§1), so no risk of stopping mid-transient.

## 4. Load the model in `start()`

```python
self.add_free_floating_antimony(
    model_string=TISSUE_SIGNAL_MODEL,
    model_name='tissue_signal',
    step_size=ODE_STEP_SIZE
)
```
One shared instance, not per-cell — this is a well-mixed compartmental signal,
not a cell-local network (`.claude/skills/cc3d-expert/references/signaling-networks.md`).
Default integrator (`cvode`, adaptive-step) — no special options needed once
step 6's fix is in place.

## 5. Read the signal, apply it, then advance the clock — in that order

```python
def step(self, mcs):
    m2_tot = self.sbml.tissue_signal['M2'] + self.sbml.tissue_signal['M2R']
    s_m2 = S_M2_COEFFICIENT * m2_tot
    for x in range(self.dim.x):
        for y in range(self.dim.y):
            self.G[x, y, 0] += s_m2
    self.timestep_sbml()
```
`timestep_sbml()` last, always — read this MCS's value and use it before
advancing the ODE past it.

## 6. The `WS` exposure schedule: events don't work, a smooth sigmoid does — with a real overflow trap along the way

The published model turns wood-smoke exposure on and off with six discrete
Antimony `at` events (`E1`-`E6`, hard 0/1 jumps at `t%24 = 8, 9, 13, 14, 18,
19`). **Left as published, this breaks the live integration**, and fixing it
took two attempts:

**First failure — the discrete events themselves.** With the default adaptive
integrator (CVODE), a 1000-MCS smoke test failed immediately:
```
Error: CVODE Error: CV_CONV_FAILURE, ... At t = 32 and h = 2.01834e-96,
the corrector convergence test failed repeatedly or with |h| = hmin.
```
`t=32` is the second day's first meal event — the adaptive solver couldn't get
through the discontinuity. Tried tightening tolerance
(`self.set_sbml_global_options({'relative': 1e-10, 'absolute': 1e-12})`, the
skill's documented fix for "stiff models") — no change, identical failure at
the identical `t`. Tried fixed-step RK4 instead (matching what
`model/ode/repair_term_check.py` uses, for the same "discontinuous WS"
reason) — avoided the crash, but the model diverged to **NaN by MCS 500**,
because `repair_term_check.py` needed `dt=0.005` for RK4 stability against
`m1=50` (the fastest rate constant), and `ODE_STEP_SIZE=1.0` is ~200x coarser
than that.

**The actual fix — replace the events with a continuous rule.** Adaptive
implicit solvers like CVODE are built for stiffness (fast but continuous
dynamics), not genuine discontinuities. Six `at` events become one assignment
rule, same `:=` syntax the model already uses for its `RM1`/`RM2` helper
functions — one rising-minus-falling sigmoid pair per meal, all in `time%24`
so the pattern repeats every 24h:
```
WS := 1/(1+exp(-WS_STEEPNESS*(time%24-8)))  - 1/(1+exp(-WS_STEEPNESS*(time%24-9)))
    + 1/(1+exp(-WS_STEEPNESS*(time%24-13))) - 1/(1+exp(-WS_STEEPNESS*(time%24-14)))
    + 1/(1+exp(-WS_STEEPNESS*(time%24-18))) - 1/(1+exp(-WS_STEEPNESS*(time%24-19)))
```
(Antimony needs this on one line — a multi-line expression with leading
`+`/`-` continuations is a syntax error, unlike Python.)

**Second failure — steepness chosen too high overflowed `exp()`.** First try
used `WS_STEEPNESS=50`. New, *different* failure, even earlier: `CV_TOO_MUCH_ACC`
at t=4h — hours before any meal transition. Cause: `time%24` ranges over 24,
so `WS_STEEPNESS*24` is the largest argument `exp()` ever sees, and
`50*24=1200` is far past double precision's overflow point (~709). Each
sigmoid term still evaluated to a clean 0 or 1 (IEEE754 makes `1/(1+inf)=0`
well-defined), but the repeated `inf` intermediates apparently corrupted
CVODE's internal Jacobian/step-size estimation regardless of the visible
output being finite. **`WS_STEEPNESS=20`** (`20*24=480`, safely under the
overflow threshold) fixed it — clean run, no crash, no NaN.

The steepness choice is a real three-way tradeoff, not just "smaller is
safer": higher = closer to the true 1-hour square pulse but stiffer to
integrate; lower = easier to integrate but the pulse visibly widens/softens
and the delivered dose per meal shifts; and independent of both, there's a
hard numerical ceiling from `exp()` overflow that has nothing to do with the
model's biology. `WS_STEEPNESS=20` gives a ~0.29h (~18 min) transition against
a 1h pulse — softer than the `50` originally intended, but numerically clean.

## 7. Use a manual pixel loop for the field write, not a vectorized one

Both `np.array(field[:, :, 0])` (read) and `field[:, :, :] += value` (write)
**crash this CC3D 4.9.0 build's C++ backend** — confirmed by testing the write
form directly (5-MCS smoke test, same `-1073740791` exit code as the earlier
read-side crash). The double `for x / for y` loop is the only form verified
safe here, and it's a real cost: `ODESignalSteppable` (loop + live ODE
integration together) took 60% of total steppable runtime in the full run.

## 8. Order matters: register before the steppable that reads the field

In `Subepithelial_Fibrosis.py`, `ODESignalSteppable` is registered **before**
`FibrosisModelSteppable`. Steppables run in registration order within a
single MCS, and `FibrosisModelSteppable.read_local_fields()` reads each cell's
local `G` — registering the pedestal first means that read sees this MCS's
updated field, not last MCS's.

## 9. Verify before trusting it

- **Convergence**: halve `step_size`; if the trajectory barely moves, it's converged
  (this is what `repair_term_check.py` already did for the Python reimplementation).
- **Sanity check against the known number**: `M2_tot` read from the live model
  should sit near `M2_TOT_REFERENCE = 0.4464` once past the saturation horizon.
  Confirmed: `M2_tot=0.4498` at MCS 500 (~day 21, before full saturation),
  and it holds a **stable periodic band (0.4388-0.4558) from MCS 500 through
  MCS 19500** — the same six values repeat every 3000 MCS (an exact multiple
  of the 24h cycle), confirming a genuine periodic attractor rather than drift
  or noise.
- **Divergence/NaN**: cut `step_size` (or here, `WS_STEEPNESS`) before assuming
  anything else is wrong — this is what actually found the overflow bug in
  step 6.
- Printed every 500 MCS in `ODESignalSteppable.step()`: `WS=... M2_tot=...
  (reference attractor 0.4464) S_M2=...`.

## Full-run results (2026-08-08)

20,000 MCS, `results/cc3d/v1-route2/` (gitignored): **1750.9s (29m11s)**.
Sheet integrity clean (`fragmented=0, isolated=0`) at MCS 0, 1000, and 19999
(the true final MCS). Mesenchymal containment 0 throughout. No crash, no NaN,
no assertion failure across the full run. `M2_tot` in its periodic attractor
band as described above for the entire simulated ~833 days.

## Open items

- `f_d` / damage seeding is still untouched — this pass only wired `M2_tot`
  into the `S_M2` pedestal, deliberately, per the original scope ("the
  simplest connection... the M2_tot signal"). Wiring `f_d` into epithelial
  damage is Group 2 territory, already scoped and paused separately.
- The published vs. "balanced" `Eh'`/`Ed'` numbering choice (step 2) should be
  revisited if this ever needs to match a manuscript figure exactly.
- The smoothed `WS` (step 6) is a deliberate deviation from the published
  model, not just a numbering tidy-up. If a result ever needs to match the
  discrete-event version exactly, that's a real difference to account for,
  not just a numerical convenience.
- The manual pixel-loop performance cost (step 7) is unresolved — every
  vectorized alternative tried crashes. Tolerable at ~29 min/full-run, not
  free.
