# Jones lab assay programme, draft ask, 2026-10-29

Scope: plate-reader work (ELISA, cell-lysate ELISA, MTT/CCK-8, LDH). No imaging, no migration. Same design logic as the macrophage pro/anti cytokine measurements for the JTB paper, different cells. Each assay is listed with the model parameter it pins (see `calibration_table.md`). Order is by value per effort.

## Cells and stimuli

- Fibroblasts: HFL1 (matches the chip) or any lung fibroblast line on hand.
- Epithelium: Calu-3 (matches the chip), BEAS-2B or A549 (matches the Calcabrini data the ODE was validated on). Any one is fine; note which.
- Smoke: wood-smoke extract (WSE) if obtainable; cigarette-smoke extract as a stated proxy otherwise. Dose series, not one dose.
- Recombinant TGF-β1 and IL-6.

## Assay 1. Epithelial secretion under smoke extract (highest value)

- Epithelial cells, WSE dose series (vehicle plus 3 to 4 doses), conditioned medium collected at 6, 24, 48, 72 h.
- ELISAs: TGF-β1, IL-6, IL-8. Plus LDH on the same medium.
- Pins: healthy-exposed vs damaged secretion for G and for P; the A19b ratio (currently 10:1, free); a check on A19a (ODE says 2:1); decay in medium from the time course; the dose at which LDH rises (where the chip sits relative to damage).
- Note: "damaged" has to be operationalized. Options: the high-WSE wells, or a membrane-damage marker on the same plate. State which.

## Assay 2. Fibroblast response to TGF-β1

- Fibroblasts, TGF-β1 dose series (0, 0.1, 0.5, 1, 5, 10, 50 ng/mL; 50 is the chip's perfusion), 24, 48, 72 h.
- Readouts: α-SMA by cell-lysate ELISA; procollagen I C-propeptide (PICP) in medium; TGF-β1 in medium (autocrine output, with and without pretreatment).
- Pins: conversion threshold (EC50 for α-SMA); activation rate (time to α-SMA plateau, currently off by about a day); relative collagen output fibroblast vs myofibroblast (sets the ECM quantum ratio); fibroblast and myofibroblast autocrine G secretion (currently 0.005 and 0.1, both free).

## Assay 3. MMP and TIMP

- Epithelial cells with IL-6 dose series and with WSE: MMP-2 and MMP-9 ELISA in medium at 24 and 48 h.
- Fibroblasts with and without TGF-β1: TIMP-1 ELISA.
- Pins: epithelial MMP source and its P dependence; myofibroblast TIMP term. Anchors the model's only negative loop to data from the same cells.

## Assay 4. Proliferation

- Fibroblasts, TGF-β1 dose series and IL-6 dose series, MTT or CCK-8 at 24, 48, 72 h.
- Pins: mitosis gate (0.225) and the new P-on-proliferation coefficient.

## Assay 5. Conditioned-medium transfer (H7 in a dish)

- Medium from Assay 1 wells (vehicle and exposed) applied to fibroblasts; α-SMA lysate ELISA and PICP at 48 h.
- Pins: nothing numerically new, but it tests the ordering the model predicts (exposed-epithelium medium activates fibroblasts more than vehicle medium) and is the tissue-layer version of the chip's mono-vs-co-culture comparison. A clean result is a figure in the paper.

## What the model gives back

- Every assay has a model readout to compare against, so the lab gets a modelling figure for each dataset, not just a parameter.
- Assay 1 and 2 together let the paper state G in ng/mL-equivalent units for the first time.

## Not in scope here

- Migration and chemotaxis (needs imaging; chemotaxis λ stays free, cited from literature).
- The focal-vs-diffuse spatial experiment (needs imaging; a possible later project if a microscope becomes available).
