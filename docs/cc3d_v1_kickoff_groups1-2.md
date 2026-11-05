# Kickoff brief: CC3D v1, Groups 1 and 2

> **Historical, 2026-08-08.** Every path below names `model/cc3d/Subepithelial_Fibrosis-02/`,
> which is no longer the working copy. Work moved to `model/cc3d/subepithelial_fibrosis_draft/` on
> 2026-08-08 and that is the committed project. Current status is in `docs/cc3d_v1_todo.md`.

Handoff document for starting implementation in Claude Code. Self-contained: assumes no
prior conversation context. Full task list is in `docs/cc3d_v1_todo.md`; this covers only
Groups 1 and 2, which must land before the ODE coupling.

## Opening prompt to paste

```
Read docs/cc3d_v1_kickoff_groups1-2.md, then CLAUDE.md, then the cc3d-expert skill
in .claude/skills/. Implement Group 1 in model/cc3d/Subepithelial_Fibrosis-02/,
running the model after each change to verify. Stop and show me the results before
starting Group 2.
```

## What this model is

A Cellular Potts model of subepithelial fibrosis in the small airway, the initiating
lesion of biomass-smoke airway remodeling. A published ODE model of the innate immune
response will supply signals to this spatial tissue layer. The headline experiment: at
matched total epithelial injury, does **focal** versus **diffuse** damage placement change
the resulting fibrotic lesion?

Layer order, outer to inner (assumption A16): fixed outer boundary, subepithelial
compartment (fibroblasts, myofibroblasts, ECM), epithelium, lumen.

Files:

- `model/cc3d/Subepithelial_Fibrosis-02/Simulation/Subepithelial_Fibrosis.xml`
- `model/cc3d/Subepithelial_Fibrosis-02/Simulation/Subepithelial_FibrosisSteppables.py`
- `model/cc3d/Subepithelial_Fibrosis-02/Simulation/Subepithelial_Fibrosis.py` (registration)

Design authority, in order of precedence:

1. `docs/model_assumptions_for_slides.md` (assumptions A7 through A18, with citations)
2. `docs/model_spec_v1_v2.md` (component and property spec)
3. `docs/ode_tissue_coupling_options.md` (the coupling design, needed for Group 2)
4. `docs/Hackathon_Lightning_Talk_-_Subepithelial_Fibrosis.pptx.pdf` slides 8, 9, 10

## Already done, do not redo

The contact energy matrix was corrected in a previous session. Damaged and healthy
epithelium now have identical mechanics, and only secretion differs. Verified interfacial
tensions, using `gamma(A,B) = J(A,B) - (J(A,A) + J(B,B))/2`:

| Interface | Healthy | Damaged |
| --- | --- | --- |
| vs Fibroblast | 29 | 29 |
| vs Myofibroblast | 37 | 37 |
| vs Medium | 19 | 19 |

Also already applied: `TARGET_VOLUME_EPITHELIAL = 48`, which now matches the seeded 8x6
footprint, and `G` secretion reduced from 0.15 to 0.01 so the field's steady state is
about 1 rather than 15.

There is **no** `Freeze` anywhere in `model/`. A collaborator's version froze the
epithelium; that approach was rejected. See the decision note in Group 1 below.

## Group 1: mechanics and sheet integrity

Goal: the epithelial sheet stays continuous for a full 20,000 MCS run without being
frozen, while remaining deformable so that subepithelial ECM accumulation can push it
inward.

**Decision on record: do not freeze the epithelium.** Freezing removes the inward
thickening readout that slide 10 item 9 requires, contradicts A17's argument that EMT is
"loss of adhesion plus gain of motility" and is the reason a Cellular Potts model was
chosen over a point-agent ABM, and converts barrier integrity from a result into an
assumption. Freeze the outer boundary only, as slide 8 specifies.

Tasks:

1. Add per-type `FluctuationAmplitude` inside the `Potts` block: 2 for both epithelial
   types, 10 for Fibroblast, 6 for Myofibroblast. Cold epithelium, warm mesenchyme.
2. Add `ConnectivityGlobal` with penalty 1000000 for both epithelial types.
3. Add `ChemotactTowards="Medium,Fibroblast,Myofibroblast"` and `SaturationCoef="1.0"` to
   both `ChemotaxisByType` entries. Rationale: even with G normalized, chemotaxis delivers
   roughly 79 energy units per pixel against an adhesion barrier of 29, so cells can still
   push through. `ChemotactTowards` removes the chemotactic term for copies into
   epithelium while leaving mechanical pushing intact, which is the distinction we want.
4. Decide myofibroblast chemotaxis explicitly. Lambda is currently 120, inherited rather
   than chosen. `model_spec_v1_v2.md` gives myofibroblasts "reduced motility" and assigns
   the chemotaxis coefficient to fibroblasts only. Propose 0 or about 20 and record the
   choice in the lab notebook.
5. Wire up the surface constraint. `SurfaceLocalFlex` is declared in the XML and
   `LAMBDA_SURFACE_EPITHELIAL = 1.0` is defined in Python, but nothing ever sets
   `cell.targetSurface` or `cell.lambdaSurface`, so the plugin is inert. Set
   `cell.targetSurface = cell.surface` in `start()` after seeding rather than hardcoding a
   perimeter, because tracked surface depends on `NeighborOrder=2`. Do not change these
   values on damage.
6. Set `J(EpithelialHealthy, EpitheliumDamaged)` to 2, currently 5. A gamma of 3 at that
   interface coarsens damage patches and would bias the Ripley's K spatial statistic that
   A18 relies on.
7. Add the frozen outer boundary, which is missing entirely. New cell type
   `<CellType TypeName="OuterBoundary" TypeId="5" Freeze=""/>`, a wall at y = 96 to 99,
   contact energies for the new type against all others, no secretion, no response. Needed
   before Group 3 recruitment (slide 10 item 5 recruits across it) and before thickening
   can be directed inward.

Acceptance criteria:

- Sheet is visually continuous at MCS 0, 1000, and 20000.
- `n_Eh + n_Ed` is constant across the whole run.
- No epithelial cell fragments into disconnected pieces.
- Fibroblasts accumulate beneath the epithelium rather than inside it.

## Group 2: make phenotype transitions spatial

Goal: both transitions respond to local field concentration instead of firing on a timer.

The problem, quantified. Both transitions are ungated integrators with a floor set by the
placeholder constants `TGFB_LEVEL = 0.10`, `PRO_INFLAMMATORY_LEVEL = 0.10`,
`M2_LEVEL = 0.20`:

- Damage floor is `0.010*TGFB + 0.005*PRO` = 0.0015/MCS, so all 25 epithelial cells cross
  `DAMAGE_THRESHOLD = 0.85` together at about MCS 567.
- Activation floor is `0.02 * (0.35*TGFB + 0.20*M2)` = 0.0015/MCS, so all 80 fibroblasts
  reach full activation by about MCS 667.

Everything converts, everywhere, on a schedule, regardless of G. This defeats the
focal-versus-diffuse hypothesis before the ODE is attached, so attaching `f_d` and `S_M2`
to the current code would produce identical output no matter what the ODE says.

Tasks:

1. Gate fibroblast differentiation on local G. `FIB_TO_MYOF_G_THRESHOLD = 0.45` is defined
   and never referenced. Use it, and remove the constant `TGFB_LEVEL` and `M2_LEVEL` terms
   from `activation_signal` so local G decides.
2. Replace the continuous damage accumulator with binary state plus probability. Slide 9
   specifies a binary damage state; slide 8 specifies that the ODE damaged fraction maps to
   a per-cell transition probability. Follow `ode_tissue_coupling_options.md` section 2
   Option A: `P(healthy -> damaged) = max(0, (f_d - f_current) / (1 - f_current))`, with
   `DAMAGED` as a persistent per-cell state rather than resampled membership, so foci keep
   their identity. Retire the `DAMAGE_THRESHOLD` and `REPAIR_THRESHOLD` hysteresis.
3. Implement focal and diffuse placement rules as the experiment's independent variable.
   Diffuse: uniform random over the epithelium. Focal: seed k foci at t = 0, then convert
   preferentially among neighbours of already-damaged cells, with probability proportional
   to the count of damaged neighbours.
4. Normalize C at point of use. The ECM field is secretion 0.08 over decay 0.0005, so it
   reaches about 160 at steady state, which pins `repair_rate = 0.0085 - 0.010*C` at zero
   and makes damage permanently irreversible. Keep the field itself as burden, per the A14
   decision of 2026-08-02, and apply `C_norm = C / (C + K_C)` in `repair_rate`,
   `migration_factor`, and the `lambdaVolume` scalings.

Acceptance criteria:

- Zeroing every field prevents phenotype conversion entirely. If cells still convert on
  schedule, the gating is not working. This is the decisive test.
- Focal and diffuse arms produce measurably different spatial statistics at matched total
  injury, via `model/analysis/spatial_stats.py`.
- Damaged cells can return to healthy when local ECM burden is low.

## Verification

Per `CLAUDE.md`, always pass an explicit output directory. A bare run writes a timestamped
folder into the working directory that matches no `.gitignore` rule.

```
conda activate cc3d
python -c "import cc3d; print(cc3d.__version__)"
python -m cc3d.run_script -i model/cc3d/Subepithelial_Fibrosis-02/Subepithelial_Fibrosis.cc3d \
    --output-dir results/cc3d/v1-group1
```

Diagnostics worth adding while working, then keeping:

- Print field min, max and mean every 100 MCS. Assumed magnitudes have been wrong twice.
- Assert epithelial cell count conservation each step.
- Print `cell.volume`, `cell.targetVolume`, `cell.surface`, `cell.targetSurface` for one
  epithelial cell at MCS 0 to confirm the constraints are actually set.

## Repo conventions

- Read the most recent file in `lab-notebook/` before starting.
- Write today's entry at `lab-notebook/YYYY/YYYY-MM-DD.md` from `lab-notebook/TEMPLATE.md`,
  recording the CC3D version, decisions made (especially task 4 of Group 1), commands run,
  and results.
- Commit small and often, straight to `main`, present-tense imperative messages that say
  why. For example `gate fibroblast differentiation on local GF so the lesion is spatial`.
- Never commit `results/`, article PDFs, or large files from `data/raw`.
- The `cc3d-expert` skill in `.claude/skills/` carries CC3D syntax, energy-budget
  reasoning, and debugging recipes. Its `references/signaling-networks.md` covers the ODE
  coupling patterns needed for Group 3.

## Known items deliberately deferred

Not part of Groups 1 and 2, already captured in `docs/cc3d_v1_todo.md`:

- The three ODE interface hooks: `f_d` wiring, the `S_M2` uniform pedestal, `R_fib`
  recruitment (Group 3).
- Missing fibroblast and myofibroblast GF secretion (Group 3).
- Lumen and interstitium are both `Medium`, so lumen narrowing cannot yet be measured
  (Group 3).
- Dead code: `migration_factor` computed but never used, `wall_stress` never written,
  `EPITHELIAL_REPAIR_THRESHOLD` and `ECM_HIGH_THRESHOLD` unused, `deposit_ecm` duplicating
  the XML secretion and scanning all 20,000 lattice sites per cell (Group 4).
- A stray zero-byte `.probe` file in `.claude/skills/cc3d-expert/` to delete.
