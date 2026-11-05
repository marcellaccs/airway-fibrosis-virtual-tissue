# Roadmap revision, 2026-10-29

**Supersedes §2, §3 and §6 of `roadmap_revision_2026-10-27.md`** (the gate order, the conditional status of the spatial `P` field, and the path table). Everything else in the 10-26 roadmap and the 10-27 revision stands: Gate A is not a gate, Gate B is closed, the bibliography is batched, the article type turns on the focal-vs-diffuse result plus real tissue.

**Source.** A read-through on 2026-10-28/29 (`reorientation_2026-10-28.md`) and Marcella's decisions on 2026-10-29.

## 1. The decision, stated once

Every mechanism that was parked as "next paper" on 10-27 is a *local* mechanism that could carry or erase pattern dependence. Excluding them does not make the focal-vs-diffuse test cleaner; it makes the answer depend on what was left out, and every exclusion biases the same way (toward focal persistence). So they move into this paper, and Gate D becomes an ablation: focal vs diffuse under the base model, then with each loop switched on. The loops are results, not machinery.

Four additions, one build gate, one rebaseline, then Gate D.

## 2. What is added

### 2.1 A spatial pro-inflammatory field `P` in the tissue (was C1, conditional)

- **Sources.** Healthy epithelium under exposure at rate `p_h`, damaged epithelium at `2 p_h` (A19a; the ratio is the ODE's `e6/e5 = 0.2/0.1`, not a new free parameter). Plus a spatially uniform pedestal `S_M1 = k_M1 (M1 + M1R)` from the ODE, on the same pattern as `S_M2`, standing in for macrophage-derived cytokine. Exposure gating uses the ODE's `WS`, so `P` sources pulse with the cooking schedule as they do in the ODE.
- **Diffusion and decay.** Two new parameters, to be set from IL-6 class behaviour (short-lived, diffusion length of order a few cell widths). Calibration table item.
- **Three consumers, each reading local `P` at the cell.**
  1. **Repair gating.** `p_repair = e4 (1 + e8 (M2 + M2R) + e9 A) / (1 + k_P P_local) × h/MCS`. A is uniform (from the ODE), `P` is local. A focus of damaged cells makes `P`, which keeps the focus damaged. Positive, local. This is the spatial version of the repair term already read from the ODE.
  2. **Fibroblast proliferation.** The mitosis gate signal becomes `G_local + k_prolif P_local` (IL-6/STAT3). One coefficient. A second route into the mesenchymal pool that bypasses `G`.
  3. **MMP.** See 2.2. The negative loop.
- **Matched damage is preserved.** Seeding tops the sheet up to the ODE's `f_d` every MCS, so the global damaged fraction stays pinned to the ODE in both arms even when local repair is slowed. What becomes spatial is where the damaged cells are and how long each lasts. The model stays one-way coupled at the ODE level; nothing is written back into the SBML.
- **Readout.** `P` band mean and the H5 `P`-analogue column both reported on the chip's clock.

### 2.2 An MMP field, sourced by epithelium under `P`

- **Why.** Pro-inflammatory signalling raises MMP expression. Zou 2014 found MMP-9, MMP-2 and TIMP-1 raised and **epithelium-localized** under wood smoke, so an epithelial MMP source is exposure-matched and small-airway-specific. This is the only negative loop on fibrosis in the model and the one most likely to erase a spurious focal signal.
- **Source.** Epithelial cells secrete MMP at `mmp_0 (1 + k_mmp P_local)`. Myofibroblasts reduce local MMP by a TIMP term (Chandrasegaran 2025 does this as a per-MCS subtraction at the cell COM; we can copy it).
- **Consumer.** ECM cells (2.3) are removed when local MMP at their COM exceeds `MMP_thr` (Chandrasegaran's rule, `proteinase_thr`). The `C` field, if kept, decays at `0.0005 + k_C,mmp MMP_local`.
- **Macrophage proxy.** The ODE's M1 level enters only through the `P` pedestal; no separate MMP pedestal in v1 of this.

### 2.3 ECM as a volume-occupying cell type (was v2 item 5, post-paper)

- **Precedent and code.** The field-vs-cell-type question was assessed on 2026-08-14 in `ecm_field_vs_celltype_assessment.md`; that doc is the long version of this section. Chandrasegaran, Sluka & Shanley 2025, *PLoS Comput Biol* 21(4): e1012298, DOI 10.1371/journal.pcbi.1012298. Code at github.com/Sharm8/Senescence_wound_healing_model (`Wound_healing_GitHub2/Simulation/wound_healing3Steppables.py`). ECM is cell type 6: passive, 7 × 7 µm (`Ecm_TarVol = (7/vox_to_um)^2`), `lambdaVolume = 2`, `lambdaSurface = 2`; contact energies ECM–ECM −2.0 (self-cohesive), Medium–ECM −1.0, ECM–cells +1.0; removed by `delete_cell` when the proteinase field at its COM is ≥ `proteinase_thr`; fibroblast chemotaxis strength increased on contact with ECM (contact guidance). Produced by fibroblasts and myofibroblasts above a growth-factor threshold, myofibroblasts at twice the fibroblast rate.
- **One thing not to copy.** Their new ECM cells are placed at a **random position anywhere in the 200 × 200 domain** (`x = random.randrange(0, 200 − cell_size)`; the adjacent-placement line is commented out). That is fine for a bulk wound readout and fatal for a spatial statistic. Ours must be placed on a Medium pixel adjacent to the producing myofibroblast, biased toward the sheet if we want the displacement to be realistic.
- **Our design.** Each myofibroblast accumulates an ECM budget each MCS (the current `0.08` on-contact secretion becomes the budget increment). When the budget crosses one quantum, one ECM cell (initially 2 × 2 px, target volume ≈ one quantum, growing to the 7 µm size with further deposition or placed at full size, to be decided in the build) is placed on an adjacent Medium pixel and the budget is decremented. Epithelial secretion into `C` stays as is (it is small and basal). `C` is retained as the diffuse burden for stiffness (`c_norm`) so the stiffening behaviour does not change; ECM cells are the volume.
- **What it buys.** A density cap on mesenchyme in a focus (cells cannot pile where matrix is), displacement of the sheet by matrix rather than by myofibroblast swelling, collagen area fraction as a direct pixel count (the histology readout), and an object to compute Ripley's K on (ECM cell centroids or pixels) that matches what a picrosirius section shows.
- **What it changes.** The myofibroblast `targetVolume` growth with `c_norm` (currently up to 3×) should be reduced or removed, since matrix now occupies the volume. The B4 baseline will move; that is why there is one rebaseline after all four additions, not one per addition.

### 2.4 Calibration of `G` (and the new fields) against data

Every `G` parameter with a measurable counterpart gets a row in `docs/calibration_table.md`: current value, what pins it, source or planned assay, status. Cited values go into the methods; uncited ones are stated as free. The Jones lab ELISA programme (`docs/jones_lab_assay_ask_2026-10-29.md`) is the planned-assay column.

The one already known to be wrong: the activation rate (0.02 per MCS of signal) converts a fibroblast in under an hour at saturating `G`; real myofibroblast differentiation takes one to three days. Fix from the α-SMA time course.

## 3. Gate structure, revised

| Order | Gate | Window | Decides |
|---|---|---|---|
| — | A1–A3 (not a gate) | Nov 2026 | Nothing; consistency check and UBC figure. |
| 1 | **B** | closed 10-27 | Baseline −2.5 %, n = 6, at 11 fibroblasts with repair. |
| 2 | **B′ — build the loops** | Nov–Dec 2026 | Clean runs with `P`, MMP, ECM cells and the three consumers; every switch off reproduces B4 line-for-line; one rebaseline with all switches on, n = 6, criteria pre-registered per A18. |
| 3 | **D — focal vs diffuse, as an ablation** | Jan–Feb 2027 | Which paper exists, and which loop carries or erases pattern dependence. |
| 4 | **C — readouts and chip-facing outputs** | Feb 2027, in parallel with D analysis | Collagen area fraction (now a pixel count), thickness, myofibroblast density, `P`-analogue, chip clock, mono-vs-co ablation. Most of C2 falls out of B′ for free. |
| 5 | **E — write** | Feb–May 2027 | Submit 1 May. Methods and introduction drafted during B′. |

**Gate D as an ablation.** Arms: focal vs diffuse at matched `f_d` and matched `S_M2`. Conditions: (0) base model, switches off; (1) + `P` repair gating; (2) + `P` proliferation; (3) + MMP; (4) + ECM cells; (5) all on. Pre-registered criterion unchanged: separation on Ripley's K(r/d) while collagen area fraction is statistically indistinguishable. The paper's result is the table of which conditions separate. If (5) separates, Original Research with a mechanism. If (0) separates and (5) does not, the honest result is that the loops erase it, which is also a paper. If nothing separates, Hypothesis and Theory.

**Switches** (all in `parameters.py`, all default off until B′ closes): `P_FIELD_ENABLED`, `P_GATES_REPAIR`, `P_DRIVES_PROLIFERATION`, `MMP_FIELD_ENABLED`, `ECM_CELLS_ENABLED`. Off must reproduce `434bc94` exactly; that is the first B′ criterion.

## 4. Cost and schedule

- B′ is about the size of Gate B (one field and three reads, one field and one rule, one cell type and a placement rule, five switches). The ECM cell type is the largest piece because it touches contact energies, displacement and the readouts.
- Gate D moves from January to February. March and April remain for writing, with methods and introduction drafted during B′ so E is not starting from nothing.
- Risk: the ECM cell type destabilizes the sheet or the lumen readout. Mitigation: it has its own switch, and the ablation design means Gate D can be run without it if it is not clean by January.
- The Jones lab assays run in parallel from November. Nothing in B′ waits on them; their results update the calibration table and, where they move a parameter, the rebaseline is rerun once.

## 5. Explicitly unchanged

- Gate A is not a gate; A1–A3 are a consistency check.
- ASM, annulus, adventitia, EMT, the antioxidant experiment: out of this paper. EMT in particular stays out: the `P` consumers above give `P` a job without adding a mesenchymal source at the damage site, which would confound the focal test.
- One-way coupling at the ODE level. `P`, MMP and ECM cells change what the tissue does with the ODE's constants; nothing is written back.
- Two clocks unreconciled; repair and the new per-hour rates converted on the tissue clock.
- Validation philosophy, Zou 2014 as primary anchor, Tier scheme, Ripley's K(r/d) criterion with `d` fixed before any curve.
- Bibliography batched; `Chandrasegaran2025` joins the E1 list.

## 6. Documents to update at B′ kickoff (not done in this revision)

*Done 2026-10-30, B′ kickoff; the build plan is `gate_Bprime_plan_2026-10-30.md`.*

- `model_assumptions_for_slides.md`: A13 (macrophages still only in the ODE, but their M1 level now enters as a `P` pedestal), A14 (ECM is a cell type plus a stiffness burden; sources restated), A17 (EMT still deferred; `P` has consumers, so the dead-weight condition no longer applies), A19b (the `G` ratio is now a calibration-table item with a planned assay).
- `model_spec_v1_v2.md`: status note pointing here; v2 ranking collapses (items 1, 4, 5 are in).
- `validation_targets.md`: §3.1 collagen area fraction becomes a direct readout; §3.6 states the ablation conditions; the Higham gap paragraph notes that ECM cells change displacement.
- `cc3d_v1_todo.md`: a B′ section with the five switches and the pre-registered criteria.
