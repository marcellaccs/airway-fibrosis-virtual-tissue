# Hackathon Teaming Doc — draft entry

Paste-ready for *Hackathon Ideas/Partnering 2026*. Two pieces: a one-line entry for the
recruiting list at the top of the doc, and the full project page.

---

## Piece 1 — add to "People with Hackathon Ideas looking for teammates"

> 6. Marcella Torres, `<INSTITUTIONAL EMAIL>`, Virtual tissue model of subepithelial fibrosis in the small airway after wood-smoke exposure

---

## Piece 2 — new page, using the template headings

**Name:  Marcella Torres**

**Title of Project:** Virtual Tissue Model of Subepithelial Fibrosis in the Small Airway: Coupling a Published Macrophage-Polarization ODE Model to a Cellular Potts Tissue Layer

**Brief Description of Project:**

**[CONTEXT]** Biomass and wood-smoke particulate is a major global driver of chronic airway disease, and the COPD it produces is a distinct, small-airway-predominant phenotype rather than a copy of the cigarette-smoke disease (Zhao et al., 2018; Ortiz-Quintero et al., 2022). Subepithelial fibrosis is the initiating structural lesion, and the step at which reversible inflammation becomes fixed remodeling. I have a published ODE model of the innate immune response to inhaled toxicants, including M1/M2 macrophage polarization calibrated to our own RAW 264.7 wood-smoke cytokine data (Bakry et al., 2024; Torres et al., 2019). A well-mixed ODE cannot represent a lesion that is defined by *where* matrix is deposited. The closest prior art, an agent-based model of inflammation and fibrosis after particulate lung exposure (Brown et al., 2011), used abstracted point-like agents and asked how much collagen accumulates; it cannot ask where it goes.

**[MINIMAL MODEL]** A 2D airway-wall cross-section in CompuCell3D, ordered outer boundary → subepithelial compartment → epithelium → lumen. Stationary epithelial cells (healthy and damaged) border the lumen; fibroblasts and myofibroblasts are mobile and chemotactic in the subepithelial compartment; a non-deformable outer boundary biases wall growth inward so that matrix accumulation narrows the lumen. Two fields: one lumped growth factor with explicit decay and no-flux lateral boundaries, and an ECM/collagen field representing burden. Macrophages stay in the ODE layer rather than the tissue, so the split is by timescale and mixing: the fast, well-mixed immune subsystem stays in the ODE, the slow, spatially structured, matrix-producing subsystem is spatial. The ODE-to-tissue interface deliberately carries **exactly two** slowly drifting scalars — a spatially uniform growth-factor source and a fibroblast recruitment rate — both obtained by cycle-averaging the ODE under recurring exposure.

**[VALIDATION]** The primary readout is collagen area fraction, reported dimensionless and compared against the 2–40% band produced by the nearest computational prior art (Islam et al., 2023). The headline test is whether **focal versus diffuse epithelial injury at matched total damage** produces different lesions. Because total injury is held fixed, a scalar burden cannot separate the arms by construction, so this is scored with Ripley's K, following Roop et al. (2026), who separated preclinical lung samples with matched Ashcroft scores and matched total fibrosis content by spatial distribution alone. Secondary target: subepithelial thickness should rise with fibroblast number, reproducing the rs = 0.88 correlation of Hoshino et al. (1998). One honest caveat built into the plan: human COPD small-airway collagen is *not* monotone with disease stage, so the model is validated against the accumulation limb (animal wood-smoke exposure, Zou et al., 2014; Li et al., 2024) rather than against severe human disease.

**[STRETCH GOALS]** (1) Locate the value of the uniform macrophage source at which the lesion tips from focal to diffuse — an operational definition of "when does remodeling become self-sustaining." (2) Epithelial-to-mesenchymal transition as a second, inflammation-driven route into the mesenchymal pool; this is the strongest Cellular-Potts-specific mechanism available, since EMT is loss of adhesion plus gain of motility. (3) Latent versus active TGF-β with stiffness-driven activation feedback (ECM → stiffness → activation → more ECM). (4) An in-silico antioxidant intervention, which reduces to a single scalar shift in the ODE output and so is cheap to run.

This v1 is scoped to be genuinely buildable in the hackathon window, but it is the first layer of a larger virtual-tissue program. The most reusable artifact is intended to be the ODE-to-field coupling steppable itself, which ports to any project that needs to drive a spatial model from a compartmental one.

**Expertise Sought in Partners:**

- CompuCell3D / Cellular Potts modeling — steppables, diffusion fields, cell types, parameter scans
- Coupling ODE or systems-level models to spatial models — the two-scalar interface and the cycle-averaging reduction are the principal technical risk in the build, and the part I would most value a second brain on
- Lung biology, airway histology or morphometry — particularly anyone who could help source or interpret real small-airway sections, which is what would turn the focal-vs-diffuse result into a comparison against measured tissue

*No prior experience in all areas is required; interest in any one of them is plenty.*

**Models to use (i.e., published work to read):**

*Closest prior art and comparison targets*

- [Brown et al. (2011)](https://doi.org/10.1016/j.mbs.2011.06.003) — ABM of inflammation and fibrosis after particulate lung exposure; the model this project is positioned against
- [Islam et al. (2023)](https://doi.org/10.1371/journal.pcbi.1011741) — ABM of lung fibrosis; source of the collagen-area-fraction convention and the stationary/mobile source result
- [Cogno et al. (2022)](https://doi.org/10.3390/sym14091759) — 3D agent-based model of lung fibrosis
- [Rikard et al. (2019)](https://doi.org/10.3389/fphys.2019.01481) — architecture precedent for coupling an ABM to a signaling model

*CompuCell3D framework*

- [Swat et al. (2012)](https://doi.org/10.1016/B978-0-12-388403-9.00013-8) — CompuCell3D
- [Sego et al. (2020)](https://doi.org/10.1371/journal.pcbi.1008451) — modular multiscale virtual-tissue framework

*Biology and validation data*

- [Zou et al. (2014)](https://doi.org/10.1371/journal.pone.0096708) — wood-smoke small-airway remodeling in rats; the exposure-matched target
- [Li et al. (2024)](https://doi.org/10.1016/j.ecoenv.2024.116423) — biomass PM2.5; no structural change at 4 weeks, remodeling at 24 weeks
- [Hoshino et al. (1998)](https://doi.org/10.1136/thx.53.1.21) — subepithelial thickness vs fibroblast number, rs = 0.88
- [Eapen et al. (2021)](https://doi.org/10.1183/23120541.00876-2020) — αSMA⁺ myofibroblast density per mm² of lamina propria in small airways
- [Zhao et al. (2018)](https://doi.org/10.1111/resp.13221) — biomass-smoke COPD as a distinct small-airway phenotype
- [Roop et al. (2026)](https://doi.org/10.1186/s12931-026-03536-2) — Ripley's K on segmented lung fibrosis; the spatial-statistics method

*Underlying ODE model*

- [Bakry et al. (2024)](https://doi.org/10.1016/j.jtbi.2024.111759) — mathematical model of the innate immune response to inhaled toxicants
- [Torres et al. (2019)](https://doi.org/10.1371/journal.pcbi.1007172) — immune cell influx and macrophage polarization

**How Potential Partners should Contact You (e-mail, phone, etc.):** `<INSTITUTIONAL EMAIL>`; Slack: DM Marcella Torres

**Group members:** Marcella Torres

**Organizers' comments:**

---

## Before you paste

- **Fill in `<INSTITUTIONAL EMAIL>`** in two places (the numbered list and the contact line).
- **Check the DOIs marked below**, which were not verified during the 2026-08-02 identifier pass and are reconstructed from the bibliography: Brown 2011, Cogno 2022, Swat 2012, Sego 2020, Zou 2014, Li 2024, Hoshino 1998, Zhao 2018, Bakry 2024, Torres 2019. The eight verified ones are Islam 2023, Rikard 2019, Eapen 2021 and Roop 2026. Simplest fix: drop the hyperlinks and give plain author-year citations as Ammar and Kyle largely did, or paste the links from Zotero.
- Confirm the Slack display name matches your actual account.
