# Model Specification — v1 and v2

**Compiled:** 2026-07-26 · Companion to `model_assumptions_for_slides.md` (assumptions A1–A17)
**Scope:** v1 is the two-week hackathon build. v2 is the designated next increment.
Every v1 item is chosen to be replaceable without restructuring.

> **Status note, 2026-10-30 (B′ kickoff).** Three v2 items are now **in this paper**, per
> `roadmap_revision_2026-10-29.md` (which supersedes the 2026-10-26 v2 ranking's items 1, 4 and 5):
> the spatial pro-inflammatory field `P` with three tissue consumers, the MMP field, and the
> volume-occupying ECM cell type. They are built in Gate B′ (Nov–Dec 2026) behind five switches in
> `parameters.py`, all off until B′ closes, and Gate D then runs as an ablation over them. The v2
> list below is kept as written for provenance; read its `P`, MMP and ECM entries as "moved to v1,
> B′", and its remaining items (stiffness-gated latent TGF-β, adventitial compartment, EMT, ASM,
> annulus) as the post-paper list. Build plan: `docs/gate_Bprime_plan_2026-10-30.md`.
>
> **Implementation status note, 2026-09-26.** This spec is the 2026-07-26 design; the built model
> departs from it in these places, each recorded where it was decided. Read the spec below with
> these in mind.
> - **ECM is a non-diffusing burden field** (A14, 2026-08-02/08), not a "density field" (§2), and
>   physical units are **provisionally calibrated** (A7: 1 px = 1.25 µm, 1 MCS = 62.4 s), so the
>   "physical units" line in §8 no longer holds. Epithelial cells are 8 × 8 px (2026-09-18).
> - **Healthy epithelium secretes GF at a nonzero rate** (A19, 2026-08-09), not 0 (§4).
>   Myofibroblast GF secretion is currently **0.1**, raised from the 0.001 low-rate decision in §4's
>   note as a deliberate 2026-08-11 experiment, not a biological claim (revisit before reading the
>   G field quantitatively).
> - **ODE coupling is live** (Tellurium/SBML inside CC3D, `S_M2` and `f_d`), superseding the
>   `ode_signal_table.csv` / `get_signal(scenario)` plan in §6.
> - **§6 open decisions:** slab geometry chosen (A8; annulus deferred), epithelium is one layer,
>   ECM is a field in v1. A **volume-occupying ECM cell type** is now the prioritized mechanism
>   for the displacement gap (2026-09-06 decision, A8 Option 3) and should be added to the v2
>   list below.
> - **Added beyond the spec:** GF-gated fibroblast mitosis, epithelial FocalPointPlasticity
>   cohesion (passive), a live-footprint containment check.
> - **Still open from §5/§7:** focal damage placement (diffuse arm only), collagen area fraction /
>   thickness / myofibroblast-density readouts (not computed in the model), the scenario scans, and
>   the antioxidant-sign question.

---

## v1 — Subepithelial fibrosis, minimal

### 1. Objects (lattice entities)

| Object | Type | Notes |
|---|---|---|
| Epithelial cell — healthy | CPM cell | stationary |
| Epithelial cell — damaged | CPM cell | stationary; stationary GF source |
| Fibroblast | CPM cell | mobile, chemotactic |
| Myofibroblast | CPM cell | mobile (reduced); ECM producer |
| Fixed outer boundary | frozen CPM cell / wall | non-deformable, non-secreting; ASM slot for v2 |
| Lumen | Medium | narrows as a consequence of wall thickening |

### 2. Fields

- **GF** — single lumped growth-factor field, modeled as the *active* signal (latent pool not resolved)
- **ECM** — density field (open decision: field vs. generalized cells, see §6)

Both require an explicit decay term and no-flux (Neumann) lateral boundaries.

### 3. ODE-layer interface (two scalars + a clock)

| Symbol | Meaning |
|---|---|
| `S_M2(scenario)` | uniform additive source into the GF field (macrophage contribution) |
| `R_fib(scenario)` | fibroblast recruitment rate at the outer boundary |
| `f_d(scenario)` | damaged-epithelial fraction, scales the seeding level |

**Constants per scenario, not time series.** The ODE saturates at a periodic attractor: `M2_tot`
and `A` are flat from about day 27 and `f_d` from about day 83, because no ODE state variable
ratchets (measured 2026-08-04, `docs/ode_tissue_coupling_options.md` §1). Cycle-average once at
the attractor and the interface is three numbers per exposure/treatment condition. Macrophages
exist only here.

### 4. Properties

**Epithelial (healthy / damaged)**
- target volume, surface constraint
- high homotypic adhesion (the sheet is held together by contact energy)
- zero motility, zero chemotaxis
- damage state (binary)
- GF secretion rate — damaged only; healthy = 0 in v1

**Fibroblast**
- target volume, surface constraint
- motility; chemotaxis coefficient on ∇GF
- GF secretion rate (mobile source)
- **ECM deposition rate — nonzero** (see note below)
- differentiation threshold on *local* GF concentration

**Myofibroblast**
- target volume, surface constraint
- reduced motility
- ECM deposition rate (> fibroblast)
- GF secretion rate — **set low in v1 as a compensation, not a biological claim** (see note below)

**Note on the two secretion rates (evidence checked 2026-08-07)**

- *Fibroblast ECM must not be zero.* Myofibroblasts are conventionally the major ECM producers (Wilson, 2020), but in fibrotic **lung** and kidney only a minority of collagen-producing cells were αSMA⁺, and αSMA⁻ collagen producers activated TGF-β just as effectively (Sun et al., 2016). In corneal keratocyte lineage, fibroblasts deposited *more* fibrillar collagen I/V while myofibroblasts deposited more fibronectin and non-collagenous matrix (Acosta et al., 2023). Keep myofibroblast rate higher, but fibroblast rate > 0.
- *Why myofibroblast GF is low in v1.* Biologically it should be **high** — myofibroblasts produce growth factors that regulate other myofibroblasts (Wilson, 2020) and autocrine TGF-β1 drives myofibroblastic differentiation (Popova et al., 2010). But that autocrine loop is **gated by matrix stiffness**: myofibroblast contraction activates latent TGF-β from ECM stores only when the matrix resists, restricting autocrine myofibroblast generation to a stiffened ECM (Wipff et al., 2007). v1 collapses latent and active TGF-β into one field and has no stiffness, so the brake is absent and a high rate would run away. **Raise it in v2** once the latent/active split and density-gated activation are in place.
- *Standing caveat.* αSMA is an inconsistent marker for the cells doing either job across multiple organ-fibrosis models (Sun et al., 2016), so the fibroblast/myofibroblast binary is a modeling convenience with contested footing.

**Fixed outer boundary**
- frozen; no secretion, no response

**Fields**
- diffusion constant, decay constant per field

### 5. Behaviors

1. Epithelial damage seeded with a **spatial pattern** (focal ↔ diffuse) at a total level scaled by the ODE damaged-cell concentration
2. Damaged epithelium secretes GF — the **stationary** source
3. `S_M2` added uniformly to GF everywhere — a flat pedestal, contributes no gradient
4. Fibroblasts chemotax up ∇GF
5. Fibroblasts recruited across the outer boundary at rate `R_fib`
6. Fibroblast → myofibroblast when local GF exceeds threshold
7. Myofibroblasts deposit ECM locally, in the subepithelial compartment
8. ECM first-order turnover (crude stand-in for MMP degradation — **required**, so that persistence is a result rather than an artifact of omitting removal)
9. ECM occupies space; volume exclusion against the fixed boundary drives thickening **inward**, narrowing the lumen

### 6. Open decisions before building

- **Domain shape: flat slab or annulus?** A slab yields wall *thickness*; only an annular (ring) cross-section yields a true *lumen area*. If lumen area is wanted as a readout, the geometry must be annular. Unresolved and consequential. Data point (2026-08-08): the collaborator's `Subepithelial_Fibrosis-02` uses a `Periodic` X boundary on field G rather than closed ends — see the consideration logged in `docs/cc3d_v1_todo.md` Group 2.
- **ECM as a diffusive field vs. as generalized cells.** Field is simpler; cells give proper volume exclusion, which is what actually produces thickening.
- Epithelium one cell layer or several.
- Export `data/processed/ode_signal_table.csv` — one row per scenario with attractor values (`scenario, f_d, S_M2, R_fib, rho`), and write the steppable against a `get_signal(scenario)` accessor (per 2026-08-04).
- Exposure horizon to simulate. Tissue-side only: the signal is already at its attractor.

### 7. Prediction goals / outcomes

**Readouts** (all dimensionless / relative to baseline)
- **Collagen (ECM) area fraction — primary**
- subepithelial (lamina propria) thickness
- myofibroblast density and count
- lumen cross-sectional area — geometry only, *not* converted to resistance
- spatial pattern metric for ECM (clustering / spatial variance), to distinguish focal from diffuse

**Experiments**
1. **Headline — focal vs. diffuse epithelial damage at matched total damage.** Does the spatial pattern of injury change the lesion? Run this *early*: if the answer is no, the Cellular Potts justification thins and a simpler framework would have sufficed.
2. **Locate the `S_M2` threshold** at which the lesion flips focal → diffuse (uniform synchronous conversion). Found by **scanning `S_M2` across scenarios**, not by running longer — the signal saturates, so no crossing occurs mid-run (A11, A14).
3. **Antioxidant intervention** — reduce `S_M2` (and/or `R_fib`); measure lesion reduction and sensitivity to intervention timing.
4. **Exposure pattern** — recurring vs. continuous at matched cumulative dose.

**v1 claims**
- Subepithelial ECM accumulation patterned by injury geometry and gated by a scenario-constant macrophage signal. Progression over the run comes from the **ECM field integrating a sustained source** — the collagen field is the only ratchet in the coupled system.

**v1 explicitly does NOT claim**
- irreversibility or self-sustaining remodeling (no autocatalytic loop — see v2)
- airflow limitation, resistance, or spirometric disease
- adventitial / peribronchiolar fibrosis (different compartment, outside the smooth muscle)
- smooth-muscle remodeling, emphysema, granuloma

### 8. Not represented in v1

macrophages in tissue · granuloma · EMT · spatial pro-inflammatory field · MMPs · latent/active TGF-β split · stiffness feedback · airway smooth muscle · adventitial compartment · physical units (µm, hours) · mechanics of any kind

---

## v2 — Adding autocatalysis, mechanics-by-proxy, and the second compartment

> *2026-10-30:* the `P` field (§2), the MMP field (§2, behaviour 3) and the volume-occupying ECM
> cell type (§1) have moved into this paper (Gate B′); see the status note at the top. The ranking
> the 2026-10-26 roadmap gave this list has collapsed accordingly.

### 1. New objects

| Object | Replaces / adds |
|---|---|
| Airway smooth muscle cell | replaces the fixed outer boundary; contractile, TGF-β-responsive, ECM-secreting |
| EMT-derived mesenchymal cell | new route into the mesenchymal pool |
| Adventitial compartment | second mesenchymal space, **outside** the ASM layer |
| Volume-occupying ECM cell type *(added 2026-09-26)* | matter that actually claims lattice space, so deposited matrix can push the epithelial sheet. Prioritized 2026-09-06 because cell crowding alone does not close the gap to the ~22% lumen-narrowing target. Open design question: how it coexists with the burden field C (A14) without duplicating it. Reference implementation: `docs/ecm_field_vs_celltype_assessment.md` |

### 2. New fields

- **Pro-inflammatory field (P)** — spatial; promoted from an ODE scalar once EMT gives it a target. *Standing revised 2026-10-26/27:* pulled forward on 2026-10-26 (`roadmap_to_publication_2026-10-26.md` §1, because the ODE already emits `P`, the Bennet chip measures IL-6/IL-8, and A19a is a claim about `P`) and made **conditional** on 2026-10-27 (`roadmap_revision_2026-10-27.md` §3): build only if Gate D passes, time remains, and the tissue-layer consumer question is decided first — A17's dead-weight condition still holds while nothing in the tissue responds to `P`, and EMT stays deferred. If `P` output is wanted regardless, the cheap form is a `P`-analogue readout from existing epithelial state (H5), not a field.
- **Latent TGF-β** — separated from the active pool
- **MMP field** — replaces the crude first-order ECM decay

### 3. New properties

- **Local ECM density as a stiffness proxy.** CPM has no elastic modulus, stress, or strain, so stiffness cannot be computed. The activation rate of latent → active TGF-β becomes an increasing function of local ECM density. Phenomenological, and must be labeled as such.
- Epithelial cells: adhesion loss + motility gain on EMT
- ASM: contractility, proliferation, TGF-β responsiveness
- Physical scale calibration: lattice site → µm, MCS → hours

### 4. New behaviors

1. **Stiffness-gated latent TGF-β activation** — closes the ECM → stiffness → activation → ECM loop. This is the only mechanism that makes remodeling self-sustaining.
2. EMT driven by local P
3. MMP-mediated ECM degradation (replaces v1 first-order turnover)
4. ASM hyperplasia and ECM secretion; active inward/outward remodeling balance
5. Multiplicative gain of the ODE anti-inflammatory signal on cell-based secretion, supplementing or replacing the uniform pedestal

### 5. Prediction goals unlocked by v2

| Goal | Requires |
|---|---|
| **Hysteresis / irreversibility** — does the lesion persist after exposure stops? | stiffness feedback + MMP turnover |
| **Point of no return** — exposure duration beyond which reducing `S_M2` no longer resolves the lesion | stiffness feedback |
| Bistability in the ECM–activation loop | stiffness feedback |
| Wa/Pbm comparable to human airway morphometry | explicit basement membrane + scale calibration |
| Relative resistance index (with the Polosukhin caveat) | annular geometry + scale calibration |
| Subepithelial vs. adventitial contribution to narrowing | adventitial compartment + ASM |
| EMT contribution to the myofibroblast pool | EMT |

### 6. Dependency notes

- **Irreversibility claims depend entirely on the stiffness loop.** Until v2, "the lesion persists" is a statement about the exposure signal, not about the tissue.
- **The adventitial compartment matters for the biomass framing.** The wood-smoke literature emphasizes *peribronchiolar* (adventitial) fibrosis; v1 models only the subepithelial (lamina propria) compartment, which is supported for this exposure by basement-membrane thickening in biomass COPD but is not the compartment those papers measure.
- EMT is the strongest CPM-specific mechanism available (loss of adhesion + gain of motility) and is therefore the best answer to "why CompuCell3D rather than a simpler framework." It is deferred from v1 only because it confounds experiment 1.
