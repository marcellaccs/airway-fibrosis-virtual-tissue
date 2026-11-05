# Reorientation, 2026-10-28

Written to be read once with pen and paper, before any more model work. Everything here is checked against the code and docs as of commit `434bc94` (2026-10-27). Section numbers in brackets point at the source doc when you want the long version.

## 1. Where the current model is

- **The model is one folder:** `model/cc3d/subepithelial_fibrosis_draft/`. Four files matter:
  - `Simulation/Subepithelial_Fibrosis.xml` (lattice, cell types, contact energies, the two diffusion fields, chemotaxis)
  - `Simulation/parameters.py` (every tunable, with provenance comments)
  - `Simulation/Subepithelial_FibrosisSteppables.py` (all behaviour, plus the ODE as an Antimony string)
  - `Simulation/ParameterScanSpecs.json` (replicate scan, Gate B3)
- **Everything else under `model/cc3d/` is stale or scaffolding.** `Subepithelial_Fibrosis-02` and `-05`, the `_8_8_10_24PM` copy, the zips, the `_draft_2026-08-08_2244` snapshot, and every `*_cc3d_<timestamp>` folder are old copies or CC3D run dumps. `M1_M2_antimony` and `Telluriumv2` are the Tellurium-in-CC3D precedent, not the fibrosis model. `Old_CC3D_M1_to_M2 files` is 2023.
- **`model/cc3d/README.md` and `WORKFLOW.md` are out of date** (they describe `M1_M2_antimony` and CC3D 4.10). The model is verified on CC3D 4.9.0.
- **Docs that are current:** `model_assumptions_for_slides.md` (A1 to A19), `validation_targets.md`, `roadmap_to_publication_2026-10-26.md` with `roadmap_revision_2026-10-27.md` on top, `cc3d_v1_todo.md`. **Docs that are historical:** `model_spec_v1_v2.md` (July design, with a drift note), `ode_tissue_coupling_options.md` (a proposal; the option it recommended was not the one built), `Model_Notes_digitized.md` (2025 handwritten design), `model_state_2026-09-26.md` (predates Gate B).

## 2. The model in one picture

Sketch a 200 by 100 box. y runs upward. Four horizontal bands:

| Band | Rows | What is in it |
|---|---|---|
| Lumen | 80 to 99 | Medium (empty). 4000 px at t = 0. Narrowing = loss of this area. |
| Epithelium | 72 to 79 | 25 cells, each 8 x 8 px, in a sheet. Two states: **EpithelialHealthy** and **EpitheliumDamaged**. Never move, divide or die. Held together by adhesion, a connectivity constraint, and springs between neighbours. |
| Subepithelium | 4 to 71 | **Fibroblasts** (start: 11, random single pixels) and **Myofibroblasts** (start: 0). The two fields live here. |
| Outer boundary | 0 to 3 | One frozen cell. Stands in for the ASM / outer wall. Only purpose: make growth go inward. |

Scale: 1 px = 1.25 µm (epithelial cell width 10 µm), 1 MCS = 62.4 s (fibroblast speed 10.7 µm/h, Tisler 2020). A 20,000 MCS run is 14.4 days.

**Two fields, both in the subepithelium**

- **G, lumped growth factor (TGF-β-like).** Diffuses (0.10), decays (0.01). Sources: damaged epithelium 0.1, healthy epithelium 0.01, fibroblasts 0.005, myofibroblasts 0.1, plus a spatially uniform pedestal S_M2 from the ODE. Consumers: fibroblast chemotaxis, fibroblast differentiation threshold (G ≥ 0.45), fibroblast mitosis clock (G ≥ 0.225), recruitment placement.
- **C, ECM / collagen burden.** Does not diffuse. Decays slowly (0.0005, crude MMP stand-in). Sources: myofibroblasts on contact with Medium (0.08), epithelium into the subepithelial side (0.01). Consumers: cell stiffness (lambdaVolume rises with C), and myofibroblast target volume grows with C (this is what pushes the sheet). Used through c_norm = C / (C + 20).

**Cell behaviours, in order of the per-MCS loop**

- Epithelium: damaged cells repair (Bernoulli, rate from the ODE; new since 10-27), then healthy cells are damaged so the damaged fraction tracks the ODE's f_d. Count is conserved. Secretes G by state, secretes C downward.
- Fibroblasts: chemotax up G; if local G ≥ 0.45, accumulate activation (0.02 per MCS of signal) and convert irreversibly to myofibroblast at 1.0; if local G ≥ 0.225, the 1730 MCS (30 h) mitosis clock runs and they divide; stiffen with C.
- Myofibroblasts: no chemotaxis, no division, no reversion. Secrete G (0.1) and C (0.08). Target volume grows up to 3x with c_norm.
- Recruitment: one Bernoulli trial per MCS at R_fib = 0.001 (about 20 new fibroblasts per run), placed in the bottom five rows, weighted by G.
- No cell dies. No macrophages in the tissue. No P field in the tissue. No MMP field.

**Readouts that exist today** (printed, and one CSV per run, `replicates_summary.csv`): lumen area and % change, cell counts by type, G and C band means, sheet position, sheet integrity, repair events, divisions, collagen leak into lumen.
**Readouts the paper needs that do not exist yet:** collagen area fraction, subepithelial thickness, myofibroblast density, Ripley's K on the collagen field (`model/analysis/spatial_stats.py` exists but is not wired to model output).

The SVG `docs/figures/model_schematic_2026-10-28.svg` is this picture drawn.

## 3. The ODE: has it changed?

**No.** The ODE running inside CC3D is the published JTB model (Bakry, Brashear, Brashear, Jones & Torres), written as an Antimony string in the steppables file and integrated live by libRoadRunner, one hour of ODE time per MCS. Nine states: E_h, E_d (healthy and damaged epithelium), M1, M2 (recruited macrophages), M0R, M1R, M2R (resident), P (pro-inflammatory cytokine pool), A (anti-inflammatory pool). All dimensionless. Parameters are the paper's (e1 to e6, m1 to m11, Hill constants, k_c, smr, mumr; e8 = e9 = 1, e10 = 0).

The equations that matter for this paper:

- E_h' = e1 (E_h + E_d)(1 − (E_h + E_d)/K) − e2 E_h − e3 WS E_h + e4 (1 + e9 (M2 + M2R) + e10 A) E_d
- E_d' = −e2 E_d + e3 WS E_h − e4 (1 + e8 (M2 + M2R) + e9 A) E_d
- P' = e5 WS F(E_h) + e6 WS F(E_d) + m6 WS F(A) (M1 + M1R) − m7 P
- WS = three one-hour cooking pulses per 24 h (8, 13, 18 h), smoothed sigmoid edges

Three things are not the paper, and all are cosmetic:

- WS is a smooth pulse train instead of discrete events (CVODE failed on the events).
- The repair term in E_h' uses e9/e10 where E_d' uses e8/e9 (old numbering; under 2% on E_h + E_d, zero on f_d).
- Nothing else.

What *has* changed is what the tissue reads from it. Before 10-27 it read M2 + M2R (for S_M2) and f_d. Now it also reads e4, e8, e9, M2 + M2R and A to compute the repair probability.

Known loose end, documented and not fixed: the ODE clock (1 h per MCS) and the tissue clock (62.4 s per MCS) differ by about 58x. It is tolerable because of A11: the ODE sits on a periodic attractor from about day 27 (M2, A) and day 83 (f_d), so the tissue consumes it as near-constants, not as a time series. The repair rate was deliberately converted on the tissue clock. The paper's methods need one paragraph on this.

## 4. Forward and backward flow: what happened to it

The original intent was two-way coupling. The current state:

- **Forward (ODE to tissue), three channels, every MCS:**
  - S_M2 = 0.003 (M2 + M2R), added uniformly to G. Raises the floor, no gradient.
  - f_d = E_d / (E_h + E_d), sets the damaged fraction of the sheet.
  - p_repair = e4 (1 + e8 (M2 + M2R) + e9 A) x hours per MCS, per damaged cell.
- **Backward (tissue to ODE): nothing.** The ODE runs autonomously. No tissue quantity is written into any ODE species or parameter.

This was decided, not forgotten. `ode_tissue_coupling_options.md` rejected two-way coupling for v1 and named the trigger that would justify it: a tissue mechanism that changes epithelial damage independently of the ODE (EMT is the example). Nothing in the tissue does that today, so feeding anything back would be feeding back noise. **Not superseded, deferred.** For this paper, the one-way design is also the point: the uniform S_M2 pedestal is the experimental control that holds immune drive flat while only the spatial pattern of injury varies.

## 5. The airway-on-chip paper and what we take from it

Bennet et al. 2026, Sci Rep (Cheung and Carlsten, UBC). `aoc_platform_impact_2026-10-11.md` is the long version.

**What they built.** Calu-3 airway epithelium at air-liquid interface over HFL1 fibroblasts in a GelMA hydrogel (0.44 to 7.5 kPa, tunable toward the 17 kPa fibrotic range), with a patterned vascular lumen about 250 µm across. Fibroblast monoculture, epithelium + fibroblast co-culture, and tri-culture with endothelium. Whole wood smoke deposited diffusely over the epithelium; TGF-β1 at 50 ng/mL perfused uniformly. 15 days, effluent sampled at days 3, 6, 12, 15.

**What they measured.** IL-6, IL-8 (Fig. 6c), MUC5AC, TGF-β1, MMP-2, LDH, vWF, and αSMA+ response by configuration. No collagen of any kind.

**What they found.** Wood smoke raised IL-6 and IL-8 significantly. MUC5AC and TGF-β1 rose modestly. LDH did not rise. MMP-2 stayed below detection. Their conclusion: early epithelial and pro-fibrotic responses without widespread cell death. Their caveats: dose "needs further optimization", n = 3 to 7 devices, effluent is pooled so no cell-type attribution.

**What it is to us.** An experimental companion in exactly our compartment and exposure, producing none of our observables. Three things it gives directly:

- A matched timescale: our 20,000 MCS = 14.4 days against their 15 days (this also closed the s/MCS decision).
- A matched condition for the S_M2 pedestal: their uniform TGF-β1 perfusion is what the pedestal represents.
- A stiffness knob for the forward predictions (H3, H4), post-paper.

And one thing it cannot give: validation of focal vs diffuse, because the chip is diffuse-only. That keeps the headline question novel and means the chip is not its validation route.

**The hypotheses it generated** (H1 to H8), where they ended up:

- H1 (signal without damage, f_d = 0): re-scoped to test whether the growth-factor-from-damaged-epithelium channel is needed; parked.
- H2 (damaged:healthy ratio scan): corrected to scan around the ODE's 2:1; parked.
- H3 (stiffness threshold), H4 (point of no return): described as forward predictions, not built.
- H5 (emit an IL-6/IL-8 analogue): folded into the readouts as one scalar column.
- H5a (ODE P vs their Fig. 6c): a consistency check and UBC material, decides nothing.
- H6 (report on their clock): folded into the readouts.
- H7 (mono vs co-culture ordering): ODE half holds by construction; tissue half is Gate C4.
- H8 (annular geometry): dropped.

## 6. Why "pro-inflammatory" keeps coming up

P is the ODE's immune-facing species: the cytokine pool that healthy and damaged epithelium (and M1 macrophages) make under exposure, and that polarizes resident macrophages toward M1. It matters for three separate reasons, which got tangled in October:

- **It is what the chip measures.** IL-6 and IL-8 are the chip's only significant response; P is our stand-in for them. If we want any model output on the chip's panel, it is P.
- **It is what the Frontiers topic is about.** Epithelial-immune interactions. P is the epithelial-to-immune signal; G is the immune-to-mesenchyme signal.
- **It is where the tissue layer had drifted from the ODE.** The ODE says damaged epithelium makes *P* at 2x the healthy rate (e6/e5 = 0.2/0.1). The tissue layer had damaged epithelium making *G* at 10x the healthy rate. Those are different claims with the same word "damaged" on them. The 10-23 split fixed the bookkeeping: A19a is the P claim (ODE-anchored, 2:1, not ours to validate), A19b is the G claim (tissue-layer, uncalibrated, scanned, argued on Kumar 2004, López-Guisa 2012, Checa 2016).

What the tissue does with P today: nothing. Fibroblasts read G. Conversion reads G. Damage reads f_d. A spatial P field would be dead weight (A17) unless something consumes it, and the natural consumer (EMT) is deferred because the evidence is thin (Zou: 3 of 8 rats; Tan 2021: about 2% of αSMA+ cells epithelium-derived) and because it confounds focal vs diffuse. That is the "consumer question": before building a P field, decide what reads it, or accept it as a readout layer only. The cheap path, if P output is wanted, is a scalar P-analogue computed from the lattice's cell counts and reported on the chip's clock, folded into the readouts.

## 7. How the direction changed, in four dates

- **10-11.** Chip read as a challenge: signal without LDH, versus a damage-first tissue layer. The v2 ranking is shaken; P and stiffness rise.
- **10-23.** Correction. The ODE already predicts the chip's result (E_d is reversible and sub-lethal; healthy epithelium secretes under exposure; the epithelial submodel was validated on cytokines, not viability). What the chip actually exposed were three departures of the tissue layer from its own ODE: no repair, an unsourced 10:1, and the wrong output species. Decisions: split A19, add the repair path ahead of the readouts, re-scope H1 and H2, add H5a.
- **10-26.** Five-gate roadmap (A to E) to a 1 May 2027 submission. Spatial P pulled to first in the v2 ranking. Gate A (ODE P vs chip) made the decider for article type. Antioxidant cut. ASM demoted hard (Zou: no ASM thickening under wood smoke). Volume-occupying ECM cell type demoted to post-paper (lumen narrowing is Tier 1 only; "the paper does not need −22%"). Annulus demoted. Bibliography batched.
- **10-27.** Review. Gate A cannot decide anything (P is a low-pass filter of WS; a normalized comparison cannot tell 2:1 from 1:1; mono-vs-co ordering holds by construction; any mismatch is uninterpretable). Order becomes B, D, C, E. Spatial P made conditional on Gate D passing and the consumer question. Article type turns on Gate D plus real tissue, as it did before October. Gate B built, pre-registered, run and closed the same day.

## 8. What has been accomplished (state as of tonight)

- A running 2D CPM of the small-airway wall with the published ODE integrated live inside it, one-way coupled through three channels, on a committed scale (1.25 µm/px, 62.4 s/MCS), with pinned-seed reproducibility and a replicate scan harness.
- Gate B closed: epithelial repair path from the ODE's e4 with M2/A enhancement; initial fibroblast count re-anchored to Zajicek 1992 (80 to 11); six replicates at 20k MCS.
- Standing baseline: lumen narrowing −0.3% to −4.2% (mean −2.5%, SD 1.4, n = 6). Sheet intact in every replicate, no collagen in the lumen, 1 to 7 repair events per run, final mesenchymal count 42 to 62. Tier 1 passes.
- A finding from B4: initial subepithelial occupancy is the dominant control on narrowing (the −12.3% at 80 fibroblasts was mostly an artefact of over-seeding). The gap to Higham's 22% is now about 9x and is logged as a limitation candidate, not a target.
- The assumptions (A1 to A19), validation targets (Tier scheme, Zou 2014 as primary anchor, Ripley's K pre-registration), evidence dossier, and a prior-art review are written and current.
- 93-entry bibliography, with the E1 batch list started and the abstract citations settled.

## 9. Objectives, in order

**Gate D, Dec 2026 to Jan 2027. The headline. Decides which paper exists.**
- Write the pass/fail criteria first (A18), stating that damage now has a finite lifetime.
- Fix d (mean epithelial cell diameter) before any K curve.
- Build the focal damage arm (diffuse exists; focal does not).
- Wire `spatial_stats.py` to model output.
- Run focal vs diffuse at matched total damage. Pass = separation on Ripley's K(r/d) while total collagen area fraction is statistically indistinguishable.
- Decide at this stage whether the 9x narrowing gap is calibrated away (recruitment, mitosis) or stated as a limitation.

**A1 to A3, November, alongside D prep. Not a gate.**
- A1: ODE P trajectory vs Bennet Fig. 6c, normalized shape and ordering. A Tellurium run.
- A2: ODE mono vs co-culture ordering.
- A3: chase supplementary S3 for dose and duration.
- Output: one figure for the UBC collaboration ask.

**Gate C, Jan to Feb 2027, only if D passes.**
- C2: the readouts (collagen area fraction, subepithelial thickness, myofibroblast density, fibroblast number), plus the P-analogue column and the chip's day 3/6/12/15 sampling.
- C4: mono vs co-culture ablation in the tissue model.
- C1 (spatial P field): only after the consumer question is decided.

**Gate E, Feb to May 2027.**
- E1: one Zotero identifier batch (list started).
- E2 to E4: draft, limitations, review. Submit 1 May for the 15 May deadline.

**Decisions that are yours, with dates**
- Approach the Cheung/Carlsten group at UBC? By December. A real-tissue K curve is the thing that would make this Original Research regardless of the chip.
- Does spatial P get a consumer? Before C1, if C1 happens.
- Split A19 in the dossier text (A19a / A19b). Early; it blocks C1 and the methods.
- Reconcile the non-monotonic dose response (Recillas-Román, Bennet's "needs optimization", H2) with the monotone damage-to-activation coupling. Limitations at minimum.

**Explicitly not in this paper:** volume-occupying ECM cell type, ASM, annulus, EMT, adventitia, antioxidant intervention, two-way coupling, MMP field, stiffness-gated latent TGF-β (described in §3 of the paper as forward predictions, not built).

## 10. The paper, as it stands

**Question.** Does the spatial pattern of epithelial injury, not its total amount, set the pattern of mesenchymal activation and subepithelial matrix deposition in the small airway under biomass-smoke exposure?

**Venue.** Frontiers in Immunology, Research Topic "Epithelial-immune interactions in lung immunity", Mucosal Immunity section. Deadline 15 May 2027.

**Article type.** Original Research if Gate D separates focal from diffuse on the spatial statistic and the paper can say plainly how the internal contrast relates to real tissue (UBC sections or a tissue bank). Hypothesis and Theory otherwise. Nothing about the chip comparison changes this.

**Sections.**
1. Focal vs diffuse injury at matched total damage, with the uniform S_M2 pedestal as the control holding immune drive flat. The CPM is justified here: an ODE cannot ask this question.
2. Epithelial-immune output against the chip (ordering and direction only; added only if D passes).
3. Forward predictions: stiffness threshold, point of no return (described, with Bennet's tunable hydrogel as the experimental counterpart).

**What can be written now, before any Gate D result.**
- Introduction and prior-art framing: Brown 2011, Islam 2023, Cogno 2022 in the first two paragraphs; the chip as the platform generating data in this niche with no model to interpret it.
- Methods: the whole of §2, §3 and §4 above is the methods section. The two-clock paragraph. The validation philosophy (Tier scheme, A18) and the pre-registered criteria.
- The Gate B result as a methods-validation paragraph (baseline, n, reproducibility).
- Limitations: cell lines vs primary (chip), 2D, no macrophages in tissue, lumped G, one-way coupling, the 9x narrowing gap, the two clocks, the non-monotone dose response, A19b uncalibrated.
- Everything in §1 of the results waits on Gate D; everything in §2 waits on C.

## 11. Things to notice when you sketch it

- There are exactly two scalar-ish inputs to the tissue that carry biology (S_M2 and f_d) and one rate (repair). Everything spatial is generated inside the lattice from the positions of damaged cells and myofibroblasts. That is the whole argument for the CPM.
- The only ratchet in the coupled system is C integrating a near-constant source. The ODE does not ratchet; it sits on a limit cycle. Progression is a tissue property.
- G is doing three jobs (chemotaxis, differentiation, mitosis) with two thresholds (0.45 and 0.225) and one uniform offset (S_M2). The focal-to-diffuse threshold for A14 is the S_M2 at which the Ripley's K signature becomes indistinguishable from uniform random. That is a scan over scenarios, not a longer run.
- Myofibroblast G secretion at 0.1 was an August experiment (100x the original), never a claim. It is one of the uncalibrated rates a reviewer will ask about.
