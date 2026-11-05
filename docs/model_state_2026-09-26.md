# State of the model — 2026-09-26

**Snapshot of what is built, verified, and outstanding.** Code state: commit `f732bd1` (model code last
changed in `2133465`; everything after it is documentation). Compiled from `model_assumptions_for_slides.md`
(A1–A19), `model_spec_v1_v2.md`, `validation_targets.md`, `cc3d_v1_todo.md`, the lab notebook, and direct
checks of the code and XML. Later states should be new dated files, not edits to this one.

Project: `model/cc3d/subepithelial_fibrosis_draft/`.

---

## Built in v1 (committed, verified)

### Tissue layer (CC3D)

- 200×100 px slice, layered top to bottom: lumen (Medium, 20 rows) → epithelium (8 rows, derived from cell
  height) → subepithelial band (68 rows) → frozen outer boundary (A8, A16).
- Cell types: `EpithelialHealthy`, `EpitheliumDamaged`, `Fibroblast`, `Myofibroblast`, `OuterBoundary`.
- Epithelial sheet: 8×8 px cells, cold fluctuation amplitude, `ConnectivityGlobal`, and FocalPointPlasticity
  cohesion links (passive, not active folding).
- Fields: growth factor G (diffusing, decaying, Neumann-style boundaries) and ECM/collagen C. C is a
  non-diffusing accumulator of burden, not density (A14), with first-order decay 0.0005.
- ECM written by myofibroblasts into Medium, subepithelial side only (A9). Epithelium also secretes into C on
  its subepithelial side.
- Coupling mechanics: local C normalized as C/(C+K_C), feeding both `lambdaVolume` stiffening and
  myofibroblast `targetVolume` growth.

### Cell behaviors

- Fibroblasts chemotax up ∇G. Fibroblast → myofibroblast conversion happens when local G crosses a threshold.
- `R_fib` recruitment across the outer boundary, GF-biased (A15).
- GF-gated fibroblast mitosis, at the literature cell-cycle rate (not a displacement lever, per the
  2026-09-06 decision).
- Damage seeding is diffuse only: per-cell Bernoulli trials driven by the ODE's `f_d`. It is one-directional
  (no repair path).
- GF sources follow A14/A19: stationary damaged epithelium (healthy nonzero, damaged higher), mobile
  fibroblasts, myofibroblasts, plus a uniform `S_M2` pedestal. **Committed secretion rates into G:
  `EpitheliumDamaged` 0.1, `EpithelialHealthy` 0.01, `Fibroblast` 0.005, `Myofibroblast` 0.1.** The
  myofibroblast value is 100× the low rate the spec decided on (2026-08-07); it was raised 2026-08-11 as a
  deliberate displacement experiment, not a biological claim. All four are first-pass and uncalibrated.

### ODE coupling

- Live Tellurium/SBML sub-model running inside CC3D (Route 2). It supplies `S_M2` (uniform pedestal on G) and
  `f_d` (damage seeding). Verified stable against the notebook-derived attractor.
- WS exposure is a smooth sigmoid rule, not discrete events.

### Calibration (A7), pulled forward from v2

- 1 px = 1.25 µm and 1 MCS = 62.4 s, both provisional and both flagged as judgment calls in the docs.
  A 20,000-MCS run is about 14 days of model time, far short of the ~24 weeks of exposure in A11.
- Epithelial cell rescaled 6×8 → 8×8 px with the Module 8.2 lambda/J rescale (2026-09-18). The seeding band is
  now derived from cell height.

### Diagnostics and tooling

- Lumen area via flood fill, sheet position, occupancy readouts, live-footprint containment check, sheet
  integrity, count conservation, field stats.
- `<RandomSeed>` now reproduces a whole run (Python `random` is seeded from it), and logs say whether a run is
  pinned. The committed XML has no pin, so general runs stay random.
- `model/analysis/spatial_stats.py` exists (Ripley's K, CSR test, patch sizes, radius normalization). It is
  post-processing and is not wired to model output.

### Current verified behavior

- Six pinned and two unpinned full 20,000-MCS runs on the current geometry: all clean (no tracebacks,
  fragmentation, or lumen collagen leak).
- Lumen narrowing at MCS 20000 is −8.6% to −17.2% (mean −12.3%, SD 3.0, n = 6 pinned), with no plateau: most
  runs keep drifting through MCS 20000.
- The Higham target is about 22%, and no run reaches it (widest −17.2%).
- Narrowing figures from before 2026-09-18 (2.5–5.5%, "plateau by MCS 300–400") are on the old epithelium and
  are not comparable.

---

## Not done from the v1 spec

- **Focal damage placement** (A18's headline experiment). Only the diffuse arm exists, so focal vs. diffuse
  cannot be run yet.
- **Primary readouts are missing from the model.** There is no collagen area fraction, subepithelial
  thickness, or myofibroblast density readout in the steppables. Lumen area, sheet position and raw counts
  exist, but the endpoints validation targets §3.1–3.3 ask for do not. *Todo item 4.*
- **Experiments not run:** the `S_M2` threshold scan, antioxidant intervention, exposure-pattern comparison,
  the Hoshino thickness-vs-fibroblast-number sweep across `R_fib`, exposed-vs-control ratio, and late-vs-early
  ordering.
- **Scenario machinery:** no PSCAN setup, `iter_count` replicates, or scenario lookup table. There is only the
  single published exposure schedule.
- **Acceptance tests:** the "zero fields → no conversion" test and the focal-vs-diffuse spatial-statistics test
  have not been run.
- **Unresolved design question (spec §6): the antioxidant intervention's sign problem.** Damage falls but M2/A
  rise under the published scaling, so the result's sign depends on which channel the interface carries. It
  must be settled before that experiment runs.
- **Initial fibroblast count needs re-anchoring.** `FIBROBLAST_INITIAL_NUMBER = 80` came from a 2026-08-11
  displacement experiment, not a calibration. *Todo item 5.*

## v2 to build (spec §v2 and assumptions)

- **Stiffness-gated latent TGF-β activation.** The only mechanism that makes remodeling self-sustaining. Needs
  a latent/active TGF-β split and a local-ECM-density stiffness proxy; unlocks hysteresis, point-of-no-return
  and bistability.
- **MMP field** replacing the crude first-order ECM decay.
- **Airway smooth muscle** replacing the frozen boundary: contractility, proliferation, TGF-β response, ECM
  secretion.
- **Adventitial compartment**, the peribronchiolar space where the wood-smoke literature measures fibrosis.
- **EMT** as a low-rate route (about 2%, per Tan 2021), plus a spatial pro-inflammatory field P.
- **Multiplicative ODE gain** on cell-based secretion, and a higher myofibroblast GF secretion rate once
  stiffness gating exists.
- **Annular geometry** for a true lumen area and the resistance index.
- **Volume-occupying ECM cell type**, decided 2026-09-06 as the mechanism for closing the displacement gap.
  Added to the v2 objects table in `model_spec_v1_v2.md` on 2026-09-26 (it was previously only an open
  decision in spec §6 and A8's "Option 3, deferred"). Open design question: how it coexists with the burden
  field C (A14) without duplicating it.

## Validation status (targets doc)

- Tier 1 (lumen narrows, inward) is met. Tier 2 (ordinal pattern) is mostly untested, since the focal arm and
  the readouts are missing. Tier 3 (absolute) stays aspirational.
- Only the accumulation limb is validated against, because there are no MMPs. The doc says to state that before
  a reviewer does.
- The RBM anchor confirms the band is sized correctly but cannot be a readout: the whole disease effect is
  about one pixel wide at 1.25 µm/px.
- **Dimensionless anchor, not yet matched:** epithelial : fibroblast ≈ 2.2 : 1 in normal bronchus (Zajicek
  et al., 1992; abstract-level, hamster, SE, *(verify)*). At `t = 0` the model has 25 epithelial and 80
  fibroblasts, about 0.3 : 1 against a literature ratio of about 0.45 fibroblasts per epithelial cell. The
  implied target is about 11 fibroblasts (match the ratio) or about 16–17 (match the linear density over the
  250 µm domain). *Todo item 5.*
- Known open validation items: digitize Tisler2020 Fig. 3B, and obtain real wood-smoke sections to run through
  the Roop segmenter.

## Reading this state

- **Doc drift reconciled 2026-09-26** (`63293d9`): A7 height rescale marked applied, A7 plateau reading scoped
  to the old geometry, A14 secretion drift recorded, spec status note added. Recheck after further parameter
  changes.
- **Next in the todo:** item 4 (choose, add, and test readouts against the validation targets), item 5
  (re-anchor the initial fibroblasts), then the ECM cell type design.
