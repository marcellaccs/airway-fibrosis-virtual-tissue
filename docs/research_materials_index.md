# Research Materials Index — Math Modeling in Toxicology

An annotated catalog of the project's working files. Most live in the research Drive folder
**`H:\My Drive\Math Modeling in Toxicology`** (a private Drive folder),
which is *separate* from the Google Classroom folder that holds student submissions. Use this as a map when you need to find code, data, figures, or documents.

> As you migrate code into this repo, copy the notebooks into `model/ode/` and the CC3D
> project into `model/cc3d/`, clearing notebook outputs before committing. Article PDFs stay
> in Zotero (see `literature/`).

---

## Start here (planning & orientation)

| File | Location | What it is |
|---|---|---|
| **2025 Summer Research Plan** | `2025 Summer Research/` · Google Doc (private) | Goals, modeling vs. experimental tracks, 6-week schedule, and a week-by-week objective appendix. The authoritative plan for the virtual-tissue phase. |
| **2025 summer research notes_small airway.pdf** | `2025 Summer Research/` | 7 pages of handwritten planning notes (big questions, fibrosis/granuloma biology, ODE→CC3D adaptation, tissue-model schematic). Transcribed in `Model_Notes_digitized.md`. |
| **Model Notes.pdf** | folder root | Single-page conceptual sketch of the immune-layer → tissue-layer coupling. Redrawn as `virtual_tissue_model_diagram.svg`. |
| **Tasks** | Drive · Google Doc (private) | Live task list for finalizing the manuscript (LaTeX/Overleaf migration, figure standardization, BibTeX bibliography, code cleanup, antioxidant-simulation idea). |

---

## Published model — code (ODE / Tellurium notebooks)

These reproduce the published JoTB model. Run these first to understand the signals the tissue model will consume. → migrate into `model/ode/`.

| Notebook | What it does |
|---|---|
| **Full model.ipynb** | The complete combined epithelial + M1/M2 + cytokine ODE model (in vivo, resident + recruited macrophages). |
| **Full model parameter scans.ipynb** | Parameter scans / exposure scenarios / antioxidant & IL-10 experiments for the full model. |
| **Epithelial cytokine model baseline and validation.ipynb** | Epithelial–cytokine submodel; validation vs. Calcabrini et al. (2004). |
| **Epithelial parameter scans + exposure events.ipynb** | Damage/repair (e3/e4) sensitivity and exposure-scenario runs for the epithelial submodel. |
| **Eh Ed phaseplane and bifurcations.ipynb** | Phase-plane and bifurcation analysis of the epithelial subsystem. |
| **Macrophage cytokine model baseline and validation** (Colab) | M1–M2–cytokine submodel; calibration to RAW 264.7 ELISA data; Morris sensitivity analysis. |
| **Macrophage cytokine model parameter scans + exposure events** (Colab) | Macrophage submodel parameter scans (m3, m6, m8, H_m2) and exposure events. |
| **Cytokine expression data.ipynb** | Processing of the experimental cytokine (MIP-2 / IL-10) expression data. |
| **supplementary.ipynb** | Supplementary Materials notebook accompanying the manuscript (includes a Gillespie/stochastic integrator variant). |

---

## Spatial prototype — CompuCell3D ("virtual tissue" starting point)

Folder: **`Old CC3D M1 to M2 files/`** — the proof-of-concept M1↔M2 spatial model. This is the scaffold the full virtual-tissue model builds on. → migrate into `model/cc3d/`.

| File | What it is |
|---|---|
| `M1_M2_P_A_paramscan.cc3d` (+ `...ParameterScan55/`) | CC3D project: M1/M2 macrophages, LPS/P/A diffusion fields, secretion + threshold phenotype transitions, LPS parameter scan. |
| `.../Simulation/M1_M2Steppables.py` | Core logic: M1 secretes P (function of local LPS, inhibited by A); M2 secretes baseline A; M2→M1 if local P > ~40; M1→M2 if local A > ~45; logs M1/M2 counts. |
| `.../Simulation/M1_M2.xml`, `parameters.py`, `ParameterScanSpecs.json` | CC3D config (cell types, fields, PDE solvers), tunable parameters, and scan specification. |
| `10_27_M1_M2_P_A_antimony_cc3d.../Simulation/Tellurium.py`, `TelluriumSteppables.py`, `Tellurium.xml` | Earlier variant embedding the ODE (Antimony/Tellurium) inside CC3D — the "ODE-as-signal-layer inside a cell-based model" approach. |
| `Macrophage differentiation in homeostasis versus during inflammation CC3D.docx` | Design doc for the prototype: objectives, entities, biological processes, and hypotheses/validation checklist. |

**Related (shared) folder:** `AirwayHybridModel` (owned by coauthor Jacob Brashear) — (private Drive folder) — likely relevant hybrid ODE/agent airway code; review when scoping the tissue implementation.

**Also in Drive:** a `virtual-tissue` subfolder — (private Drive folder).

---

## Manuscript & figures

| File | Location | Notes |
|---|---|---|
| **JTB-D-24-01036-pages-2.pdf** | Classroom folder root & research Drive | The submitted JoTB manuscript (full ODE model write-up). |
| **Working Draft** | Drive · Google Doc (private) | Google-Docs draft being migrated to LaTeX/Overleaf. |
| **Figures/** | research Drive | `Fig1.pptx`, `finalfig2.pdf/pptx`, `sensitivity_analysis.svg/png`, and all `LHS_*.png/eps` (Latin hypercube outputs for Eh, Ed, M1, M2, M1R, M2R, P, A). |

---

## Background literature (in project)

| File | Location |
|---|---|
| **Ma (2020)** — Polarization of Immune Cells in the Pathologic Response to inhaled particulates | Classroom folder / readings; also `molecules-28-02379.pdf` (Deng et al. 2023, macrophage polarization in lung disease) in Drive |
| **kfy309.pdf** — reading #2 | Classroom folder |
| **Dunster et al. (2014)** — resolution of inflammation model; **antioxidants-11-00873** | `Journal Club Summer2025/` |
| Journal-club examples & sign-up | `Journal Club Summer2025/` |

---

## Related reference models (from the paper's Discussion — worth reading for the tissue phase)

- **Sego et al. (2020)** — CC3D COVID-19 virtual-tissue / immune-response framework (the strategic template for our tissue model).
- **Torres et al. (2019)** — immune cell influx & macrophage polarization; apoptosis/necrosis approach for granuloma modeling.
- **Swat et al. (2012)** — multi-scale tissue modeling with CompuCell3D (the CC3D methods reference).
- **Huaux et al. (1998)** — IL-10 knockout / silica; basis of the IL-10-deficiency validation.
