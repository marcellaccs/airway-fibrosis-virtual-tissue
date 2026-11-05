# Citation Gap Report — Small-Airway Remodeling Lightning Talk

**Reviewer role:** senior academic reviewer (internal)
**Date:** 2026-07-22
**Reviewed:** `docs/Hackathon_Lightning_Talk_-_Small-Airway_Remodeling (1).pptx` (8 slides), cross-referenced against `docs/2025_project_status.md`, `docs/Model_Notes_digitized.md`, and the collected literature in `literature/` (`bio_lit`, `cc3d_lit`, `math_models_lit`) plus `literature/references.bib`.
**Purpose:** synthesize the core argument, map the deck's structure, and isolate every major claim or assumption that is currently presented without a citation. Each gap is scored for whether supporting evidence already sits in your library or must be sourced.

## 1. Core argument, in one pass

The talk advances a single causal chain and one intervention corollary:

- Repeated wood-smoke PM inhalation injures small-airway epithelium and triggers the innate immune response.
- Macrophage polarization steers the outcome: a self-limiting M1 (Type I) phase *should* resolve, but repeated exposure locks in a persistent M2 (Type II) state.
- Persistent M2 / TGF-β signaling activates fibroblasts, drives myofibroblast conversion, and deposits excess subepithelial ECM (collagen).
- The result is subepithelial fibrosis and airway-wall thickening — a **spatial** remodeling of tissue architecture that a well-mixed ODE model cannot capture.
- Therefore a spatial (CompuCell3D) model is needed; the published ODE model becomes the signal-generating layer, and the headline in-silico experiment is whether antioxidant intervention (shifting the local A/P balance back toward resolution) limits ECM deposition.

The argument is coherent and the "well-mixed ODE cannot represent a spatial process" motivation is your strongest, best-supported move. The weakness is evidentiary, not logical: almost every biological and epidemiological premise in that chain is asserted without a citation on the slide, even though your library already contains support for most of them.

## 2. Structure map of the deck

| Slide | Function in the argument | Load-bearing claims |
|---|---|---|
| 1. Title | Framing | — |
| 2. Biological Background | Establishes the full causal chain (injury → M1/M2 → TGF-β → fibrosis) | C1–C5 |
| 3. Problem Motivation | Establishes significance (global burden; remodeling = irreversibility) | C6–C7 |
| 4. Modeling Goals (hypothesis) | States the central hypothesis + intervention corollary | C8–C9 |
| 5. Modeling Goals (design) | Operationalizes readouts (ECM, myofibroblast density, wall thickness vs A/P) | A1–A3 |
| 6. Feasibility & Plan | Justifies CC3D; states expected results | C10–C11 |
| 7. Resources | Bibliography (4 references only) | — |
| 8. Potential Teammates | Recruiting ask | — |

Observation: the entire evidentiary burden sits on slides 2–4, but the only citations in the deck (slide 7) are the ODE foundation (Torres 2024), two CompuCell3D methods papers (Sego 2020, Swat 2012), and one polarization review (Ma 2020). Three of the four references support *method and foundation*; only Ma 2020 backs any biological premise. The biology and epidemiology of slides 2–3 are effectively uncited in the talk itself.

## 3. Bibliography infrastructure gap (fix this first)

There is a large disconnect between what you have read and what is citable:

- `references.bib` contains **6 entries** (Torres 2024, Torres 2019, Sego 2020, Swat 2012, Ma 2020, Huaux 1998).
- `literature/` contains **~26 collected PDFs**, of which only Sego and Swat also appear in the `.bib`. Roughly **24 papers you have gathered are not yet in the bibliography** and cannot be cited cleanly.
- `literature/notes/` is **empty** (only `.gitkeep`), despite the `CLAUDE.md` convention of one reading-note file per cite key. There is no captured evidence trail linking any paper to any claim.
- The deck cites only 4 of the 6 bib entries and none of the 24 uncited PDFs.

Net effect: most of the gaps below are *closable from material already in hand* — the problem is that the evidence is not wired into the bibliography or onto the slides.

## 4. Claim inventory — uncited claims and assumptions

Status key: **In library** = support already collected, add citation; **Partial** = related paper exists but does not fully cover the claim as worded; **Gap** = no supporting source in the collection, must be sourced.

### Biological / empirical claims (Slides 2–3)

| ID | Claim (as presented) | Slide | Citation status | Candidate support already in `literature/` |
|---|---|---|---|---|
| C1 | Repeated wood-smoke PM injures small-airway epithelium and triggers the innate immune response | 2 | Uncited | **In library:** Roscioli 2018 (wildfire-smoke extract → epithelial barrier dysfunction), Hewitt & Lloyd 2021, Kato & Schleimer 2007 |
| C2 | Macrophages (M1/M2) steer the response; the early M1 phase should resolve, but repeated exposure drives a persistent M2 / Type II state | 2 | Uncited on slide | **In library:** Ma 2020 (in bib), Hiraiwa & van Eeden 2013 (macrophages + air pollutants), Cheng 2021, Ge 2024 |
| C3 | Persistent M2 signaling (TGF-β) activates fibroblasts → myofibroblasts that deposit excess ECM/collagen beneath the epithelium | 2 | Uncited | **In library:** Allen & Spiteri 2001 (growth factors incl. TGF-β in fibrosis), Cheng 2021, Ge 2024. *Note: a direct TGF-β → myofibroblast primary reference would be stronger than these reviews* |
| C4 | Result is subepithelial fibrosis and airway-wall thickening; fundamentally a spatial change in tissue architecture | 2 | Uncited | **In library:** Varricchi 2024 (airway remodelling, asthma), Nho 2022 (biomechanics of lung fibrosis, supports the "spatial/mechanical" framing) |
| C6 | Wood-smoke PM is a major driver of chronic airway disease (COPD, asthma) worldwide, especially where biomass fuels are used for cooking/heating | 3 | Uncited | **Gap.** Wang 2024 touches the global CRD burden but not biomass-fuel exposure. Needs a GBD / WHO household-air-pollution epidemiology source (not currently in the library) |
| C7 | Remodeling is the structural step that turns reversible inflammation into fixed airflow limitation | 3 | Uncited | **Partial.** Varricchi 2024 covers remodeling in asthma; "fixed airflow limitation" is COPD-specific and needs a COPD remodeling reference |

### Hypotheses and intervention claims (Slides 4–6)

| ID | Claim (as presented) | Slide | Citation status | Notes |
|---|---|---|---|---|
| C8 | Remodeling emerges when repeated PM exposure sustains a Type II response long enough to drive fibroblast→myofibroblast conversion and subepithelial ECM accumulation | 4 | Uncited (this is your hypothesis) | Legitimately novel and may stand uncited *as a hypothesis*, but its premises are C2–C3 and should carry their support. Precedent that this class of mechanism has been modeled: Brown 2011 (ABM, inflammation+fibrosis after **particulate** lung exposure), Cogno 2022, Islam 2023, Hao 2015 — none currently cited |
| C9 | Shifting the local balance toward resolution (antioxidant intervention) limits ECM deposition and slows remodeling | 4–5 | Uncited | **In library:** Lee 2023 (antioxidant/curcumin, Nrf2 vs PM-induced pulmonary injury), Wang 2024 (dietary antioxidants ↔ CRD). Also your own ODE antioxidant result (Torres 2024). The *biological* link is supportable; the *parameter mapping* is an assumption (see A4) |
| C10 | CompuCell3D natively handles multiple cell types, movement/chemotaxis, differentiation, and diffusing cytokine/ECM fields | 6 | Cited only via slide 7 (Sego, Swat) | Method claim is fine; consider an inline cite |
| C11 | Recurring exposure will yield progressive subepithelial fibrosis; antioxidant intervention will reduce it | 6 | Uncited (predicted result) | Prediction, not a claim — acceptable uncited, but framing it as "expected" invites a "based on what?" question; anchor to C8/C9 support |

### Modeling assumptions presented as given (Slides 4–6, and design notes)

These are not literature claims but design choices stated without justification. A reviewer or collaborator will press on each.

| ID | Assumption | Where | Why it needs defending |
|---|---|---|---|
| A1 | The A/P (or M2:M1) ratio is the master signal that recruits fibroblasts and drives remodeling | 5; notes B.4 | No empirical citation links a specific A/P ratio to fibroblast recruitment; this is a modeling posit and should be labeled as such |
| A2 | TGF-β is treated as the dominant profibrotic M2 signal | 2, 4 | Your own notes (B.3) list PDGF, IL-4/IL-13, CCL18 and EMT as parallel drivers; reducing to TGF-β is a simplification that should be stated |
| A3 | Fibrosis readout = ECM deposited into a "lumen layer" that reduces medium | notes B.7 | An abstraction of a 3D histological process; needs a stated mapping to a measurable (wall thickness / collagen area) |
| A4 | Antioxidant therapy is represented purely by parameter changes | 4–5; status §5 | Which parameters, and the evidence that antioxidants act on those pathways, is unspecified (Lee 2023 could ground the target pathways) |
| A5 | Wood-smoke exposure enters as a Boolean on/off switch (no dose–response) | status §2 | Acknowledged internally as "no dose–response data exist"; this limitation is not surfaced in the talk and undercuts C6-style dose/threshold language on slide 5 |
| A6 | A persistent Type II signal *alone* is sufficient to generate subepithelial fibrosis | 4–5 | Strong monocausal claim; Nho 2022 (mechanics) and the EMT pathway in your notes suggest fibrosis is multifactorial. Soften to "sufficient in-model" or justify |

## 5. Unused precedent (a different kind of gap)

Your `cc3d_lit` and `math_models_lit` folders contain directly relevant modeling precedents that the feasibility and novelty framing never cites. Not citing them makes the work look less grounded than it is, and invites the "has this been done?" question:

- **Brown 2011** — agent-based model of inflammation and fibrosis after *particulate* lung exposure. This is the closest prior art to your exact hypothesis and is uncited.
- **Cogno 2022** (3D ABM of lung fibrosis), **Islam 2023** (ABM lung fibrosis), **Hao 2015** (ODE model of IPF), **Hao 2014** (renal fibrosis ODE) — fibrosis-modeling lineage.
- **Bahram Yazdroudi & Malek 2025** — optimal control to reduce M2 in lung fibrosis; direct precedent for your "intervention that shifts M2" experiment.
- **Rikard 2019** (multiscale ABM fibrosis + signaling), **Metzcar 2025** and **Crossley 2024** (ECM representation) — method support for the coupling and ECM field.
- **Chandrasegaran 2025**, **Zha 2024**, **Hutson 2017**, **Carpenter 2024**, **cc3d burns / Korkmaz 2024** — additional CompuCell3D / Cellular Potts precedents (fibrosis, lung tissue, toxicology, epithelial mechanics, immune response) that reinforce feasibility.

## 6. Priority gaps requiring new sources (not in the library)

Only two genuine holes cannot be closed from material you already have:

1. **Epidemiology / burden (C6).** No source in the library supports the "wood-smoke PM is a major global driver of COPD/asthma, especially biomass fuels" claim. Add a GBD or WHO household-air-pollution reference. This is the single most exposed uncited claim because it opens the talk's significance.
2. **Remodeling → fixed airflow limitation in COPD (C7).** Varricchi 2024 covers asthma remodeling; the COPD "irreversible airflow limitation" step needs its own reference.

Secondary (nice to strengthen, currently review-only): a primary TGF-β → myofibroblast differentiation reference to back C3 beyond the review articles.

## 7. Recommended actions

1. Export the ~24 collected PDFs from Zotero into `references.bib` so every claim above has a citable key.
2. Add inline citations to slides 2–4 mapping C1–C4, C9 to the in-library sources listed in §4.
3. Add a one-line "prior modeling work" note on slide 6 citing Brown 2011, Cogno 2022, and Sego 2020 to pre-empt the novelty question.
4. Source the two epidemiology/COPD references (§6) for slide 3.
5. Add an explicit "Simplifying assumptions" note (A1–A6) to the speaker notes or a backup slide; collaborators will ask, and naming them first is a credibility signal.
6. Backfill `literature/notes/` with short cite-key notes as claims are wired up, per the repo convention.
