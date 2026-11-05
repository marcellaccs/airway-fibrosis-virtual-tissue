# Roadmap to publication — 2026-10-26

**Target:** *Frontiers in Immunology*, Research Topic "Epithelial–immune interactions in lung
immunity," Mucosal Immunity section. **Manuscript deadline 15 May 2027** (~6.5 months).

**Inputs reviewed:** `cc3d_v1_todo.md` (items 0–5 + carried infra), `model_spec_v1_v2.md` (v2
objects/fields/behaviors/prediction goals), `validation_targets.md` §§1–9, the Notion Academic
Tasks rows for *CC3D model v1*, *Citations & evidence dossier*, *Write the paper* and
*Toxicology Virtual Tissue*, and the two 2026-10 reassessments
(`aoc_platform_impact_2026-10-11.md` incl. §2A, `novelty_utility_review_2026-09-26.md`).

Supersedes the priority ordering in `novelty_utility_review_2026-09-26.md` §5 and the v2 ordering
in `model_spec_v1_v2.md` §v2. Does **not** supersede any assumption or validation target.

> **Status note, 2026-10-27.** §4 (Critical path) below is superseded by
> `roadmap_revision_2026-10-27.md`, following a read-only review that accepted the reordering in §1
> with one change. In short: Gate A is no longer a gate (A1–A3 run in November as a descriptive
> consistency check and UBC material, deciding nothing); the gate order is **B → D → C → E**; C1
> (spatial `P`) is conditional on D passing, time remaining, and a prior decision on what in the
> tissue consumes `P`; article type turns on Gate D plus the real-sections question, not on Gate A.
> §§1–3 and 5–7 stand; read §3's article-type line and §6's schedule through the revision. §4 is
> kept below as written for provenance.

---

## 1. The one decision that reorders everything

**The v2 component that matters for this paper is the spatial pro-inflammatory field `P`, not the
volume-occupying ECM cell type.**

`model_spec_v1_v2.md` §v2.2 lists `P` as "promoted from an ODE scalar once EMT gives it a target."
That justification is now wrong, and four independent things say so:

1. **The journal.** The Research Topic is epithelial–immune crosstalk. `P` is the immune-facing
   species in this model. ECM mechanics is not.
2. **The ODE already emits it.** `dP/dt = e5 F(WS) F(E_h) + e6 F(WS) F(E_d) − e7 P`, validated
   against Calcabrini (2004). No new biology is required to make it spatial — only to stop
   collapsing it to a scalar at the interface.
3. **The chip measures it.** Bennet et al. report IL-6 and IL-8 as their *only* statistically
   significant exposure response. The model currently emits nothing from their assay panel.
4. **A19a is about `P`.** The 2026-10-23 correction established that the ODE-anchored secretion
   claim (2:1 damaged:healthy) is a pro-inflammatory claim. The tissue layer has no `P` to carry it.

Consequence: the 2026-09-06 decision that prioritized the volume-occupying ECM cell type stands as
*the* answer to the displacement gap, but the displacement gap is **not on the critical path to
this paper**. Lumen narrowing is Tier 1 (a sanity check) in `validation_targets.md` §3.5. The paper
does not need −22%.

---

## 2. What is now obsolete, and what changed under it

### Close as done

| Item | Why |
|---|---|
| **v1 item 1 — "pick the s/MCS anchor"** | Picked. 62.4 s/MCS (IPF/IPF, Tisler) is the committed baseline in `parameters.py`, A7 and `model_state_2026-09-26.md`. Bennet independently corroborates it: at 62.4, a 20,000-MCS run is 14.4 days, matching their 15-day culture window; the 109.5 alternative would give 25.3 days and *mismatch* it. The limitation statement stays in A7; the open decision does not. |
| **"Decide what to do with the ~30% spread the new anchors expose"** | Decided. `validation_targets.md` §7 already states the resolution: quote µm/px as ~0.85–1.25 with 1.25 chosen, not as a settled single value. |
| **"Get Eapen2021 full text"** | Done 2026-09-26. Correlations and the shallow-band description extracted into §8.2. What remains is figure digitization, which is its own task. |
| **"Decide: does the damaged:healthy ratio need a validation-target row?"** | Superseded by the A19a/A19b split, which answers it: A19a's 2:1 is an ODE parameter, not a validation target; A19b's ratio is a scanned parameter. |

### Delete

| Item | Why |
|---|---|
| **"Add inline citations to the assumptions deck"** | The lightning-talk decks were removed from the repo 2026-09-06 (`e4e20e6`). There is no deck. The citations live in A1–A19 and the evidence dossier, which is where a manuscript draws from. |
| **Doc drift: "Slide 8 calls ECM a density field"** | Same reason. No slide. |

### Downgrade to Low / footnote

| Item | Why |
|---|---|
| **"Clear the Tisler2020 *(verify)* flag"** | It was load-bearing only while s/MCS was unpicked. Now it is a provenance footnote on a committed, independently corroborated number. Digitizing Fig. 3B changes nothing downstream. |
| **"Find a small-airway-specific human epithelial cell width"** | Searched 2026-09-04, not found. Convert from an open hunt to a stated limitation in A7. Reopen only if a reviewer asks. |
| **"Find wood-smoke-specific replacements for Checa2016 / Baarsma2022"** | The exposure gap is substantially closed from both ends: Recillas-Román (2021) gives wood-smoke-extract fibroblast responses, and Bennet (2026) gives whole wood smoke on epithelium + fibroblasts at ALI. Keep the proxies, label them, cite the two new sources. |

### v2 components, re-ranked for this exposure and this paper

| v2 component | Old standing | New standing | Reason |
|---|---|---|---|
| **Spatial `P` field** | "once EMT gives it a target" | **1st — on the critical path** | §1 above. |
| **Stiffness-gated latent TGF-β activation** | 1st (the autocatalysis story) | **2nd — the forward predictions** | Still the only mechanism giving hysteresis and point-of-no-return. Now also has an experimental counterpart: Bennet tune GelMA across native (0.44–7.5 kPa) to fibrotic (~17 kPa). Precedent: Hall et al. (2024). |
| **Adventitial compartment** | listed, unranked | **3rd — promote** | Eapen: collagen-1 up ~1.5× in lamina propria but **5–6× in adventitia**. Zou: peribronchiolar fibrosis. The wood-smoke literature measures the compartment v1 does not have. |
| **MMP field** | listed | **4th — keep, cite meanwhile** | Zou found MMP9/MMP2/TIMP1 all raised and epithelium-localized in exactly this exposure. Until built, this is a *citable* known omission (`validation_targets.md` §4), not an oversight. |
| **Volume-occupying ECM cell type** | prioritized 2026-09-06 | **5th — post-paper** | Right answer to the displacement gap; the displacement gap is not what this paper claims. |
| **EMT** | deferred (A17) | **stay deferred** | Zou found E-cadherin/vimentin double-positive cells in only **3 of 8** wood-smoke rats. Weak in this exposure. |
| **Airway smooth muscle** | "replaces the fixed outer boundary" | **demote hard** | Zou found **no significant ASM thickening** under wood smoke or cigarette smoke. A8's frozen boundary is adequate for this exposure, and that is now a citable justification rather than a simplification. |
| **Annular geometry** | listed | **demote** | Bennet's stromal compartment is bulk hydrogel around a vascular lumen, not a radially organized wall, so an annulus would not improve the model-vs-chip match. Keep the slab, describe it as a local wall-segment approximation. |

---

## 3. The paper, stated once

> **Does the spatial pattern of epithelial injury — not its total amount — set the pattern of
> mesenchymal activation and subepithelial matrix deposition in the small airway under
> biomass-smoke exposure?**

Three sections:

1. **Focal vs diffuse at matched total injury.** The contribution. Only a spatial model can ask it.
   The uniform `S_M2` pedestal is the *control* that holds immune drive spatially flat, so any
   structure in the lesion must come from the epithelium. (That reframing is what makes this an
   epithelial-compartment paper rather than a mechanics paper.)
2. **Epithelial–immune output, validated against an in vitro comparator.** The ODE's `P`, made
   spatial, against Bennet's IL-6/IL-8 and across their mono- vs co-culture configurations.
3. **Forward predictions the platform can test.** Stiffness threshold for self-sustaining
   activation; reversibility / point of no return.

Article type: **Original Research** if §2 lands. **Hypothesis and Theory** if it does not — that
fallback requires no external validation and still carries §1 and §3.

---

## 4. Critical path

Five gates. Each must pass before the next is worth starting.

### Gate A — Does the signal layer survive contact with the comparator? *(Nov 2026)*
*No tissue-model code.*

- **A1. H5a.** ODE `P` trajectory vs Bennet Fig. 6c. Normalized shape and ordering only.
- **A2.** Re-run the ODE across the chip's configurations (fibroblast-only vs epithelium+fibroblast)
  and check the ordering matches (H7's signal-layer half).
- **A3.** Chase Bennet supplementary S3 for PM2.5 concentration and exposure duration. If it gives
  numbers, that is the first dose figure matched to a platform this project has.

**Gate:** if `P` reproduces the chip's direction and ordering, §2 of the paper exists and the target
is Original Research. If it does not, cut §2, go Hypothesis and Theory, and skip Gate C.

### Gate B — Make the tissue layer honest *(Nov–Dec 2026)*
*Three changes that alter what every later number means. Do them together, then rebaseline once.*

- **B1. Repair path** for `EpitheliumDamaged`, rate from the ODE's `e4` (≈3.5e-5 per MCS per
  damaged cell at 62.4 s/MCS). Decide whether to carry the M2/`A` enhancement.
- **B2. Re-anchor `FIBROBLAST_INITIAL_NUMBER`** (80 → ~11 or ~16–17, Zajicek). Pick the reading
  that makes the chip's seeding comparison cleanest.
- **B3. PSCAN + `iter_count` replicates.** Carried open since 2026-09-04. Everything after this
  needs an n and a p-value; doing it by hand does not scale.
- **B4. Rebaseline** the 20k replicates after B1–B3. The −12.3% mean was measured at 80 fibroblasts
  with no repair path.

**Gate:** clean runs, a replicate spread, and a baseline that post-dates all three changes.

### Gate C — Emit what the comparator measures *(Dec 2026 – Jan 2027)*

- **C1. Spatial `P` field** (v2 component, pulled forward). Sources per A19a: damaged epithelium at
  ~2× the healthy exposed rate. This is the single largest build in the plan.
- **C2. The readouts** — v1 item 4: collagen area fraction, subepithelial thickness, myofibroblast
  density, fibroblast number. Write each pass/fail criterion **before** running, per A18.
- **C3. Report on the chip's clock** — days 3, 6, 12, 15 alongside MCS checkpoints. Free.
- **C4. H7 proper** — mono- vs co-culture ablation in the tissue model.

**Gate:** the model emits at least one quantity Bennet also measures, and the §5 minimal validation
set is computable.

### Gate D — The headline experiment *(Jan–Feb 2027)*

- **D1. Focal damage arm.** Still unbuilt; it is the one thing the paper cannot be written without.
- **D2. Wire `spatial_stats.py` to model output.** Fix `d` (mean epithelial cell diameter) *before*
  generating any curve, and record it.
- **D3. Focal vs diffuse at matched total damage**, n from B3, with the pre-registered criterion:
  separation on Ripley's K while collagen area fraction is statistically indistinguishable.

**Gate:** this is the real scientific risk. If the statistic does not separate the two arms, the CPM
justification thins and the paper becomes a different, weaker paper. **Know this by February**, not
in April.

### Gate E — Write *(Feb–May 2027)*

- **E1.** Bibliography close-out (§5 below).
- **E2.** Draft §1–§3. Cite Brown 2011, Islam 2023, Cogno 2022 in the **first two paragraphs** —
  `citation_gap_report.md` has flagged since 2026-08 that not citing them invites the novelty
  question.
- **E3.** Limitations, written from `validation_targets.md` §4 and the A19b/MMP/ASM notes above.
- **E4.** Internal review, submit by 1 May with two weeks of slack.

### Parked — not on the path

H1 (re-scoped), H2 (ratio scan), H3/H4 (stiffness and reversibility — these are §3's forward
predictions and can be *described* without being built), the volume-occupying ECM cell type, the
antioxidant experiment, annular geometry, ASM, EMT, adventitia.

**The antioxidant experiment should be cut from this paper.** Its sign problem (spec §6) is
unresolved; it is a spatial re-run of a published ODE result; and the 2026-10-23 finding gives a
second, independent reason it cannot work yet — the intervention operates partly through the `e4`
repair term, which the tissue layer does not have until B1. It belongs in the next paper.

---

## 5. Bibliography close-out (Gate E1, but start it early)

Batch into **one** Zotero identifier run rather than the current scatter of per-source tasks:

- `Bennet2026` (DOI 10.1038/s41598-026-69468-5) + the PDF into `literature/bio_lit`.
- **The project's own ODE paper** — still not in `references.bib`. Check the published JTB version
  against the manuscript PDF before quoting `e3`–`e6` anywhere.
- The nine A19 papers, the nine A7 papers, the ~24 `bio_lit` PDFs not yet reconciled.
- The 2026-09-26 prior-art set: `Hall2024`, `Warsinske2016`, `Hill2018`, `RoblesHernandez2025`,
  `Camp2013`, `LeonardDuke2020`.
- Decide the four conference abstracts / preprint (`Kong2023`, `Higham2022`, `Suzuki2010`, …) —
  with Zou now the primary quantitative anchor (§8.1), the abstracts are context and can be cited
  as such or dropped.

Two substantive citation items that are **not** clerical and should move early:

- **Split A19 into A19a / A19b.** Blocks C1, because A19a is what the spatial `P` field implements.
- **Reconcile the non-monotonic exposure response with the monotonic damage→activation coupling.**
  Recillas-Román's trimodal dose response, Bennet's "exposure conditions need further optimization,"
  and H2's ratio scan all bear on the same question. This is the most intellectually live item in
  the dossier and it deserves to be in the paper's limitations at minimum.

---

## 6. Schedule against the teaching year

| Window | Gate | Notes |
|---|---|---|
| Nov 2026 | A | Light build. Fits alongside teaching. |
| Dec 2026 – Jan 2027 | B, start C | Winter break is the main build window. C1 is the big one. |
| Jan – Feb 2027 | finish C, D | Spring term starts; D1–D3 are the priority. |
| Feb 2027 | **Gate D decision** | Go / no-go on Original Research vs Hypothesis and Theory. |
| Feb – Apr 2027 | E | Drafting. |
| 1 May 2027 | submit | Two weeks' slack before the 15 May deadline. |

**External dependency, decide by December:** whether to approach the Cheung / Carlsten group at
UBC. It bears on `validation_targets.md` §3.7 (a measured K curve from real tissue), and Carlsten
is a plausible referee for this issue either way. A collaboration is more tractable than tissue-bank
access, and the ask is much stronger *after* Gate A produces a result about their data.

---

## 7. Honest risks

1. **Gate D may fail.** If focal and diffuse do not separate on the spatial statistic at matched
   burden, the paper's contribution evaporates. Mitigation: reach Gate D by February, and keep
   Hypothesis and Theory as the fallback type — it can carry the argument without the result.
2. **C1 is a v2 component being pulled into a v1 timeline.** The spatial `P` field is the largest
   single build here and the schedule gives it one winter break. If it slips, Gate C collapses to
   C2–C3 only, §2 of the paper narrows to the signal-layer comparison from Gate A, and the article
   type likely drops to Hypothesis and Theory.
3. **No real tissue sections.** §3.7 stays gated. The focal-vs-diffuse result remains an internal
   contrast unless the UBC route or a tissue bank opens. Islam (2023) and Cogno (2022) both stopped
   at dynamics and shape agreement, so this is publishable — but it must be said plainly.
4. **Single-author modeling paper in an immunology issue.** The reframing in §3 is what makes it fit.
   If reviewers read it as a mechanics paper submitted to the wrong venue, the framing failed, not
   the science.
