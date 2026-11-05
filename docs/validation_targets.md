# Validation Targets

**Question this doc answers:** when the v1 model produces a lesion, what published measurement do we
hold it against, and what would count as agreement?

**Status:** first pass, 2026-08-02. Numeric anchors below are taken from abstracts and reported
summary statistics; values marked *(verify)* need checking against the full text before they appear
in a manuscript or slide.

## 1. The constraint that shapes everything

A7 commits the model to **dimensionless, relative readouts**: no lattice-site-to-µm mapping, no
MCS-to-hours mapping. That is the right call for a two-week build, but it means:

- We **cannot** validate against an absolute thickness in µm, an absolute cell count per mm², or an
  absolute time-to-fibrosis.
- We **can** validate against dimensionless ratios (area fractions, percentages), directions of
  change, orderings between conditions, and spatial pattern statistics.

So validation is tiered. Tier 1 and 2 are achievable now; Tier 3 is what a calibration step would
later buy.

## 2. Three tiers

| Tier | What is compared | Achievable in v1 | Function |
|---|---|---|---|
| 1. Qualitative / pattern | Does the lesion look like the histology (subepithelial, focal, epithelium-adjacent)? | Yes | Sanity check. Failure here means the model is wrong, not uncalibrated. |
| 2. Ordinal / directional | Does condition A produce more collagen than condition B, in the same order as the literature? | Yes | The real test. This is where the model earns its claims. |
| 3. Absolute quantitative | Does collagen area fraction land in the published 4–15% band? | Only after calibration | Aspirational. Report as "consistent with" at most. |

Prior art sets the precedent for stopping at Tier 2. Islam et al. (2023) validated against mouse
data by comparing *dynamics and ranges* of collagen area fraction and cell populations, not
matched absolute values. Cogno et al. (2022) reproduced published results "qualitatively and
quantitatively" but leaned on shape agreement (a sigmoidal ECM dose–response) and a custom
severity index compared with published fibrosis indices. Yoshizawa et al. (2022) validated a liver
fibrosis ABM by matching the *spatial progression pattern* of collagen (periportal → bridging)
against histological sections rather than a scalar.

## 3. Readout-by-readout targets

### 3.1 Collagen area fraction (primary endpoint, A12)

Model output: collagen-field area over tissue area in the airway-wall cross-section.

*Revised 2026-10-30 (B′ kickoff).* With the volume-occupying ECM cell type
(`roadmap_revision_2026-10-29.md` §2.3) this becomes a **direct readout**: the number of lattice
pixels occupied by `ECM` cells in the subepithelial band divided by the band's area, the same
quantity a thresholded picrosirius or trichrome section gives. No field threshold is needed. The
burden field `C` stays as the stiffness input only and is no longer the collagen-area source. The
2026-10-29 outreach overlay (`docs/outreach/2026-10-29_torres_lab_night/analysis_fig.py`) already
computes the histology side of this on Zou et al. (2014) Fig. 4 (16% control vs 26% wood smoke in a
60 µm band; demonstration only); the model side is written in B′.

Comparable published measurements:

- **Human bronchial submucosa, COPD vs healthy:** 10.8% (IQR 8.0–15.1) vs 3.8% (0.7–4.8), Movat
  pentachrome, n=12 per group (Kong et al., 2023). *(verify)* Closest thing to a direct
  percentage-of-tissue anchor, but it is large-airway biopsy, not small airway.
- **In silico prior art:** 2–40% across source configurations (Islam et al., 2023). This is the
  band our own numbers should be compared against first, because it shares the modelling
  convention.
- **Rat wood smoke, 7 months:** collagen deposition area significantly increased in small airway
  walls vs clean air, at 4–7 months (Zou et al., 2014). Direction only; no percentage reported in
  the abstract.
- **Rat biomass PM2.5:** no structural change at 4 weeks, increased collagen deposition at 24 weeks
  (Li et al., 2024). This is the exposure-matched time-course target.

**Recommended target:** Tier 2. The model should place unexposed baseline near the healthy end of
the Islam band and chronic exposure several-fold higher, with the *ratio* exposed:control being the
reported quantity. A 2.5–3× increase over baseline is the ratio implied by Kong et al. (2023).

**The trap: collagen is not monotone with disease stage in human COPD.** The literature genuinely
disagrees, and the disagreement is compartment- and stage-dependent:

- Increased: Eurlings et al. (2014) found collagen raised in small airway walls already at GOLD II;
  Kong et al. (2023) in bronchial submucosa.
- Decreased: Annoni et al. (2012) found type-I collagen fractional area *lower* in COPD small
  airways; Higham et al. (2022) found collagen decreased and inversely correlated with elastin;
  Polosukhin et al. (2021) found reduced collagen density in severe COPD; Suzuki et al. (2010)
  found small airway wall collagen volume fraction *negatively* correlated with wall thickness.

Consequence for us: **validate against the early / animal wood-smoke phase, not against severe
human COPD.** The v1 model has no MMP or degradation arm, so it can only produce the accumulation
limb. State that explicitly rather than letting a reviewer find it. *(2026-10-30: B′ adds an MMP
field that removes ECM cells, so with `MMP_FIELD_ENABLED` on the model has a degradation arm and
this sentence applies only to the switch-off base condition. The target still stays the
accumulation phase; the MMP arm is an ablation condition in §3.6, not a route to the human severe
stage.)* Suzuki et al. (2010) also
implies the composition ratio (collagen I:III) carries information a single lumped ECM field cannot
represent.

### 3.2 Subepithelial / lamina propria thickness

Model output: distance from the epithelial basal surface to the outer boundary occupied by
ECM + mesenchymal cells, in lattice units, relative to baseline.

Comparable measurements:

- **Human small airway:** lamina propria and adventitia thickness increased in smokers and COPD vs
  non-smoker controls, with lamina propria the most affected layer (Eapen et al., 2021).
- **Human asthma:** subepithelial layer thickness correlates with fibroblast number at
  rs = 0.88 and with TGF-β1 expression (Hoshino et al., 1998). This is the single best target for
  the model, because it validates the *coupling* (cell number → thickness), not just an endpoint.
- **Mouse SO2, 5 days:** increased small airway wall thickness attributable specifically to
  subepithelial collagen deposition (Teitz-Tennenbaum et al., 2025). Useful because it isolates the
  same lesion from a different irritant.
- **Human COPD, non-monotone:** wall thickness increased in GOLD 1–2 but similar to never-smokers in
  GOLD 3 (Higham et al., 2022). Same caveat as collagen.

**Recommended target:** Tier 2, and specifically reproduce **the Hoshino correlation**: across a
parameter sweep of `R_fib` (A15), plot subepithelial thickness against fibroblast number and check
for a strong positive monotone relationship. This is a correlational validation that survives having
no unit calibration, and it directly tests why `R_fib` is in the interface at all.

### 3.3 Myofibroblast density

Model output: myofibroblast count per unit subepithelial area, and myofibroblast area fraction.

Comparable measurements:

- **Human small airway, the closest target:** αSMA⁺ cells counted per mm² of lamina propria and per
  mm of reticular basement membrane, increased in both smokers and COPD vs non-smoker controls, and
  the lamina propria population correlated with lung-function decline, lamina propria thickening and
  ECM protein deposition (Eapen et al., 2021). This paper reports exactly the two normalisations the
  model produces natively.
- **Area-fraction form:** αSMA⁺ fractional area 14.7 ± 2.8% (fatal asthma), 13.0 ± 1.2% (non-fatal
  asthma), 7.4 ± 2.4% (controls), by point counting (Boser et al., 2017). *(verify)* Parenchyma, not
  airway wall, so use it as a plausibility band for "roughly a doubling," not as a matched target.
- **Rat biomass PM2.5:** myofibroblast proliferation at 24 weeks but not 4 weeks (Li et al., 2024).
- **Contrarian:** αSMA⁺ cells were *reduced* in bronchioles in smokers and COPD while increased in
  bronchi (Karvonen et al., 2013). *(verify author list)* Same non-monotonicity problem as collagen;
  hold in reserve.

**Recommended target:** Tier 2 ordering (control < exposed) plus the Eapen correlation structure
(myofibroblast density should co-vary with both thickness and collagen fraction within a run).

### 3.4 Fibroblast number

Model output: total fibroblast + myofibroblast count over time.

- Hoshino et al. (1998) is again the anchor: number, not only phenotype, tracks thickening.
- This is the readout that justifies `R_fib` in A15. If the model reproduces thickening with a fixed
  cell pool, `R_fib` is unnecessary and should be dropped; that is a legitimate negative result and
  worth reporting.

**Recommended target:** Tier 2, as an ablation rather than a comparison to a literature number.

### 3.5 Lumen area

Model output: lumen cross-sectional area relative to baseline.

- **Human small airway:** luminal narrowing 22% in COPD vs 10% in never-smokers and 13% in smokers,
  inversely related to FEV1 % (rho = −0.4) (Higham et al., 2022). *(verify)*
- **Severe COPD, micro-CT:** ~10-fold reduction in terminal bronchiole number and ~100-fold
  reduction in lumen area (Hogg et al., 2009). End-stage; far outside what v1 can or should produce.

**Recommended target:** Tier 1 only, i.e. lumen area should *decrease* and should decrease because
the wall grew inward (A8), not because of an artefact. Per A12 this is explicitly **not** converted
to a resistance or airflow claim, since Polosukhin et al. (2021) identified loss of alveolar
attachments rather than wall thickening as the dominant determinant of airflow limitation.

### 3.6 Spatial pattern: the focal-vs-diffuse readout

This is the model's actual contribution (per the deck), and it needs a metric that no scalar area
fraction provides.

- **Method precedent:** Roop et al. (2026) applied **Ripley's K** to AI-segmented fibrosis in
  preclinical lung histology and found *different spatial distributions among samples with similar
  Ashcroft scores and similar total fibrosis content*. That is precisely the claim structure of our
  focal-vs-diffuse experiment: matched total burden, different spatial arrangement.
- **Distribution precedent:** Cogno et al. (2022) reported ECM density distribution histograms to
  distinguish late-fibrosis patterns, another matched-total, different-shape comparison.
- **Biological anchor:** fibroblastic foci are discrete and spatially organised (Watanabe et al.,
  2025), and peribronchiolar fibrosis in wood-smoke exposure is described as focal rather than
  diffuse interstitial (Zou et al., 2014; Morán-Mendoza et al., 2008, who found diffuse interstitial
  fibrosis *absent*).

**Recommended target:** Tier 2, and treat this as the headline validation, not an afterthought.
Compute Ripley's K (or the simpler nearest-neighbour / patch-size distribution) on the collagen
field for focal and diffuse seeding at matched total damage. The model passes if it separates the
two conditions on the spatial statistic while total collagen area fraction is statistically
indistinguishable. If it cannot, the CPM justification thins (see the 2026-07-26 next steps).

**This also gives the A14 threshold a measurable definition:** the focal→diffuse transition in
`S_M2` is the value at which the Ripley's K signature of the exposed condition becomes
indistinguishable from a uniform random field.

**Ablation conditions (added 2026-10-30, `roadmap_revision_2026-10-29.md` §3).** Gate D runs the
focal and diffuse arms at matched `f_d` and matched `S_M2` under six conditions of the B′
switches: (0) base model, all off; (1) + `P` repair gating; (2) + `P` proliferation; (3) + MMP;
(4) + ECM cells; (5) all on. The pre-registered criterion is unchanged and applied per condition:
separation on Ripley's K(r/d), with `d` fixed before any curve is drawn, while collagen area
fraction (now the ECM-cell pixel fraction of §3.1) is statistically indistinguishable between
arms. The paper's result is the table of which conditions separate. The point pattern for K is
the ECM-cell centroids (or pixels), which is what a stained section shows; myofibroblast centres
are the secondary pattern.

### 3.7 Comparing the spatial statistic against real histology

§3.6 gives the model a spatial statistic. This section is about getting a *measured target* to
compare it with, which is what turns focal-vs-diffuse from an internal contrast into a validation.

**Use the published tool on real tissue, not on model output.** The Roop et al. (2026) code is
available, and the tempting move is to run their segmenter on rendered CC3D frames. That is the
wrong half of the pipeline to reuse:

- *No information is gained.* Their segmenter solves "recover which pixels are collagen from a
  noisy stained image." In the model the collagen field is written directly, so ground truth is
  already exact. Segmenting a picture of it can only add error.
- *Domain shift.* The classifier was trained on Masson's trichrome histology — fiber texture,
  nuclei, stain variation, a fixed magnification. A CC3D render is flat synthetic raster with
  pixel-step boundaries. It will still return numbers, and they will not be meaningful.
- *Ashcroft is the wrong scale for this lesion.* Its anchors are alveolar septa and airspace
  obliteration. The v1 domain is an airway-wall cross-section with no alveoli, so a predicted
  Ashcroft score has no referent.
- *The error would land where it hurts.* Segmentation error is largest where the lesion is sparse,
  which is the focal arm — precisely the comparison that must stay clean.

There is a real argument for pushing model and tissue through the same measurement instrument, the
same reason one applies a single threshold to both arms. But that is achieved by **matching the
statistic, not the classifier**: the same K estimator and the same edge correction on both sides.
That gets the instrument-matching benefit without inheriting an unvalidated model on
out-of-distribution input.

**So the productive direction is the reverse one:** run their segmenter on real biomass /
wood-smoke small-airway sections, compute Ripley's K on the segmented output, and compare those
curves against the model's.

**The unit problem, and the fix.** Ripley's K carries units of distance, but A7 commits the model
to no lattice-site-to-µm mapping. A model K curve and a histology K curve therefore live on
different rulers and cannot be overlaid as-is. Rather than abandon A7, normalise the radius by a
characteristic length that is well defined on *both* sides. **Mean epithelial cell diameter** is the
natural choice: it is directly measurable on the lattice and directly measurable in a stained
section. Report **K(r/d)**, not K(r).

Implemented in `model/analysis/spatial_stats.py`:

- `mean_cell_diameter(cell_id_field)` returns `d = 2·√(mean cell area / π)` in lattice units.
- Every K function takes `norm_length=d`; radii come back divided by `d` and K by `d²`, so
  Besag's `L(r) − r` is divided by `d` and stays a length.
- The CLI takes `--cell-ids` (derives `d` automatically) or `--norm-length`.

Two properties worth knowing, both verified in the module's tests:

- Normalisation is **exact**, not approximate: radii scale by `1/d` and `L − r` by `1/d`.
- The **CSR test and the pass/fail verdict are invariant** to it, since observed and simulated
  statistics rescale together. Normalisation changes the reported magnitude and the units, never
  the conclusion. So it can be switched on for the histology comparison without any risk of
  altering the internal focal-vs-diffuse result.

Decide `d` before generating curves. Retrofitting a normalisation after the fact means recomputing
everything, and it is easy to forget which figures were made on which ruler.

## 4. What we deliberately cannot validate

State these before a reviewer does:

- **Airflow limitation / spirometry.** Excluded by scope, and Polosukhin et al. (2021) says wall
  thickening is the wrong lever anyway.
- **Absolute timescale.** A11 reduces the ODE by cycle-averaging; there is no committed MCS-to-week
  mapping, so "24 weeks" is reproduced as an ordering (late > early), not a time.
- **Collagen composition.** A single lumped ECM field cannot produce the collagen I:III ratio that
  Suzuki et al. (2010) and Hogg et al. (2009) found informative.
- **The degradation limb.** No MMPs in v1, so the late-COPD collagen *decrease* is out of reach.
  Zou et al. (2014) found gelatinase upregulation in exactly this exposure model, so this is a known
  and citable omission, not an oversight.
- **EMT.** Deferred per A17, and contested independently (Milara et al., 2013 report EMT in COPD
  small airways; lineage-tracing work disputes the myofibroblast fate).

## 5. Minimal validation set for the hackathon build

In priority order, all Tier 2:

1. **Focal vs diffuse separates on a spatial statistic at matched total collagen.** The contribution.
2. **Exposed > control on collagen area fraction**, with the ratio in the neighbourhood of the ~3×
   implied by Kong et al. (2023) and the 2–40% band of Islam et al. (2023).
3. **Thickness correlates with fibroblast number** across the `R_fib` sweep (the Hoshino rs = 0.88
   structure).
4. **Late > early at matched exposure rate**, reproducing the 4-week-vs-24-week ordering of Li et al.
   (2024) without claiming the units.
5. **Lumen area decreases** and does so inward (Tier 1 sanity check on A8).

## 6. Follow-up needed

- Pull the full texts of Eapen et al. (2021), Higham et al. (2022) and Kong et al. (2023) and
  extract the actual αSMA⁺/mm², thickness and collagen-% values with dispersion into a small table
  in `data/processed/`. Abstract-level numbers are not enough to plot against.
- ~~Decide the spatial statistic and write it as post-processing.~~ **Done** —
  `model/analysis/spatial_stats.py` (Ripley's K + global CSR test, patch-size distribution,
  mark-weighted variant, radius normalisation).
- Obtain real biomass / wood-smoke small-airway sections to run through the Roop et al. (2026)
  segmenter, so §3.7 has a measured K curve to compare against. This is the gating item for turning
  focal-vs-diffuse into a genuine validation rather than an internal contrast.
- Fix the value of `d` (mean epithelial cell diameter) once the v1 geometry exists, and record it,
  so every K figure is made on the same ruler.
- Confirm whether Islam et al. (2023) report collagen area fraction over the whole domain or over a
  tissue subregion; our denominator must match theirs for the band comparison to mean anything.

## 7. Parameter anchors for scale calibration (A7)

*Added 2026-09-04.* These are **not** validation readouts — they are the literature values the model's unit
conversions are solved against. They sit here rather than in §3 because §1's dimensionless constraint is
what they are in the business of relaxing. Sources, with supporting and challenging entries and the full
reviewer note, are in `docs/evidence_dossier_assumptions.md` (§ Assumption A7).

Values marked *(verify)* were read off a published figure, not a table, and are not plottable until confirmed.

| Quantity | Value (dispersion) | System / species | Use | Tier it serves |
|---|---|---|---|---|
| Airway epithelial cell **width** | **10.2 ± 1.0 µm** (bronchial), 10.6 ± 1.1 µm (nasal); planimetry of confluent cultures | Primary human bronchial epithelial cells, cultured (Devalia et al., 1990) | Primary µm/px anchor against `EPITHELIAL_CELL_WIDTH = 8` px | 3 (calibration input) |
| Airway epithelial cell **width**, second anchor | **9.3 µm** (Clara/secretory) to 21.2 µm (mucous M1); height 9.6 µm to 30.6 µm; TEM morphometry | Sheep tracheobronchial epithelium (Mariassy & Plopper, 1984) | Independent-method check on the above; the Clara-cell figure is the small-airway-relevant one | 3 |
| Small-airway epithelial **cell shape** | Simple cuboidal, ciliated + nonciliated secretory | Mammalian bronchiole, qualitative (Plopper, 2020) | Reason to take the low end of any generic "airway epithelial" width range | 1 |
| Fibroblast **migration speed** | **≈ 10.7 µm/h** (SD ≈ 3.5) IPF cell on IPF matrix; 9.8 (2.8) IPF on normal; 7.3 (3.3) normal on IPF; 6.1 (2.1) normal on normal. n = 100–200 cells/condition, ≥3 independent runs, imaged every 30 min over 72 h *(verify — Fig. 3B only; full text checked 2026-09-07, no table and no in-text values exist, so this can only be resolved by digitizing the figure or asking the authors)* | Primary human lung fibroblasts on image-based collagen scaffolds of normal and IPF lung (Tisler et al., 2020) | Primary s/MCS anchor; **replaces** the 40 µm/h dermal placeholder from Chandrasegaran et al. (2025) | 3 (calibration input); 2 for the IPF > normal ordering |
| Fibroblast **migration**, direction only | Control 183 (86) vs IPF 689 (491) cells/field serum-free; 829 (222) vs 1928 (600) with PDGF | Human lung fibroblast lines, Boyden chamber (Suganuma et al., 1995) | Confirms fibrotic > normal; also found migration **uncorrelated** with proliferative capacity | 2 |
| Fibroblast **doubling time** | **32.0 ± 6.0 h** (IPF/UIP, n = 10 lines) vs **33.2 ± 10.4 h** (control, n = 10) — no difference | Human lung fibroblast lines from open biopsy (Mio et al., 1992) | Mitosis-rate parameter for GF-gated mitosis; MCS↔time cross-check | 3 |
| Fibroblast **doubling time**, COPD phenotype | **33.6 ± 2.8 h** (emphysema) vs **24.8 ± 1.4 h** (control), n = 10 each; max PDL 13.8 (7.4–22.6) vs 20.2 (11.2–25.5), ns | Human lung fibroblasts, explant culture (Holz et al., 2004) | Same; and the exposure-closest of the two doubling-time sources | 3 |
| Fibroblast **proliferation in vivo** | Clonal expansion of alveolar-fibroblast progeny, localized to remodeling regions; higher proliferation in human fibrotic PCLS | Two mouse PF models + human PCLS (Molina et al., 2025) | Justifies GF-**gating** of mitosis rather than a raised global rate | 2 |
| Reticular basement membrane **thickness** | **6.0 (1.8) µm** COPD vs **4.8 (1.2) µm** control (n = 17 / 10); healthy 3.19 ± 0.55 µm by LM and 2.85 ± 0.86 µm by EM (n = 13); diagnostic thresholds 5–7 µm | Human bronchial biopsy, in situ (Liesker et al., 2009; Wilson et al., 1997; Bourdin et al., 2007) | **Second, independent pixel↔µm anchor** — an in-tissue ECM dimension on the same section as the epithelium. Confirms the subepithelial band is physically sized | 3 (calibration check only — see below) |
| Epithelial : fibroblast **cell-count ratio** | **14.8 ± 0.1 vs 6.6 ± 0.1 cells per 100 µm airway segment ≈ 2.2 : 1** (SE, n = 49 animals) *(verify — abstract-level)* | Normal adult hamster bronchus, lamina propria, [3H]-thymidine autoradiography (Zajicek et al., 1992) | **Dimensionless anchor** — checkable against the model's own cell counts with no µm/px commitment. Also implies ≈ 6.8 µm per epithelial cell along the basement membrane, a 30% challenge to the 10 µm width anchor | 2 (ordinal / ratio) |
| Fibroblast : epithelial **turnover ratio** | Labeling index **1.24 ± 0.1 (fibroblast) vs 0.13 ± 0.02 (epithelial)** at 1 h — fibroblasts ≈ 10× faster baseline turnover *(verify)* | Same source (Zajicek et al., 1992) | Baseline proliferation ordering for the GF-gated mitosis rule: fibroblasts turn over fast, epithelium does not | 2 |
| Small-airway epithelial **height**, human | **45 vs 35 µm** (LVRS nonresponders vs responders, P = 0.025), n = 25 *(verify — almost certainly epithelial **layer** thickness in remodeled tissue, not single-cell height)* | Resected human small airways, severe emphysema (Kim et al., 2004) | Human small-airway epithelial dimension — the species/site gap in the width anchors. Use as direction, not value | 1 |
| Fibroblast **growth rate**, wood-smoke-specific | **Trimodal in dose:** 0.5–1% WSE increases growth rate; 2.5% decreases it without damage; 5–20% inhibits growth and damages cells. At 2.5%/3 h: ↑ total collagen, ↑ TGF-β1, Col I/III, MMP-1, TIMP-1/2 | Normal human lung fibroblasts + wood smoke extract (Recillas-Román et al., 2021) | The **only** biomass-specific fibroblast proliferation figure found; closes half the A7/A19 exposure gap | 2 (and a challenge — the response is non-monotonic) |
| Fibroblast/epithelial **motility** under particulate | Unchanged to 125 µg/mL; **decreased** migration, motility and motility speed at 250–500 µg/mL. Cigarette-smoke proxies concur (migration inhibited via adhesion/cytoskeleton and via ROS/AMPK) | A549 + biomass-burning particles (de Albuquerque et al., 2021); proxies (Wong et al., 2004; Shin et al., 2019) | **Challenges** any parameterization in which exposure raises fibroblast motility | 2 (direction) |
| Cytokine **diffusion length** (`P`) | **80–120 µm** in vivo; few cell diameters with dense consumers | Mouse in vivo + 3D models (Oyler-Yaniv et al., 2017; Thurley et al., 2015) | Sets λ_P = 80 px; D derived from decay (calibration_table § B′ pins) | 3 (calibration input) |
| IL-6 **half-life** | t½ 3 min / ~55 min plasma; 15 min receptor-mediated | Rat in vivo; rat hepatocytes (Castell et al., 1988; Nesbitt & Fuller, 1992) | Sensitivity value for `P` decay; challenges the 17 h ODE fallback | 3 (proxy) |
| Fibroblast → **α-SMA⁺** time | **24 h** TGF-β1, stable 8 d; 72 h in gingival proxy | Human fetal/adult lung fibroblasts, MRC-5 (Garrison et al., 2013; Yap et al., 2021; Marconi et al., 2021) | Activation rate 7.2e-4 /MCS (2.4e-4 sensitivity) | 3 (calibration input); 2 as an ordering vs proliferation |
| IL-6 effect on epithelial **repair** | **Faster**: 24 h closure 15% → 79% at 0 → 100 ng/mL *(verify)*; smoke slows repair | Primary nasal epithelium (Bequignon et al., 2020); primary bronchial + smoke (Di Vincenzo et al., 2022) | Sign check on `k_P`; scanned, not pinned | 2 (direction, contested) |
| IL-6 effect on lung fibroblast **proliferation** | ~2× with IL-1β; **inhibits** normal, stimulates IPF fibroblasts | Human lung fibroblasts (Olman et al., 2004; Moodley et al., 2003) | Sign and ceiling for `k_prolif`; scanned | 2 (direction, contested) |
| Free **diffusion coefficient** of a 21–26 kDa protein (`G`, `P`) | **84 µm²/s (20 °C) to ~128 µm²/s (37 °C)**, D ∝ M^−1/3, 75 % of 301 proteins within 20 % of the correlation; cytokines within 24 % of Stokes–Einstein | Correlation on 143 proteins (Young et al., 1980); labelled TNF-α, IFN-γ, IL-2 (Ross & Pompano, 2018) | 3300–5100 px²/MCS: **unusable directly** (λ > 600 px at either decay); establishes that TGF-β1 and IL-6 share a free D | 3 (calibration input, upper bound only) |
| **Effective** D in tissue, binding-dressed (`G`, `P`) | Tortuosity/ECM viscosity: 2.6–10× below free; heparan-sulfate binding: a further **~60 %** in vivo; receptor binding + tortuosity: **order of magnitude** local→global | Rat cortex, HS-binding protein (Thorne et al., 2008); zebrafish ECS geometry, simulation (Zhu et al., 2024); dense ECM gels (Galgoczy et al., 2014); HS-protein review (Alotaibi et al., 2024) | Why D is derived from λ: the solver's D is the dressed value, 40–160 px²/MCS at most and lower for matrix-bound TGF-β1 | 1 (mechanism); 2 for the ordering TGF-β1 < IL-8 < IL-6 by binding |
| TGF-β1 **signalling range** (`G`) | **~70 µm** nearest-neighbour distance of pSMAD2⁺ T cells to TGF-β1-presenting Tregs, 2× closer than random, 186 samples *(verify — a proximity statistic, not a gradient fit)*; family members act over "a few cell diameters" in intact tissue; contact-dependent signalling without release | Human carcinomas incl. lung (Van Meerbeeck et al., 2025); *Xenopus* (Jones et al., 1996); structural + mouse (Campbell et al., 2020; Jin et al., 2024) | **λ_G scan 10–70 µm = 8–56 px** (D = 0.64–31 px²/MCS at k = 0.01); current 4 µm is the contact-only arm | 3 (calibration input); 2 for "short-range" |
| Active TGF-β1 **half-life** (`G` decay) | **1.6 ± 0.7 min** (mouse plasma); **2–3 min** (rat plasma); **×3** with heparin/fucoidan; latent complex **> 100 min**, < 5 % degraded at 90 min; irreversibly matrix-bound fraction | Mouse (Philip & O'Connor-McCourt, 1991); rat (Wakefield et al., 1990); smooth-muscle cultures (McCaffrey et al., 1994); ECM release assay (Dinbergs et al., 1996) | Bounds k_G to 0.0072–0.45 /MCS; current 0.01 (t½ 72 min) is the latent end — defensible for a lumped active+latent `G`, stated | 3 (proxy, bounds only) |
| IL-8 / IL-6 **matrix retention** (`P` range) | IL-8 bound to HS- and CS-rich cell surfaces and ECM in lung sections, lost on GAG removal; IL-8–heparin K_d **0.39–2.63 µM**; IL-6 heparin retention **partial**, none on chondroitin sulfate | Human and rabbit lung tissue (Frevert et al., 2003); HUVEC/ITC (Kuschert et al., 1999); affinity chromatography (Ramsden & Rider, 1992); review (Crijns et al., 2020) | Sets the `P` lower arm (haptotactic IL-8, λ ≈ 25 µm) and justifies λ_P > λ_G; **λ_P scan 25–120 µm = 20–96 px** (D = 0.28–6.4 px²/MCS at k = 6.93e-4), 250 µm upper arm | 2 (ordering); 3 for the λ_P range with Oyler-Yaniv et al. (2017) |

**What this buys, and what it does not.**

- **µm/px.** The three width sources converge on ~9–11 µm for a bronchiolar/secretory airway epithelial cell,
  below the 12.5 µm midpoint the model has been carrying. At **10 µm / 8 px = 1.25 µm/px**, the 200 × 100 px
  domain is **250 × 125 µm**, the 20 px lumen band is 25 µm and the subepithelial band is 87.5 µm (70 px; **68 px / 85 µm since 2026-09-18**, when the taller epithelium took 2 rows).
  The 10–15 µm range is not wrong — it describes large-airway pseudostratified columnar epithelium — but A16
  places this model in the small airway, where the epithelium is cuboidal.
- **This is a reinterpretation, not a rescaling.** `EPITHELIAL_CELL_WIDTH` stays 8 px; no adhesion energy or
  `lambdaVolume` changes. Module 8.2's rescaling rule bites when the pixel count per cell changes, which it
  does not here.
- **s/MCS — closed 2026-09-06.** The isolated-fibroblast scratch run (`lab-notebook/2026/2026-09-04.md`
  continued session) measured mean |ΔCOM| = **0.1484 px/MCS** (5000-MCS run, boundary never confining it).
  `s/MCS = v[px/MCS] × 1.25 [µm/px] ÷ v_lit[µm/s]` then gives two candidates depending which Tisler2020
  condition anchors it: **62.4 s/MCS** at the IPF/IPF figure (10.7 µm/h) — **chosen as the baseline** — or
  **109.5 s/MCS** at the conservative normal/normal figure (6.1 µm/h), which clears the ceiling below by only
  ~9%. The choice is a modeling judgment call, not a settled literature value: this model's fibroblasts are
  undergoing active wood-smoke/PM2.5-driven conversion rather than sitting at baseline, which leans (weakly)
  toward IPF/IPF, but the exposure etiology does not match Tisler2020's IPF cohort. State this limitation
  wherever the number is cited in a manuscript or slide. Using the dermal 40 µm/h placeholder instead of
  either would divide s/MCS by a further 3.7–6.6× — the largest single correction avoided by this solve.
- **The cell-cycle cross-check bounds it.** Module 8.2 asks for ≥1000 MCS per cell cycle. At a measured cycle
  of 25–34 h that is **s/MCS ≤ ~90–120 s** — both candidates above clear this. For reference, Chandrasegaran
  et al. (2025) run at 27 s/MCS, which would put a 30 h cycle at ~4000 MCS. At the chosen 62.4 s/MCS, a 30 h
  cycle is **~1730 MCS** (`parameters.py FIBROBLAST_CYCLE_MCS`, used by the GF-gated mitosis rule added
  2026-09-06).
- **What that makes a run mean.** At the chosen 62.4 s/MCS a 20,000 MCS run is **14.4 days** of biological
  time (25.3 days at the conservative 109.5 s/MCS alternative) — days, not the 24 weeks of Li et al. (2024).
  The "displacement plateaus by MCS 300–400" observation from 2026-08-14 is therefore a plateau within
  **5.2–12.2 hours**, a much stronger reason to suspect a saturating mechanism rather than a slow one.
  *Superseded 2026-09-26:* that plateau was specific to the old 6 × 8 px epithelium. On the current
  8 × 8 px geometry lumen narrowing reaches ~−8% by MCS 1000 and keeps drifting through MCS 20000
  (−8.6% to −17.2%, mean −12.3%, 6 pinned full runs; `lab-notebook/2026/2026-09-18.md`), so there
  is no early plateau to read as a saturating mechanism. The 14.4-day run length still applies.
  *Superseded 2026-10-27 (Gate B4, measurement only — no criterion changed):* on the anchored
  `FIBROBLAST_INITIAL_NUMBER = 11` with the epithelial repair path, the same n = 6 reads −0.3% to
  −4.2% at MCS 20000 (mean −2.5%, SD 1.4; `lab-notebook/2026/2026-10-27.md`). §3.5 Tier 1 still
  passes in every replicate; the Tier 2 magnitude gap to Higham's ~22% widened from ~2× to ~9× and
  is logged as a finding for the Gate D stage, not re-targeted here.
  *B′ note, 2026-10-30:* the volume-occupying ECM cell type changes the displacement mechanism —
  matrix, not myofibroblast swelling, now pushes the sheet, and the `c_norm` growth of myofibroblast
  `targetVolume` is reduced or removed with it — so the −2.5% figure is expected to move in the one
  B′ rebaseline (all switches on, n = 6). The Higham gap is re-measured there, still as a finding.
- **The second, independent pixel anchor — found 2026-09-07, and it is an ECM dimension.** The fibroblast-size
  route stays ruled out: that literature reports 2D spread area on a substrate — median ≈ 800–2100 µm² across
  1–50 kPa (Asano et al., 2017, Fig. 2A) *(verify)* — a flattened cell's full footprint on glass, not its
  profile in a tissue cross-section, and 20–40× larger than `TARGET_VOLUME_FIB = 30` px (46.9 µm² at
  1.25 µm/px, equivalent diameter 7.7 µm). What works instead is **reticular basement membrane thickness**,
  measured in µm in situ on the same section as the epithelium, by three groups and two independent methods
  agreeing to ~0.35 µm (Liesker et al., 2009; Wilson et al., 1997; Bourdin et al., 2007). It confirms the
  subepithelial band is physically sized at 1.25 µm/px.
- **But RBM cannot be a model readout at this resolution.** At 1.25 µm/px a healthy RBM (≈ 4.7 µm) is 3.8 px
  and a COPD RBM (≈ 6.0 µm) is 4.8 px: the entire disease effect is **one pixel wide**. State this before a
  reviewer does. A19/A18's ordinal stance does not fully cover it, because the quantity is not merely
  uncalibrated — it is unresolved.
- **The strongest of the new anchors is dimensionless, so A7 does not bite it.** Zajicek et al. (1992) give
  **14.8 epithelial and 6.6 fibroblast cells per 100 µm of bronchial segment**, an **epithelial : fibroblast
  ratio of ≈ 2.2 : 1**, checkable against the model's own cell counts with no µm/px commitment at all. The same
  source's linear epithelial density implies **≈ 6.8 µm per epithelial cell** along the basement membrane, a
  genuine ~30% challenge to the 10 µm width anchor (hamster, and oblique sectioning inflates counts). Quote
  µm/px as **~0.85–1.25, 1.25 chosen**, not as a settled single value.
- **Epithelial cell height — recommendation 2026-09-07: move `TARGET_VOLUME_EPITHELIAL` 48 → 64 px, pending
  Marcella's sign-off and a rescaled re-run.** `TARGET_VOLUME_EPITHELIAL = 48` px at an 8 px width is 6 px tall
  = **7.5 µm** at 1.25 µm/px, against a measured Clara-cell height of **9.6 µm** (Mariassy & Plopper, 1984).
  Three things point the same way: 9.6 µm is 7.7 px, i.e. 8 px to the nearest pixel; Plopper (2020) describes
  bronchiolar epithelium as **simple cuboidal**, and cuboidal means height ≈ width, which 6 × 8 is not; and A16
  places this model in the small airway, so a flattened cell is the wrong shape for the stated tissue. The
  current 48 px is inherited, not chosen.
  **Unlike the µm/px change, this one is a real rescale** — the pixel count per cell moves — so Module 8.2's
  rule fires and three parameters must move with it (`V_ref/V_actual = 48/64 = 0.75`; effective diameter
  `D_ref/D_actual = √48/√64 = 0.866`):
  `LAMBDA_VOLUME_EPITHELIAL` 30 → **22.5**; `LAMBDA_SURFACE_EPITHELIAL` 1.0 → **0.87**; every epithelial
  contact energy `J` × **0.866**. `EPITHELIAL_FPP_TARGET_DISTANCE` is keyed to `EPITHELIAL_CELL_WIDTH`, which
  does not change, so the focal-point-plasticity block is untouched.
  **Not applied to `parameters.py` in the 2026-09-07 pass (applied 2026-09-18, see the status update at the end of this bullet)** — it changes model behavior and needs a before/after run
  (fixed `<RandomSeed>`, per Module 8.2) to confirm the epithelial layer still holds together at the new
  target volume. Kim et al. (2004)'s human small-airway epithelial height of 35–45 µm is *not* evidence for a
  taller cell here: that is layer thickness in remodeled emphysematous tissue, flagged *(verify)*.
  **Status update 2026-09-18:** applied — `TARGET_VOLUME_EPITHELIAL` 64, `LAMBDA_VOLUME_EPITHELIAL`
  22.5, `LAMBDA_SURFACE_EPITHELIAL` 0.87, epithelial `J` × 0.866. The before/after run found two things
  this section did not anticipate: (i) the epithelial seeding band must scale with cell height (left
  at 6 rows, cells seeded 16 px under target and inflated into the lumen, giving a spurious −12.5%
  narrowing), so it is now derived from `EPITHELIAL_CELL_HEIGHT`; (ii) the rescaled lambdas and J make
  the sheet softer and narrow the lumen more at matched subepithelial pressure, so narrowing figures
  from before this date are not comparable with later ones.

## 8. Exposure-matched anchors from full text (added 2026-09-26)

*Added after extracting full text of the three PDFs placed in `literature/bio_lit` in September
2026. These supersede the abstract-level entries above where they conflict; §3 has not been
rewritten, so read this section with it.*

### 8.1 Zou et al. (2014) — now the primary quantitative anchor

Wood-smoke rat model, 4 and 7 months, n = 8 per group, mean ± SEM, one-way ANOVA. This is the only
anchor in this doc that is both **exposure-matched** and **small-airway-specific**, so it should be
the number the model is held against; Kong (2023) and Higham (2022) drop to context.

| Quantity | Control | Wood smoke | Cigarette smoke | Ratio WS:control | Tier |
|---|---|---|---|---|---|
| Small airway wall thickness (µm²/µm Pbm) | 7.6 ± 1.1 | 14.3 ± 3.3 (p<0.01) | 12.1 ± 3.4 (p<0.01) | **1.9×** | 2 |
| Total collagen, Masson (µm²/µm Pbm) | 2.4 ± 1.1 | 4.9 ± 2.2 (p<0.05) | 4.9 ± 1.0 (p<0.05) | **2.0×** | 2 |
| Type I collagen, IHC (µm²/µm Pbm) | 7.0 ± 2.1 | 11.1 ± 2.7 (p<0.05) | 10.5 ± 2.5 (p<0.05) | **1.6×** | 2 |
| Mean linear intercept (µm) | 47.7 ± 4.0 | 60.5 ± 6.7 (p<0.01) | 56.1 ± 4.1 (p<0.05) | 1.3× | out of scope (parenchyma) |
| Airway smooth muscle (αSMA area) | — | **not significantly increased** | not significantly increased | — | supports A8 |

**Revision to §3.1.** The recommended target ratio changes from "2.5–3× implied by Kong et al.
(2023)" to **~1.6–2.0×, from Zou et al. (2014)**. Kong is large-airway bronchial submucosa
biopsy; Zou is the small airway under the model's own exposure.

**Units warning.** Zou reports collagen as **area per unit basement-membrane perimeter**
(µm²/µm), standardized for airway size — a thickness-like quantity, not an area fraction. It is
directly comparable to the model's *subepithelial thickness* readout and to exposed:control
*ratios*, and it is **not** comparable to the Kong percentage or the Islam 2–40% band. The three
anchors in this doc are three different quantities; do not plot them on one axis.

**Late > early (minimal-set item 4) is now anchored in the matched exposure.** Zou found **no
significant collagen difference at 4 months** and significance at 7 months, and fibroblast number
elevated at both 4 and 7 months. So the ordering target no longer has to lean on Li et al. (2024)'s
PM2.5 4-vs-24-week result, though that remains a consistent second source.

**The MMP omission is confirmed as exposure-relevant, not hypothetical.** MMP9, MMP2 and TIMP1 were
all raised in the small airway wall at 4 and 7 months and localized primarily to the **airway
epithelium**, with serum MMP9/TIMP1 also raised. §4's degradation-limb caveat should cite these
specifics.

**EMT is weak in this exposure.** E-cadherin/vimentin double-positive subepithelial cells appeared
in only **3 of 8** wood-smoke rats at 7 months, with no marked epithelial E-cadherin loss. Supports
A17's deferral.

### 8.2 Eapen et al. (2021) — partly closes §6, and shifts where the signal is

Human small airway (<2 mm i.d.), resections, n = 10 NC / 11 NLFS / 9 COPD-CS / 10 COPD-ES.

**Extractable (usable now):**

- Lamina propria thickness increases **at least ~10-fold** overall vs non-smoker controls;
  adventitia 2–3×; smooth muscle +50%. LP thickness in pathological groups spans roughly
  **5–25 µm** (Fig. 5e axis).
- Collagen-1 % area rises **~1.5× in the lamina propria** but **5–6× in the adventitia**;
  fibronectin rises more uniformly and more strongly than collagen-1.
- Correlations (Spearman): αSMA⁺ in LP vs LP thickness **r′ = 0.43, p < 0.05**; αSMA⁺ in LP vs
  FEV1/FVC r′ = −0.80 (COPD-CS, p<0.01) and −0.61 (COPD-ES, p<0.05); collagen-1 % in LP vs LP
  thickness **r′ = 0.59, p < 0.05 (COPD-CS)** and not significant in normal-lung-function smokers;
  fibronectin vs LP thickness significant in NLFS only.
- **Spatial description, and the most directly usable target here:** the myofibroblast increase in
  the lamina propria is **not uniform** — the cells are "most concentrated in a shallow band just
  deep to the Rbm." This is a Tier 1/2 spatial target requiring no unit calibration, and the model's
  myofibroblast distribution can be checked against it as soon as a density readout exists.

**Not extractable — the §6 follow-up item is only partly closable.** Group means and dispersions for
αSMA⁺ cells per mm of Rbm and per mm² of LP, and for the layer thicknesses, appear **only in
figures** (Figs. 1c–e, 3b–d); the full text contains no corresponding table. Axis ranges are
~0–50 cells/mm Rbm and ~0–3000 cells/mm² LP. These stay *(verify)* and are not plottable until the
figures are digitized — the same situation as Tisler2020 Fig. 3B.

**Consequence for scope.** The compartment carrying the largest collagen signal in human disease is
the **adventitia**, which v1 does not represent. Combined with Zou's null ASM result, this argues
the adventitial compartment should outrank airway smooth muscle on the v2 list.

### 8.3 Tisler et al. (2020) — no change

Full text now in `literature/bio_lit/ajplung.00087.2019.pdf`. Confirms the 2026-09-07 finding: the
migration speeds exist only in Fig. 3B, with no table and no in-text values. The A7 s/MCS
*(verify)* flag stands.

### 8.4 Net effect on the minimal validation set (§5)

| § 5 item | Status after 2026-09-26 |
|---|---|
| 1. Focal vs diffuse separates on a spatial statistic | Unchanged. Blocked on the focal arm; the gating external item is real sections |
| 2. Exposed > control on collagen | **Target revised to ~1.6–2.0× (Zou 2014)**; blocked only on the readout |
| 3. Thickness correlates with fibroblast number | Unchanged (Hoshino rs = 0.88); Eapen r′ = 0.43 adds a second, weaker correlational target |
| 4. Late > early | **Now anchored in the matched exposure** (Zou: null at 4 months, significant at 7) |
| 5. Lumen area decreases inward | Met |
| **new** 6. Myofibroblasts concentrate in a shallow band deep to the epithelium, non-uniformly | Eapen 2021, descriptive; needs the myofibroblast-density readout only |

## 9. An in vitro comparator appears (added 2026-10-11)

*Bennet et al. (2026), Sci Rep, DOI 10.1038/s41598-026-69468-5: a microfluidic airway-on-a-chip with
Calu-3 epithelium at air-liquid interface, HFL1 fibroblasts encapsulated in 3D GelMA, an
endothelialized patterned lumen, and **whole wood smoke** aerosol exposure. Full assessment in
`docs/aoc_platform_impact_2026-10-11.md`; platform details in `lab-notebook/2026/2026-10-11.md`.*

This is the first validation route that matches the model on compartment **and** exposure. It does
not replace §8 — it adds a different kind of target, and it removes one.

**New targets it makes available**

| Target | What is compared | Tier | Blocked on |
|---|---|---|---|
| Culture-configuration ordering | αSMA⁺ and cytokine response across fibroblast monoculture vs epithelial–fibroblast co-culture, model vs chip | 2 (ordinal) | A cytokine-analogue readout (todo item 4). No units, no collagen, no new biology — **the best near-term target in this doc** |
| Response on their clock | Model trajectories reported at days 3, 6, 12, 15 | 2 | Nothing. A 20,000-MCS run at 62.4 s/MCS is **14.4 days**, so the model's natural run length is already their 15-day window |
| Signal without cytotoxicity | Does the model produce a lesion with `f_d` = 0 and the `S_M2` pedestal alone? | 1 (qualitative) | Nothing — see the A14/A19 challenge below |
| Stiffness threshold | Model-predicted stiffness at which activation becomes self-sustaining, against GelMA tuned from native (0.44–7.5 kPa) toward fibrotic (~17 kPa) | 2, forward prediction | v2 latent/active TGF-β split |

**Reachable with no tissue-model code at all (added 2026-10-23).** The published ODE emits a
pro-inflammatory cytokine `P` whose epithelial submodel was validated against Calcabrini et al.
(2004) — A549 cells, PM2.5, IL-6 and TNF-α over 72 h. Bennet et al. measure **IL-6 and IL-8** in
effluent from a whole-smoke, air-liquid-interface, epithelial–fibroblast co-culture. Comparing the
ODE's `P` trajectory against their Fig. 6c is the same validation redone on a far better-matched
exposure, and it requires only a Tellurium run. **Do this before the tissue-layer targets above.**
Caveats: their effluent is pooled, their n is 3–7, and the ODE's `P` is a lumped pro-inflammatory
species rather than either named cytokine, so compare normalized shape and ordering, not magnitude.

**The target it removes.** Their smoke arrives by tangential airflow with gravity-driven deposition
across the whole epithelial surface. It is a **diffuse-injury platform with no focal configuration**,
so §3.6's focal-vs-diffuse contrast cannot be validated here. §3.7's requirement for real sections
stands unchanged.

**What it does not supply.** No collagen quantification of any kind. MMP-2 in effluent stayed below
the assay's lower limit of quantification (0.5 ng/mL) for the whole culture period, which they
present as a functional baseline for future work. `Zou2014` (§8.1) therefore remains the only
exposure-matched quantitative anchor and nothing above changes.

**A challenge to the model, recorded here because it changes what counts as agreement.** Wood smoke
raised IL-6 and IL-8 significantly, MUC5AC and endogenous TGF-β1 modestly, and **LDH not
significantly** — pro-fibrotic and inflammatory signaling without widespread cell death. The v1
model routes essentially all exposure-driven signal through damaged epithelium (committed rates
`EpitheliumDamaged` 0.1 vs `EpithelialHealthy` 0.01, a 10:1 ratio, uncalibrated). A19's nonzero
healthy-epithelium rate is **supported** by this result; the 10:1 ratio is **challenged**. Whether
this is a dose effect, LDH insensitivity to sub-lethal stress, or a genuinely wrong ratio is
distinguishable in-model (H1/H2 in the impact doc) and should be settled before the ratio appears in
a manuscript.

**Caveats on any model-vs-chip comparison.** Calu-3 and HFL1 are cell lines, not primary cells (no
ciliated or club cells; fetal fibroblasts). Effluent is pooled from the vascular compartment under
air-tissue-interface operation, so cytokine origin cannot be assigned to a cell type. n = 3–7 devices
per condition, and they name low statistical power as a limitation. Predictions should be stated as
directions and orderings, never as effect sizes to match.

## References

de Albuquerque, Y. L., et al. (2021). The toxic effect of water-soluble particulate pollutants from biomass burning on alveolar lung cells. *Atmosphere*.

Annoni, R., et al. (2012). Extracellular matrix composition in COPD. *European Respiratory Journal*.

Asano, S., Ito, S., Takahashi, K., Furuya, K., Kondo, M., Sokabe, M., & Hasegawa, Y. (2017). Matrix stiffness regulates migration of human lung fibroblasts. *Physiological Reports, 5*(9), e13281.

Boser, S. R., et al. (2017). Myofibroblasts are increased in the lung parenchyma in asthma. *PLOS ONE*.

Bourdin, A., et al. (2007). Specificity of basement membrane thickening in severe asthma. *The Journal of Allergy and Clinical Immunology*.

Cogno, N., et al. (2022). A 3D agent-based model of lung fibrosis. *Symmetry*.

Devalia, J. L., et al. (1990). Culture and comparison of human bronchial and nasal epithelial cells in vitro. *Respiratory Medicine*.

Eapen, M. S., et al. (2021). Increased myofibroblasts in the small airways, and relationship to remodelling and functional changes in smokers and COPD patients. *ERJ Open Research*.

Eurlings, I. M. J., et al. (2014). Similar matrix alterations in alveolar and small airway walls of COPD patients. *BMC Pulmonary Medicine*.

Higham, A., et al. (2022). Increased luminal narrowing but reduced wall thickness in the small airways of severe COPD patients. *European Respiratory Society Congress Abstracts*.

Hogg, J. C., et al. (2009). What drives the peripheral lung-remodeling process in chronic obstructive pulmonary disease? *Proceedings of the American Thoracic Society*.

Holz, O., et al. (2004). Lung fibroblasts from patients with emphysema show a reduced proliferation rate in culture. *European Respiratory Journal*.

Hoshino, M., Nakamura, Y., & Sim, J. J. (1998). Expression of growth factors and remodelling of the airway wall in bronchial asthma. *Thorax*.

Huang, L., et al. (2025). NR1D1 mitigates IL-17a-induced small airway remodeling in biomass smoke-induced COPD. *Toxicology Letters*.

Islam, M. A., et al. (2023). An agent-based modeling approach for lung fibrosis in response to COVID-19. *PLOS Computational Biology*.

Karvonen, H. M., et al. (2013). Myofibroblast expression in airways and alveoli is affected by smoking and COPD. *Respiratory Research*.

Kim, V., et al. (2004). Small airway morphometry and improvement in pulmonary function after lung volume reduction surgery. *American Journal of Respiratory and Critical Care Medicine*.

Kong, A., et al. (2023). Collagen remodelling in COPD: A new paradigm. *European Respiratory Society Congress Abstracts*.

Li, S., et al. (2024). Biomass fuels related-PM2.5 promotes lung fibroblast-myofibroblast transition through PI3K/AKT/TRPC1 pathway. *Ecotoxicology and Environmental Safety*.

Liesker, J. J. W., et al. (2009). Reticular basement membrane in asthma and COPD: Similar thickness, yet different composition. *International Journal of Chronic Obstructive Pulmonary Disease*.

Mariassy, A. T., & Plopper, C. G. (1984). Tracheobronchial epithelium of the sheep: II. Ultrastructural and morphometric analysis of the epithelial secretory cell types. *The Anatomical Record*.

Milara, J., et al. (2013). Epithelial to mesenchymal transition is increased in patients with COPD and induced by cigarette smoke. *Thorax*.

Mio, T., et al. (1992). Proliferative characteristics of fibroblast lines derived from open lung biopsy specimens of patients with IPF (UIP). *Chest*.

Molina, C., et al. (2025). Clonal expansion of alveolar fibroblast progeny drives pulmonary fibrosis in mouse models. *The Journal of Clinical Investigation*.

Morán-Mendoza, O., et al. (2008). Wood smoke-associated lung disease. *International Journal of Tuberculosis and Lung Disease*.

Plopper, C. G. (2020). Structural methods for studying bronchiolar epithelial cells. *Lung Biology in Health and Disease*.

Polosukhin, V. V., et al. (2021). Small airway determinants of airflow limitation in chronic obstructive pulmonary disease. *Thorax*.

Recillas-Román, S., et al. (2021). Wood smoke extract promotes extracellular matrix remodeling in normal human lung fibroblasts. *International Journal of Toxicology*.

Roop, B., et al. (2026). Artificial intelligence, machine learning-based automated fibrosis quantification in preclinical models of pulmonary fibrosis. *Respiratory Research*.

Shin, J.-M., et al. (2019). Cigarette smoke extract inhibits cell migration and contraction via the reactive oxygen species/AMPK pathway in nasal fibroblasts. *International Forum of Allergy & Rhinology*.

Suganuma, H., et al. (1995). Enhanced migration of fibroblasts derived from lungs with fibrotic lesions. *Thorax*.

Suzuki, M., et al. (2010). The quantitative relationship between collagen deposition and lung structure in COPD. *American Thoracic Society Conference Abstracts*.

Teitz-Tennenbaum, S., et al. (2025). Sulfur dioxide exposure of mice induces peribronchiolar fibrosis. *PLOS ONE*.

Tisler, M., Alkmin, S., Chang, H.-Y., Leet, J., Bernau, K., Sandbo, N., & Campagnola, P. J. (2020). Analysis of fibroblast migration dynamics in idiopathic pulmonary fibrosis using image-based scaffolds of the lung extracellular matrix. *American Journal of Physiology: Lung Cellular and Molecular Physiology, 318*(2), L276–L286.

Watanabe, N., et al. (2025). Integrated spatial and single-cell transcriptomics reveal PAK kinase as a therapeutic target in fibroblastic foci and dense fibrosis of idiopathic pulmonary fibrosis. *European Respiratory Journal*.

Wilson, J. W., et al. (1997). The measurement of reticular basement membrane and submucosal collagen in the asthmatic airway. *Clinical & Experimental Allergy*.

Wong, L. S., et al. (2004). Firsthand cigarette smoke alters fibroblast migration and survival: implications for impaired healing. *Wound Repair and Regeneration*.

Yoshizawa, M., et al. (2022). Computational simulation of liver fibrosis dynamics. *Scientific Reports*.

Zajicek, G., et al. (1992). Cell kinetics of lamina propria fibroblasts in normal adult hamster bronchus. *The Anatomical Record*.

Zou, Y., et al. (2014). Upregulation of gelatinases and epithelial–mesenchymal transition in small airway remodeling associated with chronic exposure to wood smoke. *PLOS ONE*.
