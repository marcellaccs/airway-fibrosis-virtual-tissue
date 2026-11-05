# Model Assumptions

## 

* **Spatially structured sources of growth factor and ECM.** Growth-factor and ECM sources should be represented with explicit spatial structure rather than as a well-mixed compartment, because source geometry may drive fibrotic outcome: in an agent-based lung-fibrosis model, source spatial behavior and activation dynamics swung collagen area fraction from \~2% to \~40% (Islam et al., 2023).

  * *Stationary vs mobile sources.* The epithelium is a fixed source that sets where subepithelial fibrosis initiates, while fibroblasts/myofibroblasts are mobile, chemotactic sources that migrate and deposit most ECM; this stationary/mobile distinction alone was a leading driver of collagen area fraction in silico, consistent with discrete, spatially organized fibroblastic foci and epithelial-to-fibroblast signaling seen in fibrotic lung (Islam et al., 2023; Watanabe et al., 2025; Cohen et al., 2024). *Importance identified by a 2025 summer research student.*
  * *Latent vs active growth factor.* TGF-β is secreted in a latent form and must be activated, so activation is treated as a distinct, spatially gated step rather than assuming secreted = active; spatially localized latent sources active for longer drove fibrosis even at lower collagen fractions (Islam et al., 2023; Walker et al., 2020; Verma et al., 2023). *Importance identified by a 2025 summer research student.*
  * *Stiffness-driven activation feedback.* Deposited ECM stiffens the local matrix, and stiffness drives integrin-mediated activation of latent TGF-β, closing a positive-feedback loop (ECM → stiffness → activation → more ECM) that may be an important driver of self-sustaining, irreversible remodeling (Santos et al., 2018; Upagupta et al., 2018; Verma et al., 2023; Nho et al., 2022). *Importance identified by a 2025 summer research student.*
  * *Minimal initial model.* v1 uses a single lumped growth-factor field modeled as the active signal, with the activation term kept separable so the latent pool and the stiffness feedback can be depedendent on local ECM in a later version.
* **Exposure input is a threshold switch.** Repeated wood-smoke PM injures small-airway epithelium and triggers innate inflammation; exposure is modeled as a threshold on/off input rather than a fitted dose-response (Alexis et al., 2022; Ramos et al., 2021) - this was the approach in the ODE model. This is a first-approximation simplification: response is variable between individuals and can be cytotoxic without acute inflammatory influx (Hansson et al., 2023).
* **Polarization balance as the master signal.** The anti-/pro-inflammatory balance (M2:M1, i.e. A/P ratio) governs the fibrotic drive, with persistent M2 dominance being pro-fibrotic (Kishore \& Petrek, 2021; Bao et al., 2024). Fibroblasts and macrophages form a feedback loop (You et al., 2023), so how do we make the signal bi-directional?
* **TGF-β as the principal profibrotic mediator.** Persistent M2/TGF-β signaling activates fibroblasts, drives fibroblast-to-myofibroblast conversion, and deposits subepithelial ECM/collagen (Ren et al., 2022; Wnuk et al., 2020). TGF-β is treated as dominant but not sole; PDGF, IL-4, and IL-13 \*should be\* retained because single-pathway targeting is insufficient in vivo (Nguyen et al., 2024).
* **Sufficiency of a persistent Type II signal.** A sustained Type II (TGF-β) signal is taken to be sufficient, in-model, to generate subepithelial fibrosis (Machahua et al., 2025). In-vivo sufficiency is likely to be multifactorial (Nguyen et al., 2024).
* **Fibrosis.** Subepithelial/lumen ECM accumulation and airway-wall thickening represent the fibrotic endpoint and the transition from reversible inflammation to fixed structural remodeling (Savin et al., 2023; Joseph \& Tatler, 2022; Zhou et al., 2025). How do we define the disease state: imaging studies/% lumen?
* **Antioxidant intervention via parameter change.** Shifting the local inflammatory balance toward resolution via antioxidant reduces fibroblast-to-myofibroblast transition and ECM deposition; represented in-model by parameter changes rather than an explicit pathway (Wang et al., 2022; Liu et al., 2022; Hao et al., 2022). We did this in the ODE model.

  * *Unresolved conflict, found 2026-08-04.* The intervention as defined in the published scan (`supplementary.ipynb` cell 23) scales anti-inflammatory production **up** (`m8`, `m9`, `k_c`) along with the repair-enhancement parameters. Run to the attractor it collapses epithelial damage (`f_d` 0.114 → 0.0012, ~90×) but **raises** `M2_tot` by 37% and `A` sevenfold. In the ODE, whose endpoint is resolution and repair, that reads as recovery. In a fibrosis model, "more A, more M2" is the pathogenic direction — this same document states persistent M2 dominance is profibrotic. So the intervention is protective through the damage channel and mildly-to-strongly profibrotic through the growth-factor channel, and **the sign of the headline antioxidant result depends on which channel the A15 interface carries.** Three ways out: carry both channels and report the decomposition (recommended: the tension becomes the finding); redefine the intervention as reducing epithelial damage `e3`, which matches "antioxidant" more literally; or restrict the claim to the damage channel and state the omission. This must be settled before the intervention experiment is run, not after. Numbers in `docs/ode_tissue_coupling_options.md` §1.
* **Motivation / broader impact.** Wood-smoke PM is a major global driver of chronic airway disease, especially where biomass fuels are used, and remodeling is the structural step toward irreversible airflow limitation (Soriano et al., 2020; Bennitt et al., 2025; Lee et al., 2020; Balmes, 2019; Ortiz-Quintero et al., 2022). This may be especially relevant in the era of frequent wildfires.

## Scope and naming (v1 minimal model)

**Working title:** *A virtual tissue model of subepithelial fibrosis in the small airway* — the initiating lesion of biomass-smoke small airway remodeling.

The v1 model is named for the **lesion it produces**, not for a clinical disease. "Subepithelial fibrosis" is exactly what the minimal cell/field set generates, and it requires no physical-scale calibration, no airflow claim, and no smooth muscle. The subtitle carries the translational ambition and is defensible for this exposure specifically: "small airway remodeling" is the established term in the wood-smoke literature, where chronic exposure produces peribronchiolar fibrosis and increased collagen deposition in small airway walls (Zou et al., 2014), and biomass-smoke COPD is documented as a small-airway-predominant phenotype with severe peribronchiolar fibrosis and thickened basement membranes (Zhao et al., 2018; Robles-Hernández et al., 2025; Ortiz-Quintero et al., 2022). *Cf.* Morán-Mendoza et al. (2008), whose autopsy series found wood-smoke lung disease histopathologically comparable to smokers with diffuse interstitial fibrosis absent.

Deliberately **not** claimed in v1: airflow limitation, spirometric COPD, smooth-muscle remodeling, or emphysema.

## Assumptions added for the v1 minimal (hackathon) model

These extend A1–A6 above and are scoped for a two-week build. Each is written to be replaceable without restructuring the model.

* **A7. Provisional physical- and time-scale calibration.** `1 px = 1.25 µm`
  (`EPITHELIAL_CELL_WIDTH = 8` px against a cited 10 µm small-airway epithelial cell width —
  Devalia et al. 1990, 10.2±1.0 µm human bronchial cells by planimetry; Mariassy & Plopper 1984,
  9.3 µm Clara/secretory cell by TEM; Plopper 2020 confirms small-airway epithelium is simple
  cuboidal, not the large-airway columnar epithelium a naive 10–15 µm range would describe).
  `1 MCS = 62.4 s` (isolated-fibroblast scratch measurement — mean |ΔCOM| = 0.1484 px/MCS under
  the model's own Contact/Chemotaxis/diffusion physics — anchored to Tisler et al. (2020)'s
  IPF-cell-on-IPF-matrix migration speed, 10.7 µm/h). Both are **reinterpretations of the
  existing lattice, not rescalings**: pixel counts per cell are unchanged, so no
  adhesion-energy/`lambdaVolume` rescaling follows (Module 8.2's rescaling rule fires on a
  pixel-count change, which this is not). Fibroblast cell cycle: ~1730 MCS (from the cited
  25–34 h doubling-time range via the above), clearing Module 8.2's ≥1000 MCS/cycle guidance.

  **Limitations, for reviewers (updated 2026-09-07):** (1) the s/MCS anchor is a modeling
  judgment call, not a settled literature value — the conservative alternative (normal cells on
  normal matrix, 6.1 µm/h) gives 109.5 s/MCS instead of 62.4, and this model's wood-smoke/PM2.5
  exposure is a different etiology from Tisler2020's IPF cohort. No biomass-specific fibroblast
  *migration* figure exists; the closest exposure-matched evidence points the **other way** —
  biomass particulate leaves A549 motility unchanged to 125 µg/mL and reduces migration and
  motility speed at 250–500 µg/mL (de Albuquerque et al., 2021), and cigarette-smoke proxies
  likewise inhibit fibroblast migration (Wong et al., 2004; Shin et al., 2019). (2) Tisler2020's
  speeds are **confirmed figure-only**: the full text (checked 2026-09-07) reports the
  significance pattern and nothing else, with no table and no in-text values, so *(verify)* can
  only be cleared by digitizing Fig. 3B at full resolution or obtaining the values from the
  corresponding author. (3) A **second, independent pixel↔µm anchor now exists**, and it is an
  ECM dimension rather than a cell dimension: reticular basement membrane thickness measured in
  situ on the same section as the epithelium — 6.0 (1.8) µm in COPD vs 4.8 (1.2) µm in controls
  (Liesker et al., 2009), 3.19 ± 0.55 µm healthy by light microscopy and 2.85 ± 0.86 µm by
  electron microscopy (Wilson et al., 1997), diagnostic thresholds at 5–7 µm (Bourdin et al.,
  2007). It confirms the subepithelial band is physically sized, but it **cannot be a model
  readout**: at 1.25 µm/px the healthy→COPD change is ~1 px wide. The fibroblast-size route
  stays ruled out (spread area is a flattened cell's 2D substrate footprint, 20–40× a tissue
  cross-section). (4) The most useful new anchor is **dimensionless and so untouched by A7**:
  an epithelial : fibroblast cell-count ratio of ≈ 2.2 : 1 (14.8 ± 0.1 vs 6.6 ± 0.1 cells per
  100 µm of bronchus; Zajicek et al., 1992), checkable directly against the model's cell
  populations. The same source's linear epithelial density implies ≈ 6.8 µm per epithelial cell,
  a ~30% challenge to the 10 µm width anchor, so µm/px is best quoted as **~0.85–1.25 with 1.25
  chosen**, not as a settled value. (5) Epithelial cell **height** (recommended 2026-09-07 and **applied 2026-09-18**, see the end of this item) was a live recommendation
  rather than an inherited default: `TARGET_VOLUME_EPITHELIAL` 48 → 64 px, making the cell
  8 × 8 px = 10 × 10 µm, matching the 9.6 µm measured Clara-cell height (Mariassy & Plopper,
  1984) and the simple-cuboidal shape Plopper (2020) describes. Unlike the µm/px change this
  **is** a rescale — `LAMBDA_VOLUME_EPITHELIAL` 30 → 22.5, `LAMBDA_SURFACE_EPITHELIAL`
  1.0 → 0.87, epithelial `J` × 0.866 — **all applied 2026-09-18** (`parameters.py`, XML). Full anchor
  table, dispersion and citations: `docs/validation_targets.md` §7; supporting/challenging
  sources: `docs/evidence_dossier_assumptions.md` § Assumption A7, entries [43]–[54].

  **Consequence:** at this calibration, a 20,000-MCS run is ~14–25 days of biological time, not
  the ~24 weeks other exposure sources (e.g. Li et al., 2024) imply, and the 2026-08-14
  displacement-plateau finding (MCS ~300–400) corresponds to ~5–12 hours — a fast, saturating
  event within the first half-day, not a slow multi-week progression.

  **Update 2026-09-26, after the epithelial rescale (2026-09-18):** the plateau reading above is
  specific to the old 6 × 8 px epithelium and does not carry over. On the current 8 × 8 px geometry
  (8 full 20,000-MCS runs) lumen narrowing reaches about −8% by MCS 1000 and then keeps drifting
  through MCS 20000 in most runs (−8.6% to −17.2%, mean −12.3%), so there is no early plateau to
  interpret as a saturating mechanism. The MCS-to-time conversion above is unchanged. The rescale
  itself accounts for part of the larger narrowing: with cell size held fixed, softer epithelial
  lambdas and lower epithelial contact energies narrow more at matched subepithelial pressure
  (3 configurations × 3 seeds, 2026-09-21), while the taller cell alone does not.
  Epithelial cell height 8 px also means the seeding band is now derived from cell height, and the
  subepithelial band is 68 px / 85 µm, not 70 px / 87.5 µm. See `lab-notebook/2026/2026-09-18.md`.

  **Applied 2026-10-27 (Gate B2, `roadmap_revision_2026-10-27.md` §5):** `FIBROBLAST_INITIAL_NUMBER`
  re-anchored 80 → **11** on anchor (4), the **ratio reading** of Zajicek et al. (1992): 25 epithelial
  cells / 2.2 ≈ 11, giving 25 : 11 ≈ 2.3 : 1 at `t = 0`. The linear-density reading of the same source
  (6.6 fibroblasts per 100 µm × 250 µm ≈ 16–17) was not taken: it inherits both the ~0.85–1.25 µm/px
  spread and the 10 µm vs ~6.8 µm epithelial-width tension above, whereas the ratio is dimensionless
  and is exactly the comparison A18 permits. The 80 was the 2026-08-11 displacement experiment, not a
  calibration, and the displacement gap is post-paper. Expected consequence, re-measured in Gate B4:
  less early lumen narrowing than the −12.3 % mean measured at 80 (initial subepithelial occupancy
  drops ~7×). Source remains abstract-level, hamster, SE not SD, *(verify)*.
  **Measured 2026-10-27 (Gate B4):** −0.3 % to −4.2 % at MCS 20000 (mean −2.5 %, SD 1.4, n = 6,
  seeds 200–205) against −12.3 % at 80; final mesenchymal count 42–62 vs 102–114. Direction held;
  this is now the standing replicate baseline (`lab-notebook/2026/2026-10-27.md`). The ~9× gap to
  the Higham magnitude in `validation_targets.md` §3.5 Tier 2 is flagged there as a finding, not a
  reason to revisit the count.

  Derivation history (superseded intermediate notes, kept for provenance):
  `lab-notebook/2026/2026-08-14.md` (µm/px started, uncited placeholder), `2026-09-04.md`
  (both anchors cited, µm/px closed), `2026-09-06.md` (s/MCS closed with the scratch
  measurement, anchor choice decided).

* **A8. 2D airway-wall cross-section with a fixed outer boundary.** The tissue is a single cross-section of the small-airway wall bounded by a non-deformable outer constraint. The boundary exists to bias wall growth **inward**, so subepithelial cell-mass expansion displaces the epithelial sheet luminally and narrows the lumen, rather than expanding the wall outward. It is explicitly *not* smooth muscle: it is a geometric device occupying the slot that an airway-smooth-muscle cell type would later fill. Inward/outward remodeling balance is a genuine open question in the literature, so the inward bias is stated as a modeling posit, not a finding.

  * *Design decision, 2026-08-08: the lumen is Medium, not a frozen airway cell; narrowing is by epithelial-sheet displacement.* The lumen is CompuCell3D **Medium**. A frozen "airway" cell was considered and rejected: its sites are locked, so the epithelial sheet could never move into it — lumen narrowing (`validation_targets.md` §3.5, Tier 1) becomes unproducible — and it would trap the subepithelial compartment between two rigid surfaces, turning `R_fib` recruitment (A15) into volume-constraint artefacts rather than thickening. **Mechanism chosen (Option 1):** subepithelial cell mass (recruited fibroblasts/myofibroblasts) thickens the compartment; the frozen outer boundary (A8) directs that expansion onto the epithelial sheet, which slides luminally into the Medium while remaining intact. No cell enters the lumen or crosses the epithelium — the sheet is displaced as a unit. This couples lumen area to fibroblast *number* (Hoshino et al., 1998, rs = 0.88; Eapen et al., 2021), consistent with §3.2, and keeps lumen strictly the Tier-1 geometric readout of A12. **ECM/collagen is a non-diffusing accumulator field** (D ≈ 0; A14): deposition adds, decay subtracts, so collagen stays where myofibroblasts write it (subepithelial, A9) and cannot leak into the lumen; only the growth-factor (TGF-β) field diffuses. **Rejected (Option 4):** an ECM field diffusing through the epithelium and filling the lumen by thresholding Medium — contradicts A9 (intraluminal deposition models organizing/obliterative bronchiolitis, a different lesion), mismodels collagen as diffusible, and would fail the subepithelial pattern check in §3.6. **Deferred to v2 (Option 3):** a reticular-basement-membrane cell just below the epithelium with TGF-β-driven target-volume growth — anatomically richer (RBM thickening, Eapen et al., 2021) but conflicts with A14's field/burden convention and adds a cell type; adopt only if a reviewer needs collagen itself to occupy space. **Containment detail:** epithelial density reduces fibroblast/myofibroblast motility (contact-mediated), used to keep the mobile cells subepithelial (reinforcing A9), not as a narrowing mechanism. **Implementation:** epithelial–epithelial adhesion must be strong enough that the sheet stays continuous as it is displaced; the growth-factor field keeps its decay + Neumann lateral BCs (A14); a one-row frozen floor at ymin is optional as a boundary anchor without rigidifying the airspace.
* **A9. ECM accumulates subepithelially, not intraluminally.** Superseding the earlier design note ("ECM is deposited into lumen layer"). The measured lesion is collagen within the airway wall and lamina propria, not organized material in the lumen (Zou et al., 2014; Eapen et al., 2021), and subepithelial layer thickening tracks fibroblast number and TGF-β1 expression (Hoshino et al., 1998). Intraluminal deposition would model a different lesion (organizing/obliterative bronchiolitis).
* **A10. Macrophage-predominant inflammation; no neutrophils in v1.** Not merely a simplification: biomass-smoke COPD shows greater macrophage and lymphocyte infiltration but *reduced* neutrophil infiltration compared with cigarette-smoke COPD (Zhao et al., 2018). The macrophage-only immune layer is the phenotypically appropriate choice for this exposure. *Cf.* Polosukhin et al. (2021), where neutrophilic infiltration correlated with adventitial collagen degradation and alveolar-attachment loss in cigarette-smoke COPD.
* **A11. Time-scale separation between the ODE layer and the tissue layer.** The published ODE model operates over hours to days; structural remodeling does not. Biomass PM2.5 exposure in rats produced small-airway inflammation with **no structural change at 4 weeks** and remodeling (collagen deposition, myofibroblast proliferation, wall thickening) only at **24 weeks** (Li et al., 2024), consistent with the 4–7-month wood-smoke exposures needed to raise small-airway collagen (Zou et al., 2014). The tissue layer is therefore driven by a reduced ODE output over a long horizon, not by instantaneous coupling.

  * *Superseded 2026-08-04: the ODE output does not drift, it saturates.* The two sub-bullets below were written from the published 200 h simulation window, which shows only the rising limb. Integrating the same model (`supplementary.ipynb` cell 21) to `t` = 4000 h under the published three-meals-a-day schedule gives `M2_tot` and `A` flat to five decimals from about **day 27**, and `f_d` flat from about **day 83** (the slower epithelial timescale, `1/e4` ≈ 21 days). Over the second half of the run `M2_tot` moves −0.28%. This is structural rather than a parameter accident: the exposure schedule is exactly periodic and **no state variable in the ODE ratchets** — every species is a birth–death balance relaxing to a periodic attractor. Numbers and method in `docs/ode_tissue_coupling_options.md` §1; reproduce with `model/ode/repair_term_check.py`.
  * *What replaces the averaging argument.* Strict quasi-steady state is now essentially the right reduction after the first month: cycle-average once at the attractor and the ODE contributes three constants per exposure scenario. There is no slow drift to homogenize, so the homogenization argument is not needed and **A11 is no longer the principal technical risk of the build.**
  * *Where progression comes from instead.* A constant input does **not** yield one static lesion, because the ECM field integrates it (A14: burden, not density). The collagen field is the only ratchet in the coupled system, and that is what makes the 4-week vs 24-week gap in Li et al. (2024) reproducible in-model. This is an independent argument for the burden-not-density decision.
  * *If signal-side progression is wanted later*, the ODE needs a slowly accumulating state — senescence, irreversible epithelial loss, or a growing fibroblast pool. None exists today; this is a v2 question.

  * *Original reasoning, retained for the record (now known to be wrong at this horizon).* Strict QSS would send the fast subsystem to a fixed point, i.e. M2 → a constant for a given exposure regime. The published ODE was believed not to do this under **recurring** exposure: it produces diminishing M1 peaks with apparently **progressive M2 accumulation**, a limit cycle with a slowly rising baseline. On that reading, ODE output would be treated as constant within an exposure cycle and slowly drifting upward across cycles, a homogenization/averaging argument. The drift is real for roughly the first month and then stops.

* **A12. Collagen area fraction is the primary endpoint; lumen area is secondary and geometric only.** Collagen area fraction is produced natively by the model, is the endpoint reported by the nearest prior art (Islam et al., 2023; Brown et al., 2011), and maps onto human small-airway histology, where α-SMA⁺ myofibroblast density per mm² of lamina propria, lamina propria thickness, and collagen-1/fibronectin change correlated with lung-function decline (Eapen et al., 2021). Lumen cross-sectional area is plotted but **not** converted to a resistance or airflow prediction: multivariable analysis of human small airways identified loss of radial alveolar attachments, not wall thickening, as the major determinant of airflow limitation (Polosukhin et al., 2021), and wall thickening itself is an early-stage feature that does not persist into severe disease (Higham et al., 2022).

* **A13. Macrophages are represented only in the ODE layer; the tissue layer contains epithelium and mesenchymal cells.** The split is by timescale and mixing, not convenience: the fast, well-mixed immune subsystem stays in the ODE, and the slow, spatially structured, matrix-producing subsystem is spatial. Consequences: (i) tissue-layer cell types are stationary epithelium (healthy/damaged) and mobile fibroblasts/myofibroblasts only; (ii) **granuloma formation is retired from scope**, since it is macrophage aggregation in tissue and is unbuildable without tissue macrophages; (iii) the existing "Old CC3D M1 to M2" prototype demonstrates CC3D mechanics but is no longer a direct precursor to the tissue layer.

  * *Revised 2026-10-30 (B′ kickoff, `roadmap_revision_2026-10-29.md` §2.1).* Macrophages are still
    only in the ODE; nothing here changes that. What changes is that the ODE's **M1** level now
    reaches the tissue, as the **M2** level already did: a spatially uniform pedestal
    `S_M1 = k_M1 (M1 + M1R)` is added to the new tissue field `P` every MCS, on the same pattern as
    `S_M2` on `G`. The coefficient is not a new free parameter: the ODE's own `P` equation gives the
    macrophage term as `m6 · WS · Hm3^nm3/(A^nm3 + Hm3^nm3) · (M1 + M1R)`, so `k_M1` inherits `m6`
    (and the `A` inhibition) relative to the epithelial rates `e5`/`e6`, exactly as the 2:1
    damaged:healthy ratio inherits `e6/e5` (A19a). Consequences (i)–(iii) stand: no tissue
    macrophages, no granuloma, and the M1-to-M2 prototype is not a precursor.
  * *Implemented 2026-10-31 (B′ Phase 1).* `S_M1` carries the ODE term's `WS` gate as well
    (`m6 · WS · Hill(A) · (M1 + M1R)`), so the pedestal pulses with exposure as the epithelial
    `P` source does, and it is spread over the subepithelial band only (the lamina propria,
    where the ODE's macrophages are), scaled by `n_epi / N_band` so its ratio to the epithelial
    source is the ODE's. `P` itself is not confined to the wall: it diffuses through the sheet into
    the lumen (nothing in the lumen reads it), the more so the longer its diffusion length. `P`'s
    diffusion constant is pinned independently of `G`'s, at the centre of the IL-6/IL-8-class
    literature range (λ = 50 µm = 40 px, decided 2026-11-02; `G`'s 3 px is a separate, still-uncited
    base-model value). See `gate_Bprime_plan_2026-10-30.md`, Phase 1 status.

* **A14. Growth-factor sources: stationary epithelial, mobile mesenchymal, plus a uniform macrophage pedestal.** Mapping onto the stationary/mobile axis that drove collagen area fraction from ~2% to ~40% in silico (Islam et al., 2023):

  * *Stationary source* — damaged epithelium. Injured airway epithelium is a documented growth-factor source, and subepithelial thickening tracks fibroblast number and TGF-β1 expression (Hoshino et al., 1998). The stronger claim this rests on — that the *damaged* epithelial type secretes at a higher rate than the healthy type, which is what makes the damage pattern set where the lesion forms — is stated and cited separately as **A19**.
  * *Mobile source* — fibroblasts, with myofibroblasts low (myofibroblasts are primarily ECM producers). **Implementation drift, 2026-09-26:** the committed XML currently secretes into G at `EpitheliumDamaged` 0.1, `EpithelialHealthy` 0.01, `Fibroblast` 0.005 and **`Myofibroblast` 0.1**. The myofibroblast value is 100× the low rate decided 2026-08-07 (stiffness-gated autocrine loop, no stiffness in v1); it was raised 2026-08-11 as a deliberate displacement experiment, not as a biological claim, and the field-G mean is already ~2 by MCS 3000 in current runs, against the ~0.02 baseline the `S_M2` calibration assumed. All four rates are first-pass and uncalibrated. *2026-11-02:* the myofibroblast rate goes back to 0.001 at the start of B′ Phase 5 as a pre-registered base-model change (`gate_Bprime_plan_2026-10-30.md` §6 item 7), because at 0.1 band `G` saturates both the differentiation and the mitosis gates and the `S_M2` focal-vs-diffuse control this assumption describes cannot operate; 0.1 becomes a Gate D sensitivity arm.
  * *Uniform pedestal* — the ODE macrophage contribution enters as a **spatially uniform additive source term** `S_M2`, derived from the cycle-averaged reduction in A11 and drifting upward with cumulative exposure.
  * *Why additive rather than a multiplicative gain.* A uniform source against uniform decay produces a flat steady-state pedestal that contributes **no gradient**, hence **no chemotactic force**; but differentiation responds to local *concentration* crossing a threshold, so the pedestal moves the whole wall closer to tipping at once. This yields two orthogonal controls — `S_M2` sets *how close the tissue is to tipping*, the epithelial damage pattern sets *where it tips first* — which makes the Anti/Pro phase space sketched in the 2025 notes (§B.5) directly executable as a parameter scan, and makes the antioxidant experiment a single scalar link (antioxidant → A → `S_M2` → lesion). A multiplicative gain on cell-based secretion is the v2 refinement: it preserves spatial structure but asserts that M2-derived TGF-β is entirely co-located with epithelium and fibroblasts.
  * *Known failure mode, treated as a result — revised 2026-08-04.* The `S_M2` value at which the lesion transitions from **focal** (patterned by epithelial damage) to **diffuse** (uniform conversion above threshold) remains the threshold worth locating: it is a direct operationalization of "when does remodeling become self-sustaining." What has changed is how it is reached. `S_M2` was expected to drift upward until it crossed the differentiation threshold on its own; it does not, because the signal saturates within about a month (see A11). The threshold must therefore be located by **scanning `S_M2` across exposure and treatment scenarios**, not by running longer. This is the better experiment: a controlled sweep rather than waiting for a crossing, and it means the failure mode cannot occur silently mid-run.
  * *Positioning vs. prior art.* Homogenizing the macrophage source is not a shortcut around Islam et al. (2023) but the complementary experiment: stripping the macrophage sources of spatial structure isolates whether epithelial patterning **alone** produces a focal lesion, a variable that model confounded.
  * *The ECM field represents burden, not density (decided 2026-08-02).* Field value is total collagen deposited per lattice site; deposition adds, decay subtracts. The two are not interchangeable and they dissociate experimentally: SO₂ exposure raised collagen fiber number, width and length in small airway walls while leaving fiber **density** unchanged (Teitz-Tennenbaum et al., 2025). Burden is chosen because it is what the nearest prior art reports as collagen area fraction (Islam et al., 2023; Brown et al., 2011), so the 2–40% band comparison in `docs/validation_targets.md` stays valid, and because it needs no per-site tissue-area denominator. Density can be recovered in post-processing if a reviewer asks.
  * *Implementation.* The growth-factor field requires an explicit decay term (a uniform source with no decay accumulates without bound), and no-flux (Neumann) lateral boundaries (a fixed-value boundary against a uniform source creates a spurious edge gradient that will drag fibroblasts sideways). The collagen/ECM field, by contrast, is **non-diffusing** (D ≈ 0): a deposited accumulator that stays where myofibroblasts write it, keeping it subepithelial (A9) and out of the lumen; only the growth-factor field diffuses (design decision 2026-08-08, under A8).
  * *Revised 2026-10-30 (B′ kickoff): ECM is a volume-occupying cell type **plus** the burden field.*
    The burden-not-density decision above stands for what `C` *means*, but `C` no longer carries the
    volume. Per `roadmap_revision_2026-10-29.md` §2.3 and the 2026-08-14 assessment
    (`ecm_field_vs_celltype_assessment.md`), deposited matrix becomes a passive CPM cell type
    (`ECM`, Chandrasegaran, Sluka & Shanley 2025 as the reference implementation), produced from a
    per-myofibroblast budget and placed on a Medium pixel **adjacent to the producing cell** (never
    at a random domain position, which is what the reference code does and what would destroy the
    Ripley's K readout). `C` is retained only as the diffuse stiffness burden read through
    `c_norm`; the myofibroblast `targetVolume` growth with `c_norm` is reduced or removed once ECM
    cells carry the volume. Collagen area fraction becomes a direct pixel count of ECM cells
    (`validation_targets.md` §3.1). **Sources, restated for the three fields** (all switch-gated,
    off by default until B′ closes): `G` — damaged epithelium (stationary), healthy epithelium
    (nonzero floor, A19b), fibroblasts and myofibroblasts (mobile), plus the uniform `S_M2`
    pedestal; `P` — healthy exposed epithelium at `p_h` and damaged at `2 p_h` under the ODE's `WS`
    (A19a), plus the uniform `S_M1` pedestal (A13); `MMP` — epithelium at `mmp_0 (1 + k_mmp P_local)`
    (Zou et al. 2014: MMP-9/MMP-2/TIMP-1 raised and epithelium-localized under wood smoke), reduced
    at myofibroblast centres by a TIMP term. `P` has three consumers (repair gating, fibroblast
    proliferation, MMP secretion); `MMP` removes ECM cells above `MMP_thr` and is the model's only
    negative loop on fibrosis.

* **A15. The ODE-to-tissue interface carries exactly two slowly drifting scalars.** `S_M2(cumulative exposure)` as the uniform additive growth-factor source, and `R_fib(cumulative exposure)` as a fibroblast recruitment rate across the domain boundary — both from the same cycle-averaged reduction. Recruitment is included because subepithelial thickening correlates with fibroblast *number*, not only phenotype (Hoshino et al., 1998, rs = 0.88), so a fixed seed pool that only differentiates will under-produce thickening. This interface is the highest-value reusable artifact of the v1 build.

  * *Open design question, 2026-08-04.* How `S_M2`, `R_fib` and a possible third signal (damaged-cell seeding from `f_d = Ed/(Eh+Ed)`) are generated from the ODE is not yet decided. Options, trade-offs and a suggested v1 stack are in `docs/ode_tissue_coupling_options.md`. Two results there bear on this assumption: (i) the signal **saturates rather than drifting** (see A11), so the interface is a small lookup table of attractor values, one row per exposure/treatment scenario, rather than a time series — which makes it a *stronger* reusable artifact than anticipated; (ii) under the published antioxidant scaling the damage and M2 channels move in **opposite directions**, so the interface choice sets the sign of the intervention result (see the antioxidant assumption above).
  * *`f_d` is safe to use as published.* The `Eh'` repair term carries an older parameter numbering than `Ed'` (`e9`/`e10` where `Ed'` uses `e8`/`e9`), so repair leaves `Ed` and arrives in `Eh` under different parameterisations. Quantified 2026-08-04: the effect is ≤1.8% on total epithelium and ≤0.04% on `f_d` even at the corners of the Figure 22 LHS ranges, because `Ed'` is the correct line and the logistic proliferation term absorbs the perturbation, moving `Eh` and `Ed` together and preserving the ratio. Worth renumbering for readability; changes no result.

* **A16. Anatomical ordering: outer boundary → subepithelial compartment → epithelium → lumen.** Correcting the layer order in the original schematic (`Model_Notes_digitized.md` §B.7 and `virtual_tissue_model_diagram.svg`), which placed the mobile cell layer between the epithelium and the lumen. "Subepithelial" means *beneath* the epithelium, i.e. away from the lumen; the epithelium is the innermost cellular layer and borders the lumen directly. This is the same error as A9 expressed geometrically.

* **A17. Epithelial-to-mesenchymal transition is deferred to v2, and the spatial pro-inflammatory field with it.** Under A13 nothing in the v1 tissue layer responds to the pro-inflammatory signal, so a spatial P field would be dead weight; P is kept as an ODE scalar. EMT is the natural v2 addition because it gives P a job in the tissue and supplies a second, inflammation-driven route to the mesenchymal pool. Deferred for v1 because (i) the evidence is thinner than it appears — Zou et al. (2014) found E-cadherin/vimentin double-stained cells in only 3 of 8 wood-smoke-exposed rats at 7 months, and the lineage-tracing literature (now cited, see below) substantially challenges whether lung epithelial cells become collagen-producing myofibroblasts; and (ii) it confounds the focal-vs-diffuse experiment, since damaged epithelium would both *source* growth factor and *become* fibroblasts. Noted as a strategic v2 target: EMT is loss of adhesion plus gain of motility, which is precisely what the Cellular Potts formalism represents and a point-agent ABM cannot — making it the strongest available answer to "why CompuCell3D rather than a simpler framework."

  * *Spatial `P` pulled forward, then made conditional (added 2026-10-27).* The 2026-10-26 roadmap
    (`roadmap_to_publication_2026-10-26.md` §1) pulled the spatial pro-inflammatory field forward to
    the head of the v2 list — ahead of the volume-occupying ECM cell type — because the ODE already
    emits `P`, the Bennet et al. (2026) chip measures IL-6/IL-8, and A19a is a claim about `P`. The
    2026-10-27 revision (`roadmap_revision_2026-10-27.md` §3) made it **conditional**: build only if
    the focal-vs-diffuse gate passes, time remains, and it is first decided what in the tissue
    layer consumes `P`. The condition stated above still holds unchanged: under A13 nothing in the
    v1 tissue layer responds to the pro-inflammatory signal, so a spatial `P` field is dead weight
    while that is true, and EMT — the consumer this assumption had in mind — remains deferred. If
    `P` output is wanted regardless, the cheap form is a `P`-analogue readout computed from the
    existing epithelial state (H5 in `aoc_platform_impact_2026-10-11.md` §5), folded into the
    readouts, not a field. Evidence for the deferral is unchanged.
  * *Dead-weight condition lifted; EMT still deferred (added 2026-10-30, B′ kickoff).* The
    2026-10-29 decision (`roadmap_revision_2026-10-29.md` §1–2) gives the spatial `P` field three
    tissue-layer consumers that are **not** EMT: it slows local epithelial repair
    (`p_repair / (1 + k_P P_local)`), it adds to the fibroblast mitosis gate signal
    (`G_local + k_prolif P_local`, IL-6/STAT3), and it drives epithelial MMP secretion. So the
    condition "nothing in the tissue responds to `P`" no longer holds, `P` is built in B′
    unconditionally, and the H5 `P`-analogue readout is kept alongside it. EMT itself stays out of
    this paper for the two reasons above, and now for a third: with `P` already doing work in the
    tissue, EMT would add a mesenchymal *source at the damage site* and confound the focal test
    (§5 of the revision). The lineage-tracing bound below (Tan et al., 2021) is unchanged.
  * *The EMT dispute, resolved enough to plan around (added 2026-08-02).* Rock et al. (2011) lineage-traced SPC-CreER and Scgb1a1-CreER epithelium through bleomycin fibrosis and found **no** conversion to myofibroblasts, and reviews of the lineage-tracing literature agree that resident mesenchymal cells, not epithelium, are the dominant source (Hung, 2020; Homps-Legrand et al., 2023). The reconciling result is quantitative: Tan et al. (2021) found only **1.94 ± 0.08%** of α-SMA⁺ cells were epithelium-derived (9.68% of S100A4⁺). So EMT is real but minor as a *cell source*, while epithelium is well supported as a *paracrine signalling source* (Hung, 2020) — which is precisely the role A14 already assigns it. Practical consequence for v2: implement EMT as a low-rate conversion bounded by roughly the Tan et al. figure, not as a major route into the mesenchymal pool, and do not let it displace `R_fib`.

* **A18. Validation is ordinal and pattern-based, not absolute.** A7's dimensionless readouts forbid comparison to an absolute thickness in µm, cell count per mm², or time-to-fibrosis, so agreement with the literature is claimed at the level of **direction, ordering, correlation structure, and spatial pattern**. This matches the standard set by the nearest prior art, which validated on dynamics and ranges rather than matched absolute values (Islam et al., 2023), on shape agreement and a custom severity index (Cogno et al., 2022), and on spatial progression pattern against histology (Yoshizawa et al., 2022). Two consequences worth stating on a slide before a reviewer raises them:

  * *The focal-vs-diffuse claim needs a spatial statistic, not an area fraction.* The experiment holds total injury fixed, so a scalar burden cannot distinguish the conditions by construction. Ripley's K applied to segmented fibrosis separates samples with **similar total fibrosis content but different spatial arrangement** in preclinical lung histology (Roop et al., 2026), and ECM density distribution histograms served the same purpose in silico (Cogno et al., 2022). This also gives A14's focal→diffuse threshold a measurable definition: the `S_M2` at which the collagen field's spatial signature becomes indistinguishable from a uniform random field.
  * *Validate against the accumulation limb only.* Human COPD small-airway collagen is not monotone with stage — increased in some series (Eurlings et al., 2014; Kong et al., 2023) and decreased in others (Annoni et al., 2012; Higham et al., 2022; Polosukhin et al., 2021; Suzuki et al., 2010). v1 has no MMP/degradation arm, so it can only produce accumulation, and the appropriate targets are the early and animal wood-smoke phase (Zou et al., 2014; Li et al., 2024), not severe human COPD. Gelatinase upregulation is documented in exactly this exposure model (Zou et al., 2014), making the omission citable rather than accidental.

  Full readout-by-readout targets, numeric anchors and the minimal validation set are in `docs/validation_targets.md`.

* **A19. Damaged epithelium secretes growth factor at a higher rate than healthy epithelium (added 2026-08-09).** The two epithelial types in the tissue layer differ in secretion rate, not only in label: `EpitheliumDamaged` writes to the growth-factor field at a higher rate than `EpithelialHealthy`, with the healthy rate non-zero rather than zero. This is what makes the damage pattern set *where* the lesion initiates under A14, and it is the assumption the focal-vs-diffuse experiment rests on, so it is stated separately rather than left implicit in A14's stationary-source bullet. The direction is well supported and supported specifically for injured or exposure-stressed airway epithelium, at three levels of evidence: **(i) association with the lesion** — in a chronic low-level allergen model, airway epithelial expression of the cleaved, potentially bioactive form of TGF-β1 rose with challenge and accumulation of epithelial TGF-β1 correlated with airway-wall remodeling, with eosinophils *not* a significant source (Kumar et al., 2004); **(ii) a healthy-vs-diseased comparison at the cell level** — airway epithelial cells brushed from asthmatic children and differentiated at air–liquid interface produced significantly more TGF-β2 and VEGF and expressed ~3.7-fold more periostin than cells from healthy children, a difference that persists in culture and so is a property of the epithelial cells themselves rather than of the surrounding milieu (López-Guisa et al., 2012); and **(iii) direct exposure and causal necessity** — cigarette-smoke-extract exposure of alveolar epithelial cells raised profibrotic gene expression and the secretion of *activated* TGF-β1 relative to unexposed controls (Checa et al., 2016), diesel exhaust particles raised TGF-β1 protein in bronchial epithelial cells (Baarsma et al., 2022), and epithelial-cell-specific deletion of CTGF attenuated bleomycin fibrosis in vivo, so epithelium-derived growth factor is not merely present but load-bearing (Yang et al., 2014).

  * *Model form.* A ratio, not an absolute rate. Under A7 the field is dimensionless, so the citable quantity is the damaged:healthy secretion ratio and the fact that the healthy floor is non-zero; no paper supplies a calibrated per-cell rate for small-airway epithelium, so the ratio is a scanned parameter and should be reported as such. This slots directly into the A14 scan alongside `S_M2`: `S_M2` sets how close the whole wall is to tipping, the damaged:healthy ratio sets how sharply the epithelial damage pattern is imprinted on the field.
  * *Known simplifications, stated before a reviewer raises them.* (a) **The evidence is one-directional but the biology is not.** Fibroblasts signal back to the epithelium — paracrine signalling from TGF-β-activated or IPF fibroblasts reactivates RAS in alveolar epithelial cells via SPARC/EGFR, closing a self-sustaining loop (Yao et al., 2021). This is the same caveat A1 carries via You et al. (2023), and v1 omits the return arm. (b) **"Damaged" is not monotonically "secreting more."** Cigarette smoke *reduced* wound repair and several EMT and Notch-1 markers in primary bronchial epithelial cells and counteracted TGF-β1's effects, so exposure-induced injury is not a uniform upregulation of profibrotic output (Di Vincenzo et al., 2022); and epithelial WNT5a in asthmatic biopsies correlated *positively* with % intact epithelium and *negatively* with % denuded epithelium (rs = −0.39), i.e. epithelium that has been shed can no longer secrete (Daud et al., 2025). v1's damaged cells persist and keep secreting, which is defensible for the sublethal, chronic exposure being modeled but would misrepresent frank denudation. (c) **Exposure-specific direction.** TGF-β's role in COPD is not unambiguously profibrotic — it acts as a repair and anti-inflammatory signal early, and it is prolonged exposure that dysregulates the signal (Kraik et al., 2024). A19 asserts the profibrotic direction only within the persistent-exposure regime A11 and A5 already scope.
  * *Consistency with A17.* A19 uses damaged epithelium as a **paracrine signalling source**, not as a cell source of myofibroblasts; that is exactly the role the lineage-tracing literature supports for epithelium (Hung, 2020), and it is why A19 can be stated strongly while EMT stays deferred.

  Supporting and challenging papers with links are in `docs/evidence_dossier_assumptions.md` (§ Assumption A19).

  * *Challenge, 2026-10-11: signal without measurable damage.* A microfluidic airway-on-a-chip with
    Calu-3 epithelium at air–liquid interface over 3D-encapsulated lung fibroblasts, exposed to
    **whole wood smoke** (the model's own exposure, not an extract), raised IL-6 and IL-8
    significantly and MUC5AC and endogenous TGF-β1 modestly, with **LDH not significantly raised** —
    pro-fibrotic and inflammatory signalling without widespread cell death (Bennet et al., 2026).
    A19's *nonzero healthy rate* is **supported** by this: at a zero healthy rate the result is
    unreproducible in-model at any parameter setting.

  * *Correction, 2026-10-23, after re-reading the ODE paper (Torres et al.).* The challenge above
    was aimed at the wrong layer. **The published ODE already predicts the chip's result**, so
    Bennet et al. corroborate the signal layer rather than contradict it:
    - `E_d` in the ODE is a **reversible, sub-lethal state, not death**. Repair runs `E_d → E_h` at
      `e4 = 0.002 h⁻¹`; damaged cells die at the same natural rate as healthy ones (`e2 = 0.001`)
      and still proliferate. The stability analysis defines `r = e3/(e2 + e4)` as the balance between
      damage creation and its removal by repair *or* natural death. Nothing in that state would
      release LDH.
    - Healthy epithelium produces pro-inflammatory cytokine **under exposure**:
      `e5 F(WS) F(E_h)` with `e5 = 0.1`, against `e6 = 0.2` for damaged — a **2:1** damaged:healthy
      ratio, gated by exposure rather than by damage.
    - In the full model, M2 macrophages and anti-inflammatory cytokine **enhance** repair
      (Eq. 16: `e4(1 + e8(M2 + M2_R) + e10 A)`), and the published antioxidant intervention operates
      partly through that term.
    - The subsystem was validated against Calcabrini et al. (2004) — A549 cells, PM2.5, IL-6 and
      TNF-α release over 72 h. Cytokine release, not viability.

    So the "LDH detects lytic death only, and is blind to the sub-lethal stressed state v1's
    *damaged* label actually denotes" reading is **confirmed by this project's own signal layer**,
    not merely plausible. The other two readings (sub-damage dose; too-steep ratio) are not refuted
    but are no longer needed to reconcile the chip.

    **What is actually challenged are three tissue-layer departures from the ODE, none of which the
    ODE supports:**
    1. **Damage is one-directional in the tissue layer.** The ODE has `e4`, and M2-enhanced repair
       on top of it. v1 is more irreversible than its own signal layer. *A repair path should be
       added; `cc3d_v1_todo.md` Priority 2.* **Added 2026-10-27 (Gate B1,
       `roadmap_revision_2026-10-27.md` §5):** `EpitheliumDamaged → EpithelialHealthy` at the ODE's
       `e4` read live from the SBML, on the tissue clock (3.5e-5 per MCS bare), with the Eq. 16
       M2/`A` enhancement carried (≈ 8.3e-5 per MCS at the attractor; evaluated on the live ODE
       state, spatially uniform, so no spatial structure is added). The `f_d`-tracking seeding rule
       refills the deficit, so the damaged *fraction* still follows the ODE while damage
       *membership* turns over at the repair rate (mean damaged lifetime ≈ 12,000 MCS against a
       20,000-MCS run). The one-directional choice was a v1 simplification, never an ODE
       inheritance. Decision record: `parameters.py` (`EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT`)
       and `lab-notebook/2026/2026-10-27.md`.
    2. **The 10:1 secretion ratio has no ODE provenance.** The ODE's ratio is **2:1**, and it is for
       pro-inflammatory cytokine. The 10:1 was a first-pass tissue-layer choice.
    3. **The output species was swapped.** The ODE's epithelium produces pro-inflammatory `P`; A19
       has the damaged epithelium producing the **growth-factor** field `G`. That is a separate
       assumption that borrowed the ODE's damaged-state label and attached a different secretion to
       it. It is not unfounded — Kumar (2004), López-Guisa (2012) and Checa (2016) do support
       epithelial TGF-β — but it needs to be argued on that evidence rather than inherited.

    **Consequent split, to apply:** A19a, damaged epithelium secretes **pro-inflammatory** cytokine
    at about 2× the healthy exposed rate (ODE-anchored, `e5`/`e6`); A19b, damaged epithelium is a
    **growth-factor** source at an uncalibrated ratio (tissue-layer assumption, scanned parameter).
    Logged in `docs/citation_todo.md`.

    *A19b status, 2026-10-30 (B′ kickoff).* The damaged:healthy `G` ratio (currently 10:1 in the
    XML) is now a row in `docs/calibration_table.md` with a **planned assay**: Jones lab assay 1
    (TGF-β1 ELISA on conditioned medium from exposed vs unexposed epithelium,
    `docs/jones_lab_assay_ask_2026-10-29.md`), with Kumar 2004 / López-Guisa 2012 / Checa 2016 as
    the literature proxies until it reports. Until then it is stated as free and scanned, and the
    B′ rebaseline runs it at 10:1 so the all-switches-off regression against `434bc94` holds.
    A19a's 2:1 ratio is inherited from the ODE and is what the new `P` sources use.

    **Consequences for the planned tests.** H1 (`f_d` = 0, pedestal alone) still runs, but it now
    tests whether the *GF-from-damaged-epithelium* channel is necessary, not whether damage is.
    H2's scan range is wrong: scan the pro-inflammatory ratio **around the ODE's 2:1**, not 1:1 → 10:1;
    the GF ratio has no ODE anchor and stays a scanned parameter. Full assessment:
    `docs/aoc_platform_impact_2026-10-11.md` §2 and §2A.

**Reusability note.** The highest-value artifact of the v1 build is the **ODE-to-field coupling interface** (a steppable that reads ODE output and writes field source terms), not the biology. Cell types, diffusion fields, and the collagen readout all port forward unchanged; the outer boundary (A8) is the single component designed to be replaced.

## References

Note: author lists are abbreviated and volume/issue/page numbers are incomplete for several entries; complete from Zotero before final use.

Alexis, N., et al. (2022). Development of a screening protocol to identify persons who are responsive to wood smoke particle-induced airway inflammation. *Inhalation Toxicology*.

Balmes, J. R. (2019). Household air pollution from domestic combustion of solid fuels and health. *Journal of Allergy and Clinical Immunology, 143*(6), 1979–1987. https://doi.org/10.1016/j.jaci.2019.04.016

Bao, J., et al. (2024). Cepharanthine attenuates pulmonary fibrosis via modulating macrophage M2 polarization. *BMC Pulmonary Medicine*.

Bennitt, F., et al. (2025). Global, regional, and national burden of household air pollution, 1990–2021: A systematic analysis for the Global Burden of Disease Study 2021. *The Lancet*.

Bosken, C. H., Wiggs, B. R., Paré, P. D., & Hogg, J. C. (1990). Small airway dimensions in smokers with obstruction to airflow. *American Review of Respiratory Disease, 142*, 563–570.

Brown, B. N., Price, I. M., Toapanta, F. R., DeAlmeida, D. R., Wiley, C. A., Ross, T. M., Oury, T. D., & Vodovotz, Y. (2011). An agent-based model of inflammation and fibrosis following particulate exposure in the lung. *Mathematical Biosciences*.

Cohen, M. L., et al. (2024). A fibroblast-dependent TGF-β1/sFRP2 noncanonical Wnt signaling axis promotes epithelial metaplasia in idiopathic pulmonary fibrosis. *Journal of Clinical Investigation*.

Eapen, M. S., et al. (2021). Increased myofibroblasts in the small airways, and relationship to remodelling and functional changes in smokers and COPD patients: Potential role of epithelial–mesenchymal transition. *ERJ Open Research*.

Hansson, A., et al. (2023). Reduced bronchoalveolar macrophage phagocytosis and cytotoxic effects after controlled short-term exposure to wood smoke in healthy humans. *Particle and Fibre Toxicology*.

Hao, W., et al. (2022). Roles of NRF2 in fibrotic diseases: From mechanisms to therapeutic approaches. *Frontiers in Physiology*.

Higham, A., et al. (2022). Increased luminal narrowing but reduced wall thickness in the small airways of severe COPD patients. *European Respiratory Society Congress Abstracts*.

Hoshino, M., Nakamura, Y., & Sim, J. J. (1998). Expression of growth factors and remodelling of the airway wall in bronchial asthma. *Thorax*.

Ikezoe, K., et al. (2021). Small airway reduction and fibrosis is an early pathologic feature of idiopathic pulmonary fibrosis. *American Journal of Respiratory and Critical Care Medicine*.

Islam, M. A., et al. (2023). An agent-based modeling approach for lung fibrosis in response to COVID-19. *PLOS Computational Biology*.

James, A. L., Paré, P. D., & Hogg, J. C. (1989). The mechanics of airway narrowing in asthma. *American Review of Respiratory Disease*.

Joseph, C., \& Tatler, A. L. (2022). Pathobiology of airway remodeling in asthma: The emerging role of integrins. *Journal of Asthma and Allergy*.

Kishore, A., \& Petrek, M. (2021). Roles of macrophage polarization and macrophage-derived miRNAs in pulmonary fibrosis. *Frontiers in Immunology*.

Lee, K., et al. (2020). Adverse health effects associated with household air pollution: A systematic review, meta-analysis, and burden estimation study. *The Lancet Global Health*.

Li, S., et al. (2024). Biomass fuels related-PM2.5 promotes lung fibroblast-myofibroblast transition through PI3K/AKT/TRPC1 pathway. *Ecotoxicology and Environmental Safety*.

Liu, J., et al. (2022). ROS-responsive liposomes as an inhaled drug delivery nanoplatform for idiopathic pulmonary fibrosis treatment via Nrf2 signaling. *Journal of Nanobiotechnology*.

Machahua, C., et al. (2025). Fibrosis in precision-cut lung slices: Comparing TGF-β and fibrotic cocktail. *Respiratory Research*.

Morán-Mendoza, O., Pérez-Padilla, J. R., Salazar-Flores, M., & Vazquez-Alfaro, F. (2008). Wood smoke-associated lung disease: A clinical, functional, radiological and pathological description. *International Journal of Tuberculosis and Lung Disease*.

Nguyen, H. N., et al. (2024). Leukemia inhibitory factor (LIF) receptor amplifies pathogenic activation of fibroblasts in lung fibrosis. *Proceedings of the National Academy of Sciences*.

Nho, R. S., et al. (2022). Biomechanical force and cellular stiffness in lung fibrosis. *The American Journal of Pathology*.

Ortiz-Quintero, B., et al. (2022). Mechanisms of lung damage and development of COPD due to household biomass-smoke exposure: Inflammation, oxidative stress, microRNAs, and gene polymorphisms. *Cells, 12*(1), 67. https://doi.org/10.3390/cells12010067

Polosukhin, V. V., et al. (2021). Small airway determinants of airflow limitation in chronic obstructive pulmonary disease. *Thorax*.

Ramos, C., et al. (2021). Short-term exposure to wood smoke increases the expression of pro-inflammatory cytokines, gelatinases, and TIMPs in guinea pigs. *Toxics*.

Ren, L. L., et al. (2022). Transforming growth factor-β signaling: From tissue fibrosis to therapeutic opportunities. *Chemico-Biological Interactions*.

Robles-Hernández, R. E., et al. (2025). Immunohistochemical analysis of mastocyte inflammation: A comparative study of COPD associated with tobacco smoking and wood smoke exposure. *Biomedicines*.

Santos, A., et al. (2018). Matrix stiffness: The conductor of organ fibrosis. *Current Rheumatology Reports*.

Savin, I. A., et al. (2023). Bronchial asthma, airway remodeling and lung fibrosis as successive steps of one process. *International Journal of Molecular Sciences*.

Soriano, J. B., et al. (2020). Prevalence and attributable health burden of chronic respiratory diseases, 1990–2017: A systematic analysis for the Global Burden of Disease Study 2017. *The Lancet Respiratory Medicine*.

Upagupta, C., et al. (2018). Matrix abnormalities in pulmonary fibrosis. *European Respiratory Review*.

Verma, B. K., et al. (2023). Substrate stiffness modulates TGF-β activation and ECM-associated gene expression in fibroblasts. *Bioengineering*.

Walker, M., et al. (2020). Mechanical stretch sustains myofibroblast phenotype and function in microtissues through latent TGF-β1 activation. *Integrative Biology*.

Wang, Y., et al. (2022). The role of Nrf2 in pulmonary fibrosis: Molecular mechanisms and treatment approaches. *Antioxidants*.

Watanabe, N., et al. (2025). Integrated spatial and single-cell transcriptomics reveal PAK kinase as a therapeutic target in fibroblastic foci and dense fibrosis of idiopathic pulmonary fibrosis. *European Respiratory Journal*.

Wnuk, D., et al. (2020). Enhanced asthma-related fibroblast to myofibroblast transition is the result of profibrotic TGF-β/Smad2/3 pathway intensification and antifibrotic TGF-β/Smad1/5/(8)9 pathway impairment. *Scientific Reports*.

You, Y., et al. (2023). Fibroblast-derived CXCL14 aggravates crystalline silica-induced pulmonary fibrosis by mediating polarization and recruitment of interstitial macrophages. *Journal of Hazardous Materials*.

Zhao, D., et al. (2018). Small airway disease: A different phenotype of early stage COPD associated with biomass smoke exposure. *Respirology*.

Zhou, R., et al. (2025). Small airway disease as a key factor in COPD: New perspectives and insights. *Frontiers in Medicine*.

Zou, Y., et al. (2014). Upregulation of gelatinases and epithelial–mesenchymal transition in small airway remodeling associated with chronic exposure to wood smoke. *PLOS ONE*.

### Additional references cited in A18 (validation targets, added 2026-08-02)

Annoni, R., et al. (2012). Extracellular matrix composition in COPD. *European Respiratory Journal*.

Cogno, N., Bauer, R., & Durante, M. (2022). A 3D agent-based model of lung fibrosis. *Symmetry*.

Eurlings, I. M. J., et al. (2014). Similar matrix alterations in alveolar and small airway walls of COPD patients. *BMC Pulmonary Medicine*.

Kong, A., et al. (2023). Collagen remodelling in COPD: A new paradigm. *European Respiratory Society Congress Abstracts*.

Roop, B., et al. (2026). Artificial intelligence, machine learning-based automated fibrosis quantification in preclinical models of pulmonary fibrosis. *Respiratory Research*.

Suzuki, M., et al. (2010). The quantitative relationship between collagen deposition and lung structure in COPD. *American Thoracic Society Conference Abstracts*.

Yoshizawa, M., et al. (2022). Computational simulation of liver fibrosis dynamics. *Scientific Reports*.

### Additional references cited in A17 (EMT lineage tracing, added 2026-08-02)

Homps-Legrand, M., et al. (2023). Origins of pathological myofibroblasts in lung fibrosis: Insights from lineage tracing mouse models in the single cell RNA sequencing era. *American Journal of Physiology: Lung Cellular and Molecular Physiology*.

Hung, C. F. (2020). Origin of myofibroblasts in lung fibrosis. *Current Tissue Microenvironment Reports*.

Rock, J. R., et al. (2011). Multiple stromal populations contribute to pulmonary fibrosis without evidence for epithelial to mesenchymal transition. *Proceedings of the National Academy of Sciences*.

Tan, W., et al. (2021). Cell tracing reveals the transdifferentiation fate of mouse lung epithelial cells during pulmonary fibrosis in vivo. *Experimental and Therapeutic Medicine*.

### Additional references cited in A19 (damaged vs healthy epithelial secretion, added 2026-08-09)

Bennet, T. J., Randhawa, A., Pieters, A., Caffrey, T. M., Solomon, T., Lyall, E., Huff, R. D., Schwartz, C., Xi, Y., Carlsten, C., & Cheung, K. C. (2026). Engineering a multilayer microfluidic airway-on-a-chip with tunable GelMA hydrogel for physiologically relevant aerosol exposure studies. *Scientific Reports*. https://doi.org/10.1038/s41598-026-69468-5

Baarsma, H. A., et al. (2022). Epithelial 3D-spheroids as a tool to study air pollutant-induced lung pathology. *SLAS Discovery*.

Checa, M., et al. (2016). Cigarette smoke enhances the expression of profibrotic molecules in alveolar epithelial cells. *PLOS ONE*.

Daud, T., et al. (2025). The role of WNT5a and TGF-β1 in airway remodelling and severe asthma. *Allergy*.

Di Vincenzo, S., et al. (2022). Cigarette smoke impairs airway epithelial wound repair: Role of modulation of epithelial–mesenchymal transition processes and Notch-1 signaling. *Antioxidants*.

Kraik, K., et al. (2024). The role of transforming growth factor-β (TGF-β) in asthma and chronic obstructive pulmonary disease (COPD). *Cells*.

Kumar, R. K., et al. (2004). Expression of growth factors by airway epithelial cells in a model of chronic asthma: Regulation and relationship to subepithelial fibrosis. *Clinical and Experimental Allergy*.

López-Guisa, J. M., et al. (2012). Airway epithelial cells from asthmatic children differentially express proremodeling factors. *Journal of Allergy and Clinical Immunology*.

Yang, J., et al. (2014). Activated alveolar epithelial cells initiate fibrosis through autocrine and paracrine secretion of connective tissue growth factor. *American Journal of Physiology: Lung Cellular and Molecular Physiology*.

Yao, L., et al. (2021). Bidirectional epithelial–mesenchymal crosstalk provides self-sustaining profibrotic signals in pulmonary fibrosis. *Journal of Biological Chemistry*.

### Additional references cited in A7 (scale-calibration anchors, added 2026-09-04)

Asano, S., Ito, S., Takahashi, K., Furuya, K., Kondo, M., Sokabe, M., & Hasegawa, Y. (2017). Matrix stiffness regulates migration of human lung fibroblasts. *Physiological Reports, 5*(9), e13281.

Bourdin, A., et al. (2007). Specificity of basement membrane thickening in severe asthma. *The Journal of Allergy and Clinical Immunology*.

de Albuquerque, Y. L., et al. (2021). The toxic effect of water-soluble particulate pollutants from biomass burning on alveolar lung cells. *Atmosphere*.

Devalia, J. L., et al. (1990). Culture and comparison of human bronchial and nasal epithelial cells in vitro. *Respiratory Medicine*.

Holz, O., et al. (2004). Lung fibroblasts from patients with emphysema show a reduced proliferation rate in culture. *European Respiratory Journal*.

Liesker, J. J. W., et al. (2009). Reticular basement membrane in asthma and COPD: Similar thickness, yet different composition. *International Journal of Chronic Obstructive Pulmonary Disease*.

Mariassy, A. T., & Plopper, C. G. (1984). Tracheobronchial epithelium of the sheep: II. Ultrastructural and morphometric analysis of the epithelial secretory cell types. *The Anatomical Record*.

Mio, T., et al. (1992). Proliferative characteristics of fibroblast lines derived from open lung biopsy specimens of patients with IPF (UIP). *Chest*.

Molina, C., et al. (2025). Clonal expansion of alveolar fibroblast progeny drives pulmonary fibrosis in mouse models. *The Journal of Clinical Investigation*.

Plopper, C. G. (2020). Structural methods for studying bronchiolar epithelial cells. *Lung Biology in Health and Disease*.

Recillas-Román, S., et al. (2021). Wood smoke extract promotes extracellular matrix remodeling in normal human lung fibroblasts. *International Journal of Toxicology*.

Shin, J.-M., et al. (2019). Cigarette smoke extract inhibits cell migration and contraction via the reactive oxygen species/AMPK pathway in nasal fibroblasts. *International Forum of Allergy & Rhinology*.

Suganuma, H., et al. (1995). Enhanced migration of fibroblasts derived from lungs with fibrotic lesions. *Thorax*.

Tisler, M., Alkmin, S., Chang, H.-Y., Leet, J., Bernau, K., Sandbo, N., & Campagnola, P. J. (2020). Analysis of fibroblast migration dynamics in idiopathic pulmonary fibrosis using image-based scaffolds of the lung extracellular matrix. *American Journal of Physiology: Lung Cellular and Molecular Physiology, 318*(2), L276–L286.

Wilson, J. W., et al. (1997). The measurement of reticular basement membrane and submucosal collagen in the asthmatic airway. *Clinical & Experimental Allergy*.

Wong, L. S., et al. (2004). Firsthand cigarette smoke alters fibroblast migration and survival: implications for impaired healing. *Wound Repair and Regeneration*.

Zajicek, G., et al. (1992). Cell kinetics of lamina propria fibroblasts in normal adult hamster bronchus. *The Anatomical Record*.
