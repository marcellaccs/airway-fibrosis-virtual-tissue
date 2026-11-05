# Citation & Bibliography To-Do

Running list of follow-ups. Last updated 2026-10-31.
`literature/references.bib` currently holds **130 entries**, no duplicate keys. Every entry except
`Suzuki2010` (dropped) now carries a DOI or PMID.

## Open — blocking (needed before the talk or a manuscript)

- [x] ~~**DOIs for the 23 Gate B′ entries added 2026-10-30**~~ **Done 2026-10-31.** All 23 have DOI and PMID in
  `references.bib` (PubMed esummary, title/first author/journal/year checked), listed in
  `literature/zotero_identifiers_2026-10-31.txt` rather than a separate 10-30 file.
- [ ] **Verify abstract-level B′ numbers from full text:** cytokine D in `Francis1997`; macromolecule D in
  `Pluen2001`; MMP surface-diffusion D in `Collier2011`; MMP9 deactivation and TIMP rate constants in
  `Vempati2007`; the 15/28/46/79% closure figures in `Bequignon2020`.
- [ ] **No airway-tissue IL-6 half-life found.** `Castell1988` and `Nesbitt1992` are plasma/liver. Search
  BAL or ALI-culture IL-6 decay; Jones assay 1 time course is the fallback.
- [ ] **No wood-smoke source for any B′ pin.** All five rows rest on generic cytokine, IL-6, MMP-9 or
  TGF-β1 literature (cigarette smoke for `DiVincenzo2022`). Log as a limitation; search wood-smoke
  extract + epithelial wound repair and + fibroblast α-SMA time course.
- [ ] **Diffusion-range pass, 2026-11-01 (`G` and `P` λ scan ranges; dossier [78]–[98]; 21 entries added,
  `references.bib` now 151).** Follow-ups, in order of value:
  - **Verify from full text:** the ~70 µm pSMAD2⁺–Treg distance in `VanMeerbeeck2025` (a proximity
    statistic — check whether the paper gives a distribution); the per-cytokine effective D values in
    `Ross2018` (TNF-α, IFN-γ, IL-2 in live lymph node — the closest measured `P` D); the fitted TGF-β
    isoform D and decay in `Daher2026` (human skin); collagen-gel D for cytokine-sized proteins in
    `Hettiaratchi2018` (figure only).
  - **No measured TGF-β1 or IL-6 diffusion coefficient in tissue exists.** Both `G` and `P` D are
    derived from λ. Two routes would close it: micro-IOI (`Ross2018`) on a lung slice, or the
    `Daher2026` pipeline on a small-airway spatial-transcriptomics dataset. Log as a limitation.
  - **No tissue half-life for active TGF-β1.** `Wakefield1990`, `Philip1991`, `LaMarre1991` are plasma;
    `McCaffrey1994` is culture. `G` decay stays bounded (0.0072–0.45 /MCS), not pinned; the 0.01 /MCS in
    use is the latent end and needs the "lumped active + latent" reading of A2 stated wherever cited.
  - **Add APA entries for the 21 new keys** to `docs/validation_targets.md` § References and
    `docs/model_assumptions_for_slides.md` (not touched 2026-11-01: another session was editing the P
    rows and A13/A14). `Philip1991` has no DOI (PMID 1718991 only); `Young1980` and `Alotaibi2024` DOIs
    came from Crossref; add all 21 to the next `zotero_identifiers_*.txt` list.
  - **Decide the shared-D question (Marcella).** The literature supports one free D for `G` and `P`
    and does not support one tissue-effective D (binding differs). If the one-knob rule stays, D must
    move from 0.10 to ~2.5–4.5 px²/MCS; otherwise scan λ_G and λ_P separately (calibration_table § B′
    pins, 2026-11-01 rows). Either way D = 0.10 becomes a lower sensitivity arm, not the baseline.
  - **Solver cost of the upper `G` arm.** λ_G = 70 µm needs D ≈ 31 px²/MCS at k = 0.01 (~125 sub-steps
    per MCS, cf. 20 at D = 4.44). Run it once, or with the steady-state solver, before putting it in a PSCAN.

- [x] ~~**Complete metadata for the remaining abbreviated entries.**~~ **Identifiers done 2026-10-31:** DOI
  and/or PMID added to 94 entries (every DOI-less entry), so the wand can now fill author lists and
  volume/pages for the whole library. What remains is running the import, the next item.
  Non-PubMed DOIs came from Crossref: `Cogno2022` (Symmetry), `Hung2020`, `Plopper2020` (book chapter),
  `Albuquerque2021` (Atmosphere), `Higham2022` (ERS abstract), `Bennet2026` (not yet in PubMed).
  `MoranMendoza2008` has no DOI; its PMID is used. Year mismatches to fix at re-export: `Torres2024` is
  J Theor Biol **2025**; `Kim2004`, `Shin2019`, `Ren2022`, `Camp2013` are print-year +1.
- [ ] **Run the identifier import (Marcella, Zotero desktop).** Paste the three lists into the green
  wand (Add Item by Identifier): `zotero_identifiers_2026-08-02.txt` (16), `2026-10-11.txt` (3) and
  `2026-10-31.txt` (108, new). Skip any you already ran. Pulls full metadata **and** open-access PDFs,
  then re-export BibTeX over `references.bib`. Preferred over the `.bib`
  import, which carries no DOIs and so cannot trigger Zotero's "Find Available PDFs".
- [x] ~~Verify `Karvonen2013` author list.~~ **Confirmed via PubMed 2026-08-02** (Karvonen HM,
  Lehtonen ST, Harju T, et al.), PMID 23937155.
- [x] ~~**Decide what to do with the four conference abstracts / preprint.**~~ **Decided
  2026-10-28** (Consensus search for successors, Marcella's call): `Kong2023` → **replaced by
  `Kong2026`** (Respir Res 27:367, DOI 10.1186/s12931-026-03798-w, same group, peer-reviewed; added
  to `references.bib` and to `literature/zotero_identifiers_2026-10-11.txt`). `Higham2022` → **keep,
  cite as an abstract**; no successor exists (later Higham papers are ageing and PRISm). `Suzuki2010`
  → **dropped**; the non-monotone collagen point is carried by `Annoni2012` and `Polosukhin2021`
  (entry kept in the bib for provenance, marked do-not-cite). `Gunputh2026` → **keep, cite as
  preprint**. Bib notes updated for all four.
- [ ] **§3.5 wording pass in `validation_targets.md` (next validation-targets edit).** Three
  changes from the 2026-10-28 decision: (1) in §3.5 and in the Gate D "~9× gap" limitation, present
  the Higham 22 % luminal narrowing as abstract-level context (n = 37 COPD), not a Tier 2 target;
  (2) strip the `Suzuki et al. (2010)` mentions at §3.1 (two), §6 and the reference list, leaning on
  Annoni 2012 / Polosukhin 2021 for "collagen is not monotone"; (3) swap `Kong et al. (2023)` for
  `Kong et al. (2026)` at §3.1, §3.1 trap, §8.1 and the reference list. Same Suzuki/Kong swaps in
  `model_assumptions_for_slides.md` A12 notes and reference list.
- [ ] **Reconcile existing PDFs into `references.bib`.** The ~24 PDFs in `literature/bio_lit`,
  `literature/cc3d_lit` and `literature/math_models_lit` are still not all in the bibliography.
  `Rikard2019` was added 2026-08-02; `Brown2011`, `Cogno2022`, `Sego2020`, `Islam2023` and
  `Swat2012` are already in. Remaining gaps are mostly `bio_lit`.
- [ ] **Add inline citations to the deck.** Map claims in
  `Hackathon Lightning Talk - Subepithelial Fibrosis.pptx` to sources using
  `docs/model_assumptions_for_slides.md`; slide 6 currently names prior art but the biological
  premises on slides 2–3 are still uncited. Add a References/backup slide.

## Open — A19 sources (new 2026-08-09)

- [x] ~~**Add the nine A19 papers to `references.bib`.**~~ **Done 2026-10-31**: eight added with full
  PubMed metadata; `DiVincenzo2022` was already in (B′). DOIs are in `zotero_identifiers_2026-10-31.txt`. Cited in `model_assumptions_for_slides.md` A19
  and `evidence_dossier_assumptions.md` [22]–[30]; none are in the bibliography yet. All are
  peer-reviewed journal articles, so the Zotero identifier route applies:
  `Kumar2004` (Clin Exp Allergy), `LopezGuisa2012` (JACI), `Checa2016` (PLOS ONE),
  `Yang2014` (Am J Physiol Lung Cell Mol Physiol), `Baarsma2022` (SLAS Discovery),
  `Yao2021` (J Biol Chem), `DiVincenzo2022` (Antioxidants), `Daud2025` (Allergy),
  `Kraik2024` (Cells). Add DOIs/PMIDs to a `zotero_identifiers_2026-08-09.txt` alongside the
  2026-08-02 list, then re-export BibTeX.
- [ ] **Find a wood-smoke-specific replacement for `Checa2016` and `Baarsma2022` if one exists.**
  Both are the nearest available proxies (cigarette-smoke extract, diesel exhaust particles) for
  the claim that particulate exposure raises epithelial TGF-β1 output; a biomass/wood-smoke
  equivalent would close the last exposure-specificity gap in A19. Not found in the 2026-08-09
  Consensus pass.
- [ ] **Decide whether the damaged:healthy secretion ratio needs its own validation-target row.**
  A19 makes it a scanned parameter with no literature anchor; if it stays scanned, say so in
  `docs/validation_targets.md` rather than leaving it unlisted.

## Open — A7 scale-calibration sources (new 2026-09-04)

- [x] ~~**Verify the Tisler et al. (2020) migration speeds against the source figure.**~~ **Checked against
  the full text (PMC7052674) on 2026-09-07: there is no table and no in-text value.** The Results give only
  the significance pattern (IPF cells faster than normal on both matrices, P < 0.001; both cell types faster
  on the aligned IPF scaffold, P < 0.05) and the Fig. 3B legend gives only "average speed (μm/h)" with
  "cumulative cell numbers between 100 and 200 with at least three independent experiments". Metadata
  confirmed: imaging **every 30 min over 72 h**; note Methods say "at least four independent runs" while the
  legend says "at least three". The four values therefore **stay *(verify)*** and can only be cleared two
  ways — see the new open item below. *(2026-09-07)*

- [ ] **Clear the Tisler2020 *(verify)* flag, by one of two routes.** Either (a) digitize Fig. 3B at full
  resolution (WebPlotDigitizer against the labelled µm/h axis, saving the digitization to
  `data/processed/`), or (b) email the corresponding author, **Paul J. Campagnola** (UW-Madison), for the
  underlying values. Route (a) is enough for a slide; route (b) is worth doing before a manuscript, since
  62.4 s/MCS — and therefore every biological time this model reports — hangs off the 10.7 µm/h figure.

- [x] ~~**Add the nine A7 papers to the Zotero identifier list.**~~ **Done 2026-10-31**: all nineteen (nine
  A7 + ten 2026-09-07) have DOI/PMID in the bib and are in `zotero_identifiers_2026-10-31.txt`. `Devalia1990`, `Mariassy1984`,
  `Plopper2020`, `Tisler2020`, `Asano2017`, `Mio1992`, `Holz2004`, `Molina2025`, `Suganuma1995` are now in
  `references.bib` but most have abbreviated author lists and no volume/pages. `Tisler2020`
  (doi 10.1152/ajplung.00087.2019, PMID 31774302) and `Asano2017` (doi 10.14814/phy2.13281,
  PMID 28507166) have verified DOIs; the rest need PMID lookup. Put them in a
  `literature/zotero_identifiers_2026-09-04.txt` alongside the 2026-08-02 and 2026-08-09 lists and
  re-export BibTeX. **Add the ten new 2026-09-07 entries to the same list**: `Liesker2009`, `Wilson1997`,
  `Bourdin2007`, `Kim2004`, `Zajicek1992`, `RecillasRoman2021`, `Capistrano2016`, `Albuquerque2021`,
  `Wong2004`, `Shin2019` — all peer-reviewed and PubMed-indexed, all currently
  first-author-plus-"and others" with blank volume/pages and no DOIs.
- [x] ~~**Find a second, independent pixel↔µm anchor that is not epithelial cell width.**~~ **Found
  2026-09-07 — it is an ECM dimension, not a cell dimension: reticular basement membrane thickness.**
  `Liesker2009` (COPD 6.0 (1.8) µm vs control 4.8 (1.2) µm, n = 17/10), `Wilson1997` (healthy 3.19 ± 0.55 µm
  by light microscopy and 2.85 ± 0.86 µm by EM, n = 13 — two methods agreeing to ~0.35 µm) and `Bourdin2007`
  (diagnostic thresholds 5–7 µm, n = 50 COPD / 18 control). Measured in situ on the same section as the
  epithelium, which is exactly what the fibroblast-spread-area route could not give. Filed as a §7 anchor row
  with the resolution caveat: at 1.25 µm/px the healthy→COPD change is ~1 px, so RBM is a **layout check, not
  a model readout**. A better anchor came out of the same pass and is dimensionless: `Zajicek1992` gives
  14.8 ± 0.1 epithelial and 6.6 ± 0.1 fibroblast cells per 100 µm of bronchus, an **epithelial : fibroblast
  ratio of ≈ 2.2 : 1** checkable with no µm/px commitment. *(2026-09-07)*

- [ ] **Decide what to do with the ~30% spread the new anchors expose.** `Zajicek1992`'s linear epithelial
  density implies ≈ 6.8 µm per epithelial cell along the basement membrane (→ 0.85 µm/px at 8 px/cell) against
  the 10 µm width anchor (→ 1.25). Hamster and oblique sectioning explain some of it, but the honest way to
  quote µm/px from here is a range with a chosen value, which `validation_targets.md` §7 and the A7 limitations
  now do. Decide whether the deck says this or only the manuscript does.

- [ ] **`Eapen2021` full text — still the best route to a lamina propria thickness anchor.** Unchanged from
  the "validation sources" block below, but now higher value: with RBM thickness in hand, an αSMA⁺/mm² and
  lamina propria thickness figure from the same paper would give a **third** independent in-tissue dimension
  and a cell-density check on the subepithelial band (70 px / 87.5 µm until 2026-09-18; now 68 px / 85 µm after
  the epithelial-height rescale).

- [ ] **Find a small-airway-specific human epithelial cell *width* if one exists.** Still open after the
  2026-09-07 pass. `Devalia1990` is human but cultured and large-airway bronchial; `Mariassy1984` is in-situ
  morphometry but sheep and tracheobronchial. The nearest new source, `Kim2004`, *is* human and small-airway
  and reports **epithelial height 45 vs 35 µm** in resected severe-emphysema airways (P = 0.025, n = 25) — but
  that is almost certainly epithelial **layer** thickness in remodeled, goblet-hyperplastic tissue rather than
  a single-cell dimension, and it is abstract-level. Filed *(verify)* as a direction, not a value. Pulling the
  `Kim2004` full text to see how "epithelial height" is defined is the cheapest next step; if it turns out to
  be a per-cell measure it closes this item outright.

- [x] ~~**Decide the epithelial cell height.**~~ **Decided 2026-09-07 (recommendation, awaiting Marcella's
  sign-off): `TARGET_VOLUME_EPITHELIAL` 48 → 64 px**, i.e. 8 × 8 px = 10 × 10 µm. Three converging reasons:
  9.6 µm (Mariassy & Plopper, 1984) is 7.7 px, i.e. 8 to the nearest pixel; `Plopper2020` describes
  bronchiolar epithelium as **simple cuboidal**, and cuboidal means height ≈ width, which 6 × 8 is not; and
  A16 places the model in the small airway, so a flattened cell is the wrong shape for the stated tissue.
  Rationale and arithmetic written into `validation_targets.md` §7 and A7's limitations. *(2026-09-07)*

- [x] **Applied 2026-09-18** (`lab-notebook/2026/2026-09-18.md`): all four changes below are in, and the
  epithelial y-band is now *derived* from `EPITHELIAL_CELL_HEIGHT` (72–79; lumen fixed at 80–99, subepithelial
  band 4–71 = 68 px / 85 µm, not 70 / 87.5). Leaving the band at 6 rows made cells seed 16 px under target and
  produced a spurious −12.5% lumen narrowing. Residual: the rescaled config narrows more than the old one
  (about −8.6% vs −3.3% at MCS 3000, 4 seeds each), cause not isolated, so **narrowing numbers from before and
  after this change are not comparable**. The fibroblast |ΔCOM| (s/MCS) measurement was not re-run.
  Original spec, kept for the record: not done in the 2026-09-07 pass because it
  changes model behavior. Required together, in `parameters.py`: `TARGET_VOLUME_EPITHELIAL` 48 → **64**;
  `LAMBDA_VOLUME_EPITHELIAL` 30 → **22.5** (`V_ref/V_actual = 48/64 = 0.75`); `LAMBDA_SURFACE_EPITHELIAL`
  1.0 → **0.87** and epithelial contact energies `J` × **0.866** (`D_ref/D_actual = √48/√64`).
  `EPITHELIAL_FPP_TARGET_DISTANCE` is keyed to `EPITHELIAL_CELL_WIDTH`, which does not change, so the
  focal-point-plasticity block is untouched. Then a before/after run with a fixed `<RandomSeed>` to confirm
  the epithelial layer still holds together and the fibroblast |ΔCOM| measurement (and hence s/MCS) has not
  moved.

- [x] ~~**Find a wood-smoke / biomass fibroblast migration or proliferation figure.**~~ **Half-closed
  2026-09-07.** The *proliferation* half is closed by `RecillasRoman2021` — normal human lung fibroblasts +
  PAH-containing wood smoke extract, with a **trimodal growth-rate response** (0.5–1% WSE increases growth,
  2.5% decreases it without damage, 5–20% inhibits and damages) and, at 2.5%/3 h, raised total collagen plus
  upregulated TGF-β1, Col I/III, MMP-1, TIMP-1/2. `Capistrano2016` (biomass smoke extract on primary human
  lung fibroblasts) supports the exposure route. The *migration* half **does not close: no wood-smoke or
  biomass fibroblast migration figure appears to exist.** What does exist points the opposite way from the
  model's coupling — `Albuquerque2021` (biomass particles: motility unchanged to 125 µg/mL, migration and
  motility speed **decreased** at 250–500), `Wong2004` and `Shin2019` (cigarette-smoke proxies, migration
  inhibited). Filed as §7 rows and dossier entries [50]–[53]. *(2026-09-07)*

- [ ] **Reconcile the non-monotonic exposure response with the model's monotonic damage→activation coupling.**
  This is a modeling question the 2026-09-07 literature raised, not a citation gap. `RecillasRoman2021`'s
  growth-rate curve is hormetic and its ECM-signaling peak (2.5% WSE) sits at a dose that *reduces*
  proliferation; the migration sources agree that smoke suppresses fibroblast motility. A single scalar
  "exposure severity" driving both proliferation and motility upward cannot reproduce either limb. Decide
  whether v1 states this as a known limitation (cheapest) or v2 splits the exposure response into separate
  proliferative and migratory terms.

- [ ] **Consider `Huang2025` for the A19 exposure gap.** Already in `references.bib` (with DOI and PMID) but
  not yet used for A19. Wood-smoke PM2.5 on BEAS-2B cells plus a wood-smoke mouse model and 20 biomass-COPD
  patients — the closest biomass-specific *epithelial* source in the library,
  though IL-17a/NR1D1-focused rather than a TGF-β1 output measurement. It does not fully replace `Checa2016`
  and `Baarsma2022`, but it is better than nothing for the "particulate exposure alters epithelial signaling"
  claim, and it is peer-reviewed and PubMed-indexed.

## Open — validation sources (new 2026-08-02)

- [x] ~~**Pull full texts and extract numbers with dispersion**~~ **Obsolete 2026-10-31**: `Eapen2021` is
  tracked under the 2026-09-26 block (figure-only, digitize); `Kong2023` was replaced by `Kong2026`;
  `Higham2022` is kept as abstract-level context (2026-10-28). Original: for `Eapen2021` (αSMA⁺/mm² lamina
  propria, lamina propria thickness), `Higham2022` (luminal narrowing %, wall thickness by GOLD
  stage) and `Kong2023` (submucosal collagen %). Abstract-level values are not plottable. Put the
  extracted table in `data/processed/`.
- [x] ~~**Import `literature/zotero_import_2026-08-02.bib`**~~ **Obsolete 2026-10-31**: superseded by the
  identifier lists, which carry DOIs (the `.bib` cannot trigger Find Available PDFs). Original: (18 entries) into the small-airway /
  validation collection, attach PDFs, then re-export the whole library as BibTeX to overwrite
  `references.bib` with complete metadata. This one action closes the metadata item above.
- [ ] **Confirm the Islam et al. (2023) denominator** for collagen area fraction (whole domain vs
  tissue subregion). The 2–40% band comparison is meaningless if our denominator differs.
- [ ] **Attach PDFs for the EMT lineage-tracing set** (`Rock2011`, `Tan2021`, `Hung2020`,
  `HompsLegrand2023`) — cited in A17 but not yet in `literature/bio_lit`.
- [ ] **Backfill `literature/notes/`.** Still empty. Start with the five papers in the minimal
  validation set (`docs/validation_targets.md` §5), one note per cite key.

## Open — full-text extraction and prior art (new 2026-09-26)

- [x] **`Zou2014` full text read.** Numbers with dispersion extracted into
  `docs/validation_targets.md` §8.1. It is now the primary exposure-matched quantitative anchor.
- [~] **`Eapen2021` full text read — only partly closes the old §6 item.** Correlations, fold
  changes and the "shallow band deep to the Rbm" spatial description are extracted
  (`validation_targets.md` §8.2). **Group means and SDs for αSMA⁺/mm² and layer thickness exist only
  in Figs. 1c–e and 3b–d**; there is no table in the paper. Still *(verify)*.
- [ ] **Digitize three figure-only sources in one pass:** Eapen 2021 Figs. 1c–e and 3b–d,
  Tisler 2020 Fig. 3B. These are the last blockers on every Tier 3 readout in this project.
- [x] ~~**Add the prior-art modeling papers surfaced 2026-09-26 to `references.bib`.**~~ **Done
  2026-10-31**: `Hall2024`, `Warsinske2016`, `Hill2018`, `LeonardDuke2020`, `Camp2013` added with full
  metadata (`RoblesHernandez2025` was already in). DOIs in `zotero_identifiers_2026-10-31.txt`. Needed for the
  novelty framing in `docs/novelty_utility_review_2026-09-26.md` §2:
  `Hall2024` (ABM + spring-network, stretch and stiffness, latent TGF-β — the precedent for the
  planned v2 stiffness gating), `Warsinske2016` (fibroblast + epithelial co-culture ABM),
  `Hill2018` (morphoelastic asthmatic airway wall — the only other airway-wall model found),
  `RoblesHernandez2025` (biomass vs tobacco COPD: severe peribronchiolar fibrosis 60% vs 10%),
  `Camp2013` (biomass airway-predominant phenotype), `LeonardDuke2020` (multiscale lung fibrosis
  review). Collect DOIs into a new `literature/zotero_identifiers_2026-09-26.txt` for the wand.
- [ ] **Cite Brown 2011, Islam 2023 and Cogno 2022 in the manuscript's first two paragraphs.**
  Carried over from `citation_gap_report.md`; the novelty review confirms not citing them invites
  the "has this been done" question.
- [ ] **Decide whether `Zhao2018` needs a second biomass-vs-tobacco histology source.**
  `RoblesHernandez2025` is a candidate and is exposure-matched, but n = 20 samples total.

## Open — airway-on-a-chip comparator (new 2026-10-11)

- [x] ~~**Add `Bennet2026` to `references.bib`.**~~ **Done 2026-10-31** (DOI confirmed via Crossref). Bennet, T. J., Randhawa, A., Pieters, A., Caffrey,
  T. M., Solomon, T., Lyall, E., Huff, R. D., Schwartz, C., Xi, Y., Carlsten, C., & Cheung, K. C.
  (2026). Engineering a multilayer microfluidic airway-on-a-chip with tunable GelMA hydrogel for
  physiologically relevant aerosol exposure studies. *Scientific Reports*.
  **DOI 10.1038/s41598-026-69468-5** (verified from the article header). Start
  `literature/zotero_identifiers_2026-10-11.txt` with this DOI.
- [ ] **File the PDF in Zotero** under the small-airway / exposure collection. It is currently only
  in the chat upload, not in `literature/bio_lit`. (Per `CLAUDE.md`, PDFs do not go in the repo.)
- [ ] **Chase the supplementary material.** S3 describes the smoke generation and exposure system; if
  it reports PM2.5 concentration and exposure duration numerically, that is the first
  dose-matched-to-a-platform exposure figure available to this project and belongs in
  `validation_targets.md` §7.
- [ ] **Decide whether to contact the Cheung/Carlsten group (UBC).** Bears on
  `validation_targets.md` §3.7, which is currently gated on obtaining real biomass-exposed
  small-airway sections. Note Carlsten is also a plausible referee for the Frontiers special issue.
- [ ] **Cite `Hall2024` alongside H3.** Already logged on 2026-09-26 as prior art; it is now also the
  modeling precedent for the stiffness-gated latent-TGF-β mechanism that the GelMA stiffness knob
  makes testable.

## Open — A19 split and ODE provenance (new 2026-10-23)

- [ ] **Split A19 into A19a and A19b.** *Partly applied (2026-10-31 check): the A19a/A19b labels are in use
  in `model_assumptions_for_slides.md`, but the A19 heading and its source list are not yet split.* A19a: damaged epithelium secretes **pro-inflammatory**
  cytokine at about 2× the healthy exposed rate — ODE-anchored (`e5 = 0.1`, `e6 = 0.2`, Torres
  et al., Eq. 3 and Table 2), so it needs no external citation beyond the ODE paper itself.
  A19b: damaged epithelium is a **growth-factor** source at an uncalibrated ratio — a tissue-layer
  assumption with no ODE provenance, carried by `Kumar2004`, `LopezGuisa2012`, `Checa2016`,
  `Baarsma2022` and `Yang2014`. Those are already cited under A19; the work is separating which
  claim each supports.
- [ ] **Cite the ODE paper for the ODE's own parameter values** wherever the tissue docs quote
  `e3`, `e4`, `e5`, `e6` or the `r = e3/(e2 + e4)` balance. The bib entry exists as `Torres2024`
  (first author Bakry; now with DOI 10.1016/j.jtbi.2025.112159, PMID 40484121, published 2025);
  the citing is what remains.
- [ ] **Check the published JTB version** against the preprint PDF in `literature/math_models_lit/`
  before quoting parameter values in the Frontiers manuscript. Numbers above are read from the
  PDF in the repo, which is the submitted manuscript.

## Done

- [x] Worked five A7 items in one pass (Consensus, peer-reviewed only): verified `Tisler2020` against the full
  text (figure-only, confirmed), found the second pixel↔µm anchor (RBM thickness, plus a dimensionless
  epithelial:fibroblast ratio), decided the epithelial cell height (48 → 64 px, with the Module 8.2 rescale
  worked out), and half-closed the wood-smoke fibroblast gap (proliferation yes, migration does not exist).
  Ten sources added to `references.bib` (82 → 92; `Huang2025` was already in the library); `docs/validation_targets.md` §7 gained six anchor rows;
  `docs/evidence_dossier_assumptions.md` § Assumption A7 gained entries [43]–[54] and reviewer notes 7–11.
  *(2026-09-07)*

- [x] Sourced and filed the two A7 scale-calibration anchors (Consensus, peer-reviewed only): airway
  epithelial cell width and lung fibroblast migration speed, plus fibroblast doubling time for the
  GF-gated mitosis item. Wrote `docs/validation_targets.md` §7 (anchor table), § Assumption A7 in
  `docs/evidence_dossier_assumptions.md` ([31]–[42], seven supporting / five challenging), and an updated
  note under A7 in `docs/model_assumptions_for_slides.md`. Result: µm/px moves 1.5625 → 1.25, and the
  40 µm/h dermal placeholder is retired for a 6–11 µm/h lung figure. *(2026-09-04)*

- [x] Citation gap report of the lightning talk (`docs/citation_gap_report.md`). *(2026-07-22)*
- [x] Evidence dossier, 2–3 supporting/challenging papers per assumption
  (`docs/evidence_dossier_assumptions.md`). *(2026-07-22)*
- [x] Slide-ready model-assumptions list with in-text citations
  (`docs/model_assumptions_for_slides.md`). *(2026-07-22)*
- [x] Folded 21 verified papers into `literature/references.bib`. *(2026-07-22)*
- [x] Closed the two external gaps: biomass/COPD burden, and remodeling → fixed airflow limitation.
  *(2026-07-22)*
- [x] Added 14 scope/assumption sources for A7–A17 (`Brown2011`…`MoranMendoza2008`). *(2026-07-26)*
- [x] Added the "prior modeling work" note to the feasibility slide (Brown 2011, Islam 2023).
  *(2026-08-02, slide 6 of the Subepithelial Fibrosis deck)*
- [x] Added 14 validation-target sources and wrote `docs/validation_targets.md`. *(2026-08-02)*
- [x] Sourced support for the damaged-vs-healthy epithelial secretion assumption (Consensus,
  peer-reviewed only); wrote assumption **A19** in `docs/model_assumptions_for_slides.md` with an
  A14 cross-reference, and § Assumption A19 ([22]–[30], five supporting / four challenging) in
  `docs/evidence_dossier_assumptions.md`. *(2026-08-09)*

## Reference

- Source files: `docs/citation_gap_report.md`, `docs/evidence_dossier_assumptions.md`,
  `docs/model_assumptions_for_slides.md`, `docs/validation_targets.md`.
- Note: `citation_gap_report.md` and `evidence_dossier_assumptions.md` predate the v1 scope change
  (A13–A17) and still describe the old deck, which included tissue-layer macrophages. Treat them as
  dated records of the 2026-07-22 review rather than current spec.
