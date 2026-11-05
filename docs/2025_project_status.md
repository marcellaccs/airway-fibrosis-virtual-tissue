# 2025 Project Status: Toward a Virtual Tissue Model of the Airway Inflammatory Response to Inhaled Toxicants

**Last updated:** July 2026 · **Maintained by:** Marcella M. Torres

> **Scope update (2026-07-26).** Sections 3–5 below describe the 2025 design. The v1 build has
> since been narrowed: the model is named for the lesion (*subepithelial fibrosis in the small
> airway*), **macrophages are represented only in the ODE layer**, granuloma formation is retired
> from scope, and the ODE→tissue interface is reduced to two scalars. See
> `model_assumptions_for_slides.md` (assumptions A7–A17), `Model_Notes_digitized.md` §D, and
> `virtual_tissue_model_v1.svg`. Inline markers below flag the superseded passages.
**Purpose:** Re-orient the PI after time away from the project and onboard a new research assistant. Read this first, then the two companion files in this folder: `Model_Notes_digitized.md` (digitized handwritten design notes) and `research_materials_index.md` (annotated catalog of all code, data, and documents in the research Drive).

---

## 1. One-paragraph summary

We built and published an ordinary differential equation (ODE) model of the innate immune response of the airway to inhaled wood smoke particulate matter (PM). That model is temporal only — it tracks *how much* of each cell type and cytokine is present over time, but not *where*. The next phase, begun in Summer 2025, is to translate that ODE model into a **spatial "virtual tissue" model** in CompuCell3D (CC3D), so we can simulate emergent tissue-level pathology — specifically **small-airway remodeling and fibrosis** driven by repeated PM exposure and a persistent type II (M2/anti-inflammatory) immune response. The ODE model becomes a "signal-generating layer" that drives the behavior of spatially explicit cells (epithelium, macrophages, fibroblasts/myofibroblasts) laid out on a lattice.

---

## 2. Where the project has been (published work)

The foundational work is published as:

> Bakry, A., Brashear, E., Brashear, J., Jones, S.Z., Torres, M.M. *Development of a Mathematical Model of the Innate Immune Response to Inhaled Toxicants.* Journal of Theoretical Biology (submitted Dec 2024). Manuscript: `JTB-D-24-01036-pages-2.pdf`.

### What the model does

It captures the immune response of lung/airway tissue to wood smoke PM, focusing on the interactions among **epithelial cells, macrophages, and two lumped classes of cytokines** (pro- and anti-inflammatory). Its central biological story is the transition from an early **type I** response (pro-inflammatory, M1-macrophage-dominated) to a later **type II** response (anti-inflammatory/repair, M2-dominated). The **M2:M1 ratio** is the key readout: a persistently elevated M2:M1 ratio corresponds to the chronic, fibrotic conditions seen with repeated exposure (COPD, asthma, interstitial lung disease).

### How it was built — three submodels

The model was assembled in stages so that each piece could be validated against its own data before being combined:

1. **Epithelial–cytokine submodel.** Healthy epithelial cells (E_h) transition to a damaged state (E_d) under wood smoke exposure; damaged cells produce pro-inflammatory cytokine (P). Includes logistic growth with carrying capacity, natural death, self-repair, and Hill-function thresholds on cytokine production. Validated against Calcabrini et al. (2004) A549 lung-epithelial TNF-α/IL-6 data.
2. **M1–M2–cytokine (macrophage) submodel.** Naive M0 macrophages differentiate to M1 (pro-inflammatory) or M2 (anti-inflammatory) based on local cytokine signals; M1 can transition to M2. M1 produce pro-inflammatory cytokine (P); M2 (and, at lower rate, M1) produce anti-inflammatory cytokine (A). Anti-inflammatory cytokines self-inhibit and suppress P. Calibrated to **our own ELISA data** from RAW 264.7 mouse macrophages exposed to wood smoke (MIP-2 and IL-10 at 24/48/72 h). Includes a Morris-method global sensitivity analysis.
3. **Full combined model.** Merges the two submodels for an *in vivo* context, adding resident vs. recruited macrophage populations, background anti-inflammatory tone, and M2/anti-inflammatory enhancement of epithelial repair.

### Wood smoke exposure

Exposure enters every submodel through a **Boolean switch** F(WS): off below a threshold, maximally on above it. This is a deliberate simplification (no dose–response data exist to fit a Hill curve) and it means the model can be repurposed to *any* inflammatory stimulus by swapping the switch.

### Key results from the paper

- **Single exposure** → self-limiting acute response that resolves within ~48 h.
- **Recurring exposure** (three 1-h exposures/day, "cooking" scenario) → diminishing M1 peaks but *progressive accumulation of M2 cells and anti-inflammatory mediators* — i.e., a drift toward the chronic/fibrotic state.
- **Continuous exposure** (in vitro condition) → sustained elevation of both mediators, M1 dominance shifting to M2.
- **Antioxidant therapy** simulation (suppress pro-, enhance anti-inflammatory pathways): better epithelial-barrier preservation and an M1→M2 shift; strongest at the most aggressive modulation.
- **IL-10 deficiency** simulation: amplified/prolonged M1 response but dampened M2 — reproducing the *dual role* of IL-10 seen in Huaux et al. (1998) knockout studies (worse acute inflammation, less fibrosis).

### The explicit hand-off to the next phase

The paper's Discussion states the intent directly: the ODE model is "a foundation for the future development of a **virtual tissue model**" of macrophage–epithelial cell interactions. It sketches two routes — (a) use the ODE output as inputs to a higher-level tissue patch (à la Sego et al. 2020 COVID-19 CC3D model), or (b) translate the ODE model directly into a single-scale CC3D virtual tissue. It notes that **granuloma formation and fibrosis are inherently spatial** and cannot be represented by well-mixed ODEs — which is the whole motivation for going spatial.

**Tooling from the published work:** all ODE work is in **Tellurium** (Python, SBML-based) Jupyter notebooks, run in Google Colab. See `research_materials_index.md` for the exact notebooks (Full model, epithelial and macrophage submodels, parameter scans, LHS, supplementary).

---

## 3. Where the project is now (Summer 2025 state)

Summer 2025 was the kickoff of the virtual-tissue phase, run as an in-person undergraduate research program (May 19 – June 28, plus 2 remote weeks). The plan (`2025 Summer Research Plan`) organized work into a **modeling track** and an **experimental track**.

### Conceptual design is done

The core architecture for coupling the ODE model to a spatial tissue model has been worked out on paper (fully transcribed in `Model_Notes_digitized.md`). In brief:

- The **ODE model acts as a signal-generating layer.** It outputs cell-population and cytokine concentrations that become **inputs to the tissue model**: a pro-inflammatory signal (from M1 / damaged epithelium), an anti-inflammatory signal (M2 background), and concentrations used to scale spatial quantities (e.g. seeding of damaged epithelial cells), plus — later — growth factors and MMPs.
- The **tissue model** is a layered lattice: an **epithelial layer** (secretes TGF-β, upregulated by anti-inflammatory signal), a **mobile cell layer** (fibroblasts, myofibroblasts; secretion of TGF-β/ECM; chemotaxis), and a **lumen layer** (where ECM is deposited, reducing medium).
- Planned **diffusion fields:** growth-factor field, pro-inflammatory field, ECM field, and (later) an MMP field.
- **Biological target:** small-airway remodeling / subepithelial fibrosis, produced when a persistent type II (M2/TGF-β) response drives fibroblast → myofibroblast differentiation and excessive ECM/collagen deposition. ~~Granuloma formation (macrophage collections walling off persistent PM, with a necrotic core) is the second pathology of interest.~~ *[Superseded 2026-07-26: granuloma retired from scope — it requires tissue-layer macrophages, which v1 does not have, and belongs to a different disease context. See A13.]*

> *[Superseded 2026-07-26 — the three bullets above.] The tissue layer contains **no macrophages**; they are represented only in the ODE layer. Tissue cell types are stationary epithelium (healthy/damaged) and mobile fibroblasts/myofibroblasts. Layer order, outer to inner, is fixed outer boundary → subepithelial compartment → epithelium → lumen (the earlier ordering placed fibroblasts between epithelium and lumen). ECM deposits subepithelially, not into the lumen. The pro-inflammatory field is demoted to an ODE scalar for v1. See `Model_Notes_digitized.md` §D.*
- **Driving research question:** *How does antioxidant treatment (simulated via parameter changes) affect airway remodeling and fibrosis?* — the spatial analog of the antioxidant result already shown in the ODE paper.

### A working spatial prototype exists

There is an existing CompuCell3D prototype — the **"M1 to M2" model** (`Old CC3D M1 to M2 files/`) — that predates the virtual-tissue plan and serves as the proof of concept. It implements:

- M1 and M2 macrophage cell types on a lattice with volume constraints;
- an **LPS** (inflammatory stimulus) field, plus **P** (pro-inflammatory) and **A** (anti-inflammatory) diffusion fields;
- **secretion rules** — M1 secrete P as a function of local LPS (inhibited by local A); M2 secrete a baseline of A;
- **threshold-based phenotype transitions** — an M2 flips to M1 when it sees P above a threshold (~40), an M1 flips to M2 when it sees A above a threshold (~45);
- a **parameter scan over LPS concentration** with per-run logging of M1/M2 counts.

This validates the basic CC3D mechanics (cell types, fields, secretion, transitions, parameter scans) that the full virtual-tissue model will build on. Model design rationale is documented in `Macrophage differentiation in homeostasis versus during inflammation CC3D.docx`.


---

## 4. Open questions carried into the next phase

These are the unresolved design questions from the 2025 notes that should drive the next block of work:

1. **Architecture:** multi-scale (ODE output feeds a separate tissue patch) *vs.* fully translated single-scale CC3D model *vs.* ODE integrated with an agent-based layer? The current lean is ODE-as-signal-layer feeding a single-scale CC3D tissue, following the Sego et al. strategy.
2. ~~**Which cells and what properties/structures** must be represented to observe the disease states we care about? (Minimum viable set appears to be: epithelial healthy/damaged, macrophage M1/M2, fibroblast/myofibroblast, plus cytokine/ECM fields.)~~ **Resolved 2026-07-26.** v1 tissue set is: stationary epithelium (healthy/damaged) and mobile fibroblasts/myofibroblasts, plus a growth-factor field and an ECM field. Macrophages stay in the ODE layer (A13).
3. **What behaviors are necessary to *observe* disease states** (fibrosis, granuloma), and what states do we expect to see?
4. **Signal design:** should the M2:M1 ratio — or better, the anti/pro (A/P) ratio — be the inflammatory signal that recruits fibroblasts and drives epithelial-layer fragmentation? What does a pro-inflammatory signal do to the tissue?
5. **TGF-β modeling:** latent vs. activated TGF-β — what triggers activation? How is the initial (steady-state) cytokine field seeded?
6. **Grounding:** are there existing epithelium or fibroblast CC3D models we can reuse? Related CC3D models to explore are in the literature folder. What variables did previous fibrosis models track? What therapies are worth simulating (this tells us what must be represented)? How do existing CC3D models implement an ODE layer?

---

## 5. Recommended next steps

**Immediate (get oriented / unblock modeling) for the PI:**

- Work through the CompuCell3D tutorials and learn how to run CC3D in the shell, including running the existing `Old CC3D M1 to M2` prototype to see the mechanics in action.
- Run the published ODE notebooks in Tellurium/Colab (Full model + submodels) to reproduce baseline behavior and understand the signals the tissue model will consume, in the shell
- Literature review (Zotero): existing math/CC3D models of **lung fibrosis and granuloma formation**, and the biology of fibroblast→myofibroblast differentiation, TGF-β activation, and ECM/MMP turnover. Key starting references already in hand: Sego et al. 2020 (CC3D COVID tissue model), Torres et al. 2019 (granuloma/apoptosis approach), Deng et al. 2023, Huaux et al. 1998.

**Building the virtual tissue:**

*[The four bullets below are superseded by the v1 scope — 2026-07-26. Corrected versions follow.]*

- ~~Stand up the layered geometry (epithelial / mobile-cell / lumen layers) and the four diffusion fields (growth factor, pro-inflammatory, ECM, later MMP).~~ → Stand up geometry **outer boundary / subepithelial compartment / epithelium / lumen** and **two** fields (growth factor, ECM). P is an ODE scalar; MMP is v2.
- ~~Wire the ODE outputs into the tissue model as the pro/anti signals and scaling concentrations (start with a static, steady-state cytokine field, then make it dynamic).~~ → Wire **two scalars**, `S_M2` (uniform additive growth-factor source) and `R_fib` (fibroblast recruitment rate), from a cycle-averaged ODE reduction that drifts upward across exposure cycles (A11, A15).
- Add fibroblast and myofibroblast cell types with TGF-β/ECM secretion and chemotaxis; implement fibroblast→myofibroblast differentiation driven by the anti-inflammatory/TGF-β signal. *(unchanged)*
- ~~Implement ECM deposition into the lumen layer as the fibrosis readout; add granuloma mechanics (apoptosis/necrosis tracking, multinucleated giant cells) following the Torres et al. 2019 approach.~~ → Implement **subepithelial** ECM deposition, with **collagen area fraction** as the primary readout and lumen area as a secondary geometric output. Granuloma mechanics are retired from scope (A13).
- **New:** locate the `S_M2` threshold at which the lesion transitions from focal (patterned by epithelial damage) to diffuse (uniform conversion) — the headline v1 experiment (A14).
- Reproduce the **antioxidant intervention** experiment spatially (parameter changes) and compare remodeling/fibrosis outcomes to the ODE prediction.

**Data to request from collaborators to support calibration (later):**

- Additional epithelial wood-smoke exposure data at **early time points (0–5 h)**, which the current model is under-constrained on.
- Refine ODE parameter estimates against the new data.
- Identify existing published data that can be cited for parameter estimates


---

## 6. Mini-glossary

- **ODE model** — ordinary differential equation model; tracks concentrations over time, assumes a well-mixed (non-spatial) population.
- **CompuCell3D (CC3D)** — an open-source framework for spatial, cell-based ("virtual tissue") simulation using the Cellular Potts / Glazier–Graner–Hogeweg model, where each cell is a patch of lattice sites that evolves by a Monte Carlo energy-minimizing process. Fields (cytokines, PM) are modeled by diffusion equations.
- **Tellurium** — a Python environment for building/simulating biochemical ODE models (SBML-based); what the published model is written in.
- **M0 / M1 / M2** — undifferentiated / classically activated (pro-inflammatory) / alternatively activated (anti-inflammatory, pro-repair) macrophages.
- **Type I vs. type II response** — early pro-inflammatory (M1) phase vs. later anti-inflammatory/repair (M2) phase. Persistent type II drives fibrosis.
- **P / A** — lumped pro-inflammatory / anti-inflammatory cytokine concentrations.
- **TGF-β** — transforming growth factor beta; M2-secreted signal that activates fibroblasts and drives their differentiation to myofibroblasts.
- **Fibroblast / myofibroblast** — connective-tissue cells; myofibroblasts (differentiated fibroblasts) produce excessive ECM/collagen — the cellular basis of fibrosis.
- **ECM** — extracellular matrix (collagen, etc.); excessive deposition = fibrosis / airway thickening.
- **MMPs / TIMPs** — matrix metalloproteinases and their tissue inhibitors; regulate ECM turnover.
- **Granuloma** — organized collection of macrophages (with a necrotic core) that walls off persistent material the cells cannot clear.
- **PM** — particulate matter (e.g., PM2.5 from wood smoke).

---

*See `research_materials_index.md` in this folder for the full annotated list of notebooks, code, data, figures, and documents.*
