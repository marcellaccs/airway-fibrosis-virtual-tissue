# ECM as a field vs. ECM as a cell type — basic assessment

Written 2026-08-14, after the lumen-diagnostic fix (see `cc3d_v1_todo.md` PRIORITY 0 and
the 2026-08-14 lab-notebook entry). Requested comparison: keep collagen/ECM as the current
non-diffusing field `C`, vs. re-implement it as a literal volume-occupying `CellType`, using
Chandrasegaran, Sluka & Shanley (2025, *PLOS Comput Biol* 21(4):e1012298,
`literature/cc3d_lit/Chandrasegaran et al. - 2025 - Modelling the spatiotemporal dynamics of
senescent....pdf`, code at
[github.com/Sharm8/Senescence_wound_healing_model](https://github.com/Sharm8/Senescence_wound_healing_model))
as the precedent for the cell-type route. That model is a directly comparable CC3D dermal
wound-healing/fibrosis model, peer-reviewed and calibrated against literature data via PSO —
this isn't a hypothetical pattern, it's a validated implementation in the same framework.

## What each model actually does with ECM

**This model (v1, current).** ECM is field `C`: `GlobalDiffusionConstant=0.0`,
`GlobalDecayConstant=0.0005` (near-static accumulator, matches A14's "burden, not density"
decision). Myofibroblasts deposit into it via `SecretionOnContact`; nothing removes it except
the tiny passive decay — there is no protease/MMP-analog field or mechanism. `C` has no pixel
footprint of its own. Its only mechanical consequence is indirect, applied at the cells that
happen to be sitting on high-`C` pixels: `c_norm(C)` scales a myofibroblast's `lambdaVolume`
(stiffness) and, since `7858a83` (2026-08-12), its `targetVolume` too — this second coupling is
what makes accumulated collagen burden actually claim more lattice space and produce the
sheet-displacement the model is built to show (`cc3d_v1_todo.md` PRIORITY 0). If a
myofibroblast that was carrying high local `C` dies or migrates away, the `C` value at that
location is unaffected, but nothing at that location claims volume anymore — the mechanical
effect of that burden disappears with the cell, even though the field value is still there.

**Chandrasegaran et al.** ECM is a `CellType`, on equal footing with fibroblast, myofibroblast,
macrophage, senescent myofibroblast. Fibroblasts and myofibroblasts *produce* ECM as a
volume-claiming act — new ECM pixels/cells appear in the lattice, not a field value going up
at a point. ECM is *removed* by a dedicated mechanism: "ECM degradation by MMP occurs by
removing ECM 'cells' that have a MMP concentration at their COM greater than `MMP_thr`" — MMP
is itself a full reaction-diffusion field with its own macrophage/myofibroblast sources, so
degradation is a real spatial process, not a decay constant. Critically, other cells *sense*
ECM by contact area, not field concentration: myofibroblast differentiation requires "common
surface area with ECM ... greater than `ECM_thr`"; myofibroblast apoptosis-by-tension-release
triggers when ECM contact area drops *below* that threshold; fibroblast/myofibroblast
chemotaxis strength toward PDGF is *increased* when the cell is in contact with ECM
(`λ_PDGF(ECM)`), modeling collagen-fiber-guided migration. None of that is expressible with a
field read at a cell's center of mass — it requires ECM to be a discrete neighbor with its own
pixels.

## Comparison

| | Field (current) | Cell type (Chandrasegaran precedent) |
|---|---|---|
| **Volume occupancy** | Indirect only — burden claims space by growing a *producer cell's* `targetVolume`; no independent footprint | Direct — ECM pixels claim lattice space on their own, independent of any live producer cell nearby |
| **Persistence after producer cell is gone** | Mechanically lost — field value stays but has nothing to act through once the coupled cell leaves/dies | Persists structurally — ECM cells stay in the lattice until an explicit degradation event removes them |
| **Degradation** | One global passive decay constant; no spatial/enzymatic process | Explicit MMP field + threshold-based removal — degradation is itself a modeled, spatially-varying process |
| **Cell sensing of ECM** | Field concentration at a cell's COM only | Contact-area-based (`Rs`, `ECM_thr`) *and* can still layer field-based signals on top — richer vocabulary (differentiation gating, apoptosis gating, directional chemotaxis modulation) |
| **Fits A14 ("burden, not density")** | Yes, directly — that's what a field is | Would need reinterpreting; discrete ECM cells are inherently closer to density/occupancy than to a burden scalar, though a hybrid (ECM cells scaled by an internal "maturity"/crosslink variable) could recover something burden-like |
| **Implementation cost from here** | None — already built, already coupled to displacement | Substantial: new `CellType`, `Volume`/`Surface`/`Contact` energies against every existing type, a deposition rule (create/grow ECM cells near secreting cells, not just increment a scalar), a degradation pathway (need an MMP-analog field that doesn't currently exist), and a rewrite of every place that currently reads `C` as a scalar (`update_myofibroblast_state`, `update_fibroblast_state`, damage/activation gating) |
| **Runtime cost** | Field solve is already the cheaper of the two field types in this model (`D=0`); pixel-loop reads are the known bottleneck (~60% of `ODESignalSteppable` runtime per `cc3d_v1_todo.md`) but scale with lattice size, not cell count | More cells in the CPM lattice (ECM as discrete cells rather than a field) generally means more pixel-copy attempts per MCS — the Chandrasegaran domain is smaller (200×200 vs. this model's) but still runs a full multi-day simulation at 27s/MCS-equivalent; would need its own runtime characterization here before assuming it's affordable at this model's `Steps` count |
| **Validated precedent** | This project's own use, not externally validated as a pattern | Yes — peer-reviewed, PSO-calibrated against literature wound-healing data, same framework (CC3D), directly comparable fibrosis/wound-healing domain |

## Assessment

The field route is not a simplification we're stuck defending — it just finished doing its
job. `targetVolume` coupling (`7858a83`) is what turned accumulated `C` into actual
sheet displacement, and the corrected lumen-collagen diagnostic (this session) exists
specifically to check whether that displacement is real narrowing or a measurement artifact.
That result isn't in yet (full confirmation run in progress). Until it lands, there's no
finding that the field approach *can't* produce the validation target — the open question is
calibration (`K_C`, `MYOF_TARGET_VOLUME_GROWTH_FACTOR`), not representation.

The cell-type route's real advantages — ECM persisting independent of its producer,
contact-area-gated cell state transitions, MMP-mediated degradation, fiber-guided
chemotaxis — are all things this model doesn't currently need for its stated v1 claim (Higham
et al. lumen-narrowing target). They *would* matter if the model grows toward: ECM remodeling
dynamics (something actively breaking down collagen, not just slow passive decay), senescence
or SASP-style secondary phenotype effects (Chandrasegaran's actual subject), or any mechanism
where a cell's behavior should depend on *being embedded in* matrix rather than *sitting on a
concentration*. None of those are in `model_spec_v1_v2.md` for v1.

**Recommendation: stay on the field for v1.** Revisit this once the full-run confirmation
under the corrected diagnostic (in progress as of this doc) shows whether `targetVolume`
coupling gets sheet displacement into the neighborhood of the ~22% Higham target through
calibration alone. If calibration can't get there — not "if it's inelegant" but "if the
field genuinely cannot produce enough displacement without going non-physical on `K_C` or
`MYOF_TARGET_VOLUME_GROWTH_FACTOR`" — that's the point where the cell-type route stops being
a hypothetical v2 upgrade and becomes the fallback `cc3d_v1_todo.md` already lists (PRIORITY 0
plan step 5, "last resort... reintroduce a static-mass cell type"). This assessment doesn't
change that ordering; it just confirms there's a working, published reference implementation
to lean on if/when that fallback is needed, rather than designing the cell-type mechanics from
scratch.
