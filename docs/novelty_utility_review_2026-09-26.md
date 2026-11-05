# Novelty and utility review — 2026-09-26

**Why this doc exists.** Marcella has committed to submit to *Frontiers in Immunology*, Research
Topic "Epithelial–immune interactions in lung immunity: regulation, reprogramming, and therapeutic
targeting in pulmonary disease" (Mucosal Immunity section; eds. Y. Peter Di, Renat Shaykhiev;
manuscript deadline 15 May 2027). Before more model work, this doc answers three questions: what is
the research question, is the model novel, and is it useful — i.e. can it be validated against
anything real.

Companion to `model_state_2026-09-26.md` (what is built) and `validation_targets.md` (what it would
be held against). Prior-art search run through Consensus on 2026-09-26.

## 1. The research question, resurfaced

Three questions are live in the docs, and they are not equally strong.

**Q1 (the recorded one): how does antioxidant treatment affect airway remodeling and fibrosis?**
`2025_project_status.md` §3 and `Model_Notes_digitized.md` §B.4 both name this as the driving
question. It is the weakest of the three:

- It is the spatial re-run of a result the ODE paper already published, so the finding is
  "the spatial model agrees," which is a validation exercise dressed as a result.
- It is **blocked**. Under the published scaling the intervention collapses epithelial damage
  (`f_d` 0.114 → 0.0012) but *raises* `M2_tot` 37% and `A` sevenfold, so the sign of the spatial
  result depends on which channel the ODE→tissue interface carries (spec §6, A-list note
  2026-08-04). That is a modeling choice, not a finding, and a reviewer will say so.
- Nothing in the intervention is spatial. It is a parameter change applied uniformly.

**Q2 (the one the validation doc already treats as the headline): does the spatial arrangement of
epithelial injury change the lesion at matched total injury?** `validation_targets.md` §3.6 calls
this "the model's actual contribution," and §5 ranks it first. Concretely: focal vs diffuse damage
seeding at matched total damage, separated on Ripley's K while collagen area fraction is
statistically indistinguishable, plus the `S_M2` value at which focal becomes diffuse (A14).

This is the strongest question because:

- It is a question a non-spatial model **cannot** ask. It justifies the whole CPM apparatus.
- It has a method precedent that makes it publishable rather than merely internal: Roop et al.
  (2026) found different Ripley's K distributions among preclinical samples with **similar Ashcroft
  scores and similar total fibrosis content** — exactly this claim structure, measured in tissue.
- It has a biological anchor: peribronchiolar fibrosis in wood-smoke exposure is described as focal,
  and diffuse interstitial fibrosis is reported absent (Zou 2014; Morán-Mendoza 2008).
- **It is not built.** Only the diffuse arm exists.

**Q3 (implicit, and the one that fits this journal): does epithelial damage geometry set where
mesenchymal activation happens?** This is Q2 restated as an epithelial-compartment question. It is
the same experiment; the difference is framing, and framing is what decides fit to this special
issue (§4).

**Recommendation:** the paper's question is Q2/Q3. Q1 becomes a secondary intervention section, or
is dropped, and the sign problem is stated as an open modeling question rather than resolved
quietly.

## 2. Novelty

Searched: agent-based and cellular-Potts models of airway-wall remodeling; multiscale
epithelial–immune models in COPD; spatial lung-fibrosis models; biomass vs tobacco COPD histology;
wood-smoke animal time courses.

**Closest prior art, and why each leaves room:**

| Work | What it is | Gap it leaves |
|---|---|---|
| Brown et al. (2011) | ABM of inflammation + fibrosis after **particulate** lung exposure; macrophages, fibroblasts, TNF-α, TGF-β1, collagen, damage. Three emergent states, matched to mouse histology | The closest in *exposure*. Abstracted tissue, not an airway-wall cross-section with a resolved epithelial sheet and a lumen; no focal-vs-diffuse spatial-statistic claim |
| Islam et al. (2023) | Multiscale PhysiCell model; collagen area fraction 2–40% driven by whether TGF-β sources are **stationary or mobile** and how long they persist | The closest in *claim structure* — source spatial behavior as the dominant lever. But alveolar tissue, COVID etiology, and the contrast is source mobility, not injury geometry |
| Cogno et al. (2022) | 3D ABM of radiation-induced lung fibrosis in an alveolar duct; ECM density histograms | Parenchyma, radiation, no airway wall |
| Hall et al. (2024) | ABM + spring-network hybrid; stretch **and** stiffness signals, latent TGF-β release, fibrotic threshold and bifurcation | Directly relevant to the planned v2 stiffness-gated activation. Parenchymal network, not an airway wall. Worth citing as the precedent for the v2 mechanism |
| Warsinske et al. (2016) | Hybrid multiscale ABM of fibroblast + epithelial co-culture, TGF-β1 receptor dynamics, PGE2 | Epithelial–mesenchymal, but co-culture geometry, IPF context |
| Hill et al. (2018) | Continuum morphoelastic model of the **asthmatic airway wall** with ASM and mechanotransduction | Same compartment. Continuum, not cell-based; asthma/ASM-driven; no injury-geometry question |

**What was not found:** any agent-based or cellular-Potts model of the **small-airway wall** under
**biomass / wood-smoke** exposure. Nor any spatial model asking whether injury *pattern* at matched
total injury changes the fibrotic lesion in an airway wall.

**So the novelty claim that survives is narrow and specific:**

> A cell-based virtual-tissue model of the small-airway wall, parameterized for biomass-smoke
> exposure and coupled to a published ODE model of the innate response, used to test whether the
> spatial pattern of epithelial injury — not its total amount — sets the pattern of subepithelial
> fibrosis.

Two things it is **not**: not the first ABM of lung fibrosis, and not the first model of
particulate-driven fibrosis. Claim neither. Brown (2011), Islam (2023) and Cogno (2022) must be
cited in the first two paragraphs, not buried — `citation_gap_report.md` already flags that not
citing them invites the novelty question.

The exposure specificity is a genuine and defensible contribution because biomass COPD is
phenotypically distinct: more small-airway disease and less emphysema (Zhao 2018; Camp 2013;
Ortiz-Quintero 2022), thicker basement membranes, and more macrophage/lymphocyte but **fewer
neutrophil** infiltrates (Zhao 2018) — which is the published basis for A10's macrophage-only
immune layer. Robles-Hernández et al. (2025) add severe peribronchiolar fibrosis in 60% of
biomass-COPD vs 10% of tobacco-COPD samples. The model is built for the phenotype that the
modeling literature has not addressed.

## 3. Utility: can this be validated?

Honest tiering, given the state in `model_state_2026-09-26.md`.

**Reachable now, or with todo item 4 (readouts) alone:**

- **Tier 1, lumen narrows inward.** Met (−8.6% to −17.2%, n = 6 pinned).
- **Exposed > control on collagen**, as a ratio. Zou (2014) now gives the exposure-matched number:
  ~2.0× total collagen and ~1.9× wall thickness at 7 months, wood smoke vs clean air. This is a
  better anchor than the ~3× inferred from Kong (2023), which is large-airway biopsy. **Revise the
  §3.1 target down.**
- **Late > early.** Zou (2014) is the clean statement: no significant collagen difference at
  4 months, significant at 7. Ordinal, no units needed.
- **Myofibroblasts in a shallow band just deep to the basement membrane, non-uniformly
  distributed** (Eapen 2021, descriptive). A spatial-pattern target that needs no calibration and
  that the model can be checked against as soon as a myofibroblast-density readout exists.
- **Hoshino correlation** (thickness vs fibroblast number across an `R_fib` sweep). Needs the
  thickness readout and the sweep; nothing else blocks it.
- **Eapen correlation structure** (myofibroblast density co-varying with thickness and collagen
  within a run): r′ = 0.43 LP myofibroblasts vs LP thickness; r′ = 0.59 collagen-1 % vs LP
  thickness in COPD-CS. Correlational, unit-free, and it tests the coupling rather than an endpoint.

**Blocked on work not yet done:**

- **Focal vs diffuse on a spatial statistic.** The headline. Needs the focal arm built. The
  statistic itself is written (`model/analysis/spatial_stats.py`) but not wired to model output.
- **A measured K curve from real tissue** to compare against. `validation_targets.md` §3.7 names
  this the gating item. Obtaining biomass small-airway sections is an external dependency, not a
  coding task, and it is the single largest risk to the headline claim. Without it, focal-vs-diffuse
  is an internal contrast — still interesting, but a model result about a model.

**Not reachable, and this should be stated in the paper before a reviewer states it:**

- **Absolute collagen area fraction.** A7 forbids it, and the anchors do not agree in units anyway:
  Kong (2023) reports % of tissue area, Zou (2014) reports µm² per µm of basement-membrane
  perimeter, Eapen (2021) reports % staining by compartment. These are three different quantities.
  Report ratios.
- **αSMA⁺ per mm² with dispersion.** Eapen's full text has no table; the values are in figures only.
  Same for Tisler Fig 3B. Both stay *(verify)* until digitized. The §6 follow-up item is therefore
  only partly closable.
- **The degradation limb.** No MMPs in v1, and Zou (2014) found MMP9/MMP2/TIMP1 all upregulated and
  localized to the airway epithelium in exactly this exposure. A known, citable omission.
- **The compartment where the collagen signal is largest.** Eapen (2021) found collagen-1 up only
  ~1.5× in the lamina propria but 5–6× in the adventitia. v1 has no adventitia (it is the frozen
  boundary). So the model addresses the weaker of the two signals in the human data.
- **Fibronectin.** More responsive than collagen in Eapen; a single lumped C field cannot separate
  species.
- **RBM thickness.** One pixel wide at 1.25 µm/px.

**One new piece of support for A8/v2 scoping:** Zou (2014) found **no significant ASM thickening**
under wood smoke or cigarette smoke. That argues the v2 airway-smooth-muscle compartment is not
needed to reproduce *this* exposure's lesion, and it strengthens the A8 frozen-boundary device. The
adventitial compartment, by contrast, now looks like the higher-value v2 addition.

**Overall verdict on utility.** The model can be validated at Tier 2 on four or five targets, and
the targets are real, exposure-matched, and already in hand. It cannot be validated at Tier 3 on
anything. The headline claim is validatable only as an internal contrast unless real sections are
obtained. That is a publishable position — Islam (2023) and Cogno (2022) both stopped at
dynamics/ranges and shape agreement — provided the paper says so plainly.

## 4. Fit to the Frontiers topic, and what it would cost

The topic is **epithelial–immune interactions**: epithelial barrier regulation, innate immune
sensing by airway epithelium, epithelial-derived cytokines, epithelial–immune reprogramming from
environmental exposure, COPD pathogenesis. Accepted types include **Original Research**, **Methods**,
**Hypothesis and Theory**, and **Technology and Code** — computational work is in scope.

**The mismatch, stated plainly.** In v1 the immune compartment is *not in the tissue*. A10 puts
macrophages in the ODE only, and the entire immune contribution reaches the lattice as two scalars,
`S_M2` (a spatially uniform pedestal on the growth-factor field) and `R_fib`. The epithelium is a
GF source that gets damaged; it does no sensing, and there is no immune cell for it to interact
with spatially. A paper submitted as-is is a fibroblast/ECM mechanics paper in an
epithelial–immune issue.

Three ways to close that, in increasing cost:

1. **Reframe, build nothing new beyond the focal arm.** The epithelium *is* the spatial organizer
   in this model: damaged epithelial cells are the stationary GF sources, and the focal-vs-diffuse
   question is precisely "does the geometry of epithelial injury determine where mesenchymal
   activation occurs, at matched immune drive?" The uniform `S_M2` pedestal becomes a feature, not
   an embarrassment — it is the experimental control that holds the immune drive spatially flat so
   that any spatial structure in the lesion must come from the epithelium. That is a clean,
   defensible epithelial-compartment claim, and it needs only the focal arm plus readouts.
   *This is the recommended route.*
2. **Make `S_M2` spatial.** Replace the uniform pedestal with a macrophage field or macrophage
   agents, so epithelial-derived signal recruits immune cells that then feed back. This is the
   honest "epithelial–immune crosstalk" model and would fit the topic squarely. It is a v2-scale
   build and reopens A10 and the ODE reduction (A11).
3. **Add the epithelial sensing layer** (pattern recognition → epithelial cytokine output as a
   function of local exposure, rather than a Bernoulli damage flip). Closest to the topic keywords,
   largest build.

Route 1 with an honest limitations paragraph naming route 2 as the next increment is the realistic
plan for a May 2027 deadline. Note the deadline is **15 May 2027**, not May 2026 — there is more
runway than assumed, which makes route 2 arguable if the focal arm lands early.

**Article type.** If the focal-vs-diffuse result holds and gets even one real-tissue comparison,
submit as **Original Research**. If the real sections do not materialize, **Hypothesis and Theory**
is the honest type and does not require the external validation; it also gives room for the
"spatial arrangement matters at matched burden" argument as the contribution.

## 5. What has to be true for this paper to work

In dependency order:

1. **Readouts exist** (collagen area fraction, subepithelial thickness, myofibroblast density).
   Todo item 4. Everything below needs them.
2. **The focal arm is built** and focal vs diffuse can be run at matched total damage.
3. **The spatial statistic separates them** while total collagen does not. If it does not, the CPM
   justification thins and the paper becomes a different, weaker paper. This is the real scientific
   risk and it should be tested before any writing starts.
4. **Replicate machinery** (PSCAN / `iter_count`) so the separation has an n and a p-value.
5. **Real sections**, ideally. Nice-to-have for Original Research; not required for Hypothesis and
   Theory.
6. **The initial fibroblast count is re-anchored** (todo item 5) so the baseline is not a leftover
   from a displacement experiment.

Items 1–4 are entirely within the repo's control.

## 6. Open questions for Marcella

- Which framing: route 1 (reframe around epithelial injury geometry) or route 2 (build a spatial
  immune compartment)? The answer changes the v2 priority list.
- Is the antioxidant experiment in or out of this paper? If in, the sign problem must be settled
  first.
- Is there a realistic route to biomass-exposed small-airway sections (collaborator, tissue bank,
  the Roop group)? The answer decides Original Research vs Hypothesis and Theory.
- Should the adventitial compartment jump ahead of ASM in the v2 list, given Zou's null ASM result
  and Eapen's 5–6× adventitial collagen?
