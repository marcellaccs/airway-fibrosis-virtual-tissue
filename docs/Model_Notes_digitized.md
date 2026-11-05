# Digitized Handwritten Design Notes — Virtual Tissue Model

This file transcribes and lightly interprets Marcella's handwritten planning notes for the virtual-tissue phase. Two scanned sources are combined here:

- **`Model Notes.pdf`** — the single-page conceptual sketch of the immune-cell-interaction layer feeding the tissue layer (redrawn cleanly in `virtual_tissue_model_diagram.svg`).
- **`2025 summer research notes_small airway.pdf`** — a 7-page research notebook (agenda, big questions, fibrosis/granuloma biology, ODE→CC3D adaptation, and the tissue-model schematic).

Wording in quotes is transcribed from the notes; unbracketed prose is the author's intent expanded into full sentences. Editorial clarifications are in *[square brackets]*.

---

## A. The core concept sketch (`Model Notes.pdf`)

A conceptual diagram of how the immune model couples to the tissue. See the redrawn version in `virtual_tissue_model_diagram.svg`.

- An **Immune cell interaction layer** sits above the tissue and exchanges signals with it. It receives feedback on **damaged epithelium** and on **reduction in epithelium**, and it sends three outputs down into the tissue layer:
  - **Pro-inflammatory signal** — from M1 macrophages and epithelium (labeled "Pro (M1s, E)").
  - **TGF-β** — associated with M2 ("TGF-β (M2)").
  - **MMPs** — associated with M2 ("MMPs (M2)").
- The **Tissue layer** contains: **muscle**, an **epithelial layer** (epithelial cells; note "later add ø [differentiation] to fibroblasts"), **fibroblasts**, **myofibroblasts**, and **ECM**.
- Within the tissue, the wiring shown is: **fibroblast → myofibroblast** differentiation; fibroblasts/myofibroblasts and the signals drive **MMP**, **TGF-β**, and **↑ECM** (increased extracellular matrix). Damaged/depleted epithelium feeds back up to the immune interaction layer.

**Interpretation:** this is the "signal-generating layer → tissue layer" coupling in pictorial form. The immune/ODE layer produces the cytokine and enzyme signals (pro-inflammatory, TGF-β, MMPs); the tissue layer converts those signals into fibroblast activation, myofibroblast differentiation, and ECM accumulation — i.e., fibrosis.

---

## B. Research notebook (`2025 summer research notes_small airway.pdf`)

### B.1 Kickoff agenda (p.1)

1. Overview of plans & schedule + summer WhatsApp.
2. Calendar invite for Zotero.
3. Check in on CC3D / NanoHub installation.
4. First CC3D tutorial.
5. **Big questions** *(expanded in B.2)*:
   a. Multi-scale ODE + tissue model?
   b. Which cells to include, and what are their properties/structures?
   c. What behaviors will be necessary to observe disease states?
   d. What states do we expect?
   e. What happens in early stages of PM exposure to wood smoke?
6. **Research journals** — how to keep them: (a) summarize/paraphrase articles first, (b) use AI to summarize/paraphrase, (c) combine, or learn what you're missing, (d) keep citation references!, (e) "screenshot software w/ notes, so you don't reinvent the wheel."
7. Time logs.
8. Tuesday: Zotero / virtual check-in.
9. Wednesday: welcome brunch.

### B.2 More on the "BIG QUESTIONS" (p.2)

- Are there existing epithelium or fibroblast models we can study?
- What therapies are useful to simulate? — "this can tell us what needs to be represented in [the] model."
- How does fibrosis work at the cellular level; what variables were tracked in previous models?
- **Translate ODE to single-scale model** with: **M1/M2**, **epithelial cells**, **cytokines**, **fibroblasts?**
- Or **integrate ODE with agent-based?**

**Essentials to answer the big questions:**
- Review of existing math-model literature.
- Review of available CC3D models.
- The basics of CC3D.
- Review of existing biology literature.

### B.3 Fibrosis vs. granuloma biology (p.3)

**Pulmonary fibrosis:**
- M2 secrete **TGF-β**, which regulates fibrosis via activation of fibroblasts and their **differentiation to myofibroblasts**, which produce excessive ECM components such as **collagen**.
- M2 secrete **matrix metalloproteinases (MMPs)** and **tissue inhibitors of MMPs (TIMPs)** that regulate ECM turnover.
- M2 secrete **PDGF** (platelet-derived growth factor), **IL-4, IL-13, CCL18**, which stimulate fibroblast proliferation, migration, and collagen production.
- M2 secrete factors that induce **epithelial-to-mesenchymal** transition with fibroblast properties *[EMT — creating more fibroblast-like cells]*.
- Anti-inflammatory suppression is *[immunosuppressive and]* pro-fibrotic.

**Granuloma formation** *("collections of macrophages with a central necrotic core"):*
- M2 produce chemokines that attract and position immune cells.
- Macrophages fail to clear PM and form **multinucleated giant cells**, organizing into granulomas to "wall off" persistent material.
- Immunosuppression by M2 contains inflammation in the granuloma but prevents resolution.
- M2 promote fibrotic encapsulation.

**Clinical implications:**
- Pulmonary fibrosis.
- **Small-airway remodeling — thickening due to subepithelial fibrosis** *(starred in the notes as the primary target).*

### B.4 Research questions — "What if…" (p.4)

- The **M2/M1 ratio** gives an inflammatory signal — "or better yet **A/P**" *[anti-/pro-inflammatory ratio]*.
- This signal **recruits fibroblasts** and drives **fragmentation of an epithelial layer**? *(Note: epithelial-layer redundancy could be an issue.)*
- Or it recruits **fibroblasts AND mesenchymal cells**, which reduces the concentration of epithelial cells.
- **Fibroblasts/myofibroblasts secrete ECM** and add to the anti-inflammatory signal?
- **What would a pro-inflammatory signal do?**

### B.5 Cytokine-field ideas (p.5)

- A 2×2 phase-space sketch over axes **Anti (TGF-β)** [vertical] and **Pro** [horizontal], with the four quadrants labeled: High Anti/Low Pro, High Anti/High Pro, Low Pro/Low Anti, Low Anti/High Pro. *[A map of the qualitative regimes to explore.]*
- "Ideas for **initial static cytokine field** (at steady-state initially)."
- **Latent versus activated TGF-β?** — "What is required for activation?"

### B.6 Adapting the ODE model to CC3D (p.6)

**Basic idea:**
- Use the existing ODE model — epithelial (healthy & damaged), macrophage (resident or recruited M0, M1, M2), and pro- and anti-inflammatory cytokines — as a **signal-generating layer for virtual tissues.**
- Use a strategy similar to the **Sego et al. COVID-19 model** *[the CC3D multiscale tissue framework]*.
- **Goal:** model **small-airway tissue remodeling and fibrosis** driven by PM exposure and the resulting persistent **Type II** response.
- **One question:** how does treatment with **antioxidant** (simulated via parameter changes) impact airway remodeling and fibrosis?

### B.7 The tissue-model schematic (p.7)

**ODE model** (box) — outputs **cell population concentrations** and **cytokine concentrations**, plus (with question marks) **growth factors?** and **MMPs?**

**Outputs / inputs to tissue model** (arrows down from the ODE box):
- **Pro signal** (from M1).
- **Anti signal** (M2 background).
- **Cell concentrations for scaling** — e.g., the concentration of damaged epithelial cells scales the seeding of damaged cells in the tissue.

**TISSUE model** — a layered structure:
- **Epithelial layer** — "secretion of TGF-β upregulated by anti signal."
- **Mobile cell layer** — fibroblasts, myofibroblasts; secretion of TGF-β / ECM; chemotaxis.
- **Lumen layer** — "ECM is deposited into lumen layer and reduces medium."
- Marked with a **stationary source of ECM** and a **mobile source of ECM**.

**Fields:**
- **Growth-factor field** (sources: M2, damaged epithelial, fibroblasts [myofibroblasts low]).
- **Pro-inflammatory field** (sources: M1, damaged epithelial, healthy [low]).
- **ECM field** / ECM cells (myofibroblasts, damaged epithelial).
- **Later, an MMP field.**

---

## C. Synthesis — the design in one place

Putting the two sources together, the intended virtual-tissue model is:

1. **A signal-generating ODE layer** (the published model) producing pro-inflammatory (P) and anti-inflammatory (A) signals, macrophage/epithelial concentrations, and — as extensions — growth factors and MMPs.
2. **A layered CC3D tissue** (epithelial layer / mobile cell layer / lumen layer) whose cells (epithelial healthy+damaged, macrophage M1/M2, fibroblast, myofibroblast) respond to those signals via secretion, chemotaxis, differentiation, and ECM deposition.
3. **Coupled through diffusion fields** (growth factor, pro-inflammatory, ECM, later MMP) and through concentration-based scaling of spatial quantities.
4. **Reading out fibrosis** as ECM accumulation in the lumen layer (driven by TGF-β → fibroblast → myofibroblast) and **granuloma formation** as organized macrophage aggregation around uncleared PM.
5. **Driven experimentally** by the M2:M1 (or A/P) ratio as the master inflammatory signal, with the antioxidant intervention as the headline in-silico experiment.

*Open design questions extracted from these notes are carried into Section 4 of `2025_project_status.md`.*

---

## D. Corrections superseding this transcription (2026-07-26)

The sections above are preserved as a faithful record of the 2025 handwritten design. The
following decisions supersede parts of them for the v1 build. Full rationale and citations are
in `docs/model_assumptions_for_slides.md` (assumptions A7–A17); the updated schematic is
`docs/virtual_tissue_model_v1.svg`.

**D.1 No macrophages in the tissue layer (supersedes §B.7, §C.2, §A).** Macrophages are
represented only in the ODE layer. Tissue-layer cell types are stationary epithelium
(healthy/damaged) and mobile fibroblasts/myofibroblasts. The split is by timescale and mixing:
the fast, well-mixed immune subsystem stays in the ODE; the slow, spatially structured,
matrix-producing subsystem is spatial. (A13)

**D.2 Field sources revised (supersedes §B.7 "Fields").** The growth-factor field has a
*stationary* source (damaged epithelium), a *mobile* source (fibroblasts; myofibroblasts low),
and a **spatially uniform additive pedestal** `S_M2` carrying the ODE macrophage contribution.
M1 and M2 are no longer spatial sources. A uniform term contributes no gradient and therefore no
chemotactic force, but shifts the whole wall toward the differentiation threshold — giving two
orthogonal controls (how close the tissue is to tipping vs. where it tips first). (A14)

**D.3 Layer order corrected (supersedes §B.7 "TISSUE model").** The original schematic ordered
the layers epithelium → mobile cells → lumen, which places fibroblasts between the epithelium and
the lumen. Correct order, outer to inner, is: **fixed outer boundary → subepithelial compartment
(fibroblasts, myofibroblasts, ECM) → epithelium → lumen.** "Subepithelial" means beneath the
epithelium, i.e. away from the lumen. (A16)

**D.4 ECM deposits subepithelially, not into the lumen (supersedes §B.7 "Lumen layer").** The
measured lesion is collagen within the airway wall and lamina propria. The lumen narrows as a
*consequence* of wall thickening; intraluminal deposition would model a different lesion
(organizing/obliterative bronchiolitis). (A9)

**D.5 The "muscle" layer becomes a fixed outer boundary.** Non-deformable, non-secreting,
mechanically passive; exists to bias growth inward and to hold the slot an airway-smooth-muscle
cell type would occupy in v2. (A8)

**D.6 The pro-inflammatory field is demoted to an ODE scalar in v1.** Under D.1 nothing in the
tissue layer responds to the pro-inflammatory signal, so a spatial P field would be dead weight.
It returns in v2 together with EMT. (A17)

**D.7 EMT deferred to v2 (relates to §B.4, and the §A note "later add ø to fibroblasts").**
Deferred because the supporting evidence is thinner than it appears and because it would confound
the focal-vs-diffuse injury experiment. Retained as the designated v2 addition: EMT is loss of
adhesion plus gain of motility, which is what the Cellular Potts formalism represents natively.
(A17)

**D.8 Granuloma formation retired from scope (supersedes §B.3, §C.4).** Granuloma is macrophage
aggregation in tissue and is unbuildable without tissue macrophages. It also belongs to a
different disease context (hypersensitivity pneumonitis, pneumoconiosis) than the subepithelial
fibrosis targeted here. (A13)

**D.9 ODE→tissue interface reduced to two scalars.** `S_M2(cumulative exposure)` and
`R_fib(cumulative exposure)`, both from a cycle-averaged reduction of ODE output that is constant
within an exposure cycle and drifts upward across cycles. This replaces the three-arrow coupling
sketched in §B.7. (A11, A15)
