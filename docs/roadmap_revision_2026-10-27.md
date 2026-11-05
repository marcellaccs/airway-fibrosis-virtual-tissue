# Roadmap revision — 2026-10-27

> **Status note, 2026-10-29.** §2, §3 and §6 below are superseded by
> `roadmap_revision_2026-10-29.md`: the spatial `P` field is no longer conditional, MMP and a
> volume-occupying ECM cell type join this paper, a build gate B′ precedes Gate D, and Gate D runs
> as an ablation over the added loops. §1, §4 and §5 stand.

**Supersedes §4 (Critical path) of `roadmap_to_publication_2026-10-26.md` only.** §§1–3 and 5–7 of
that document stand; read §3's article-type line and §6's schedule table through this revision.
Does **not** supersede any assumption or validation target.

**Source:** a read-only review on 2026-10-27 accepted the 2026-10-26 reordering (spatial `P` ahead
of the volume-occupying ECM cell type) with one change: the Bennet comparator gets a narrower role,
and the headline experiment moves ahead of the spatial `P` build.

---

## 1. Gate A is no longer a gate

Run A1–A3 in November as written in the 2026-10-26 §4 — H5a (ODE `P` vs Bennet Fig. 6c, normalized
shape and ordering), the mono- vs co-culture ODE ordering, and the supplementary S3 chase — but as a
**descriptive consistency check** and as **material for the UBC ask**, not as a decision point.

- A pass does **not** promote the paper to Original Research.
- A fail does **not** cut §2 of the paper and does **not** skip Gate C.

**Why it cannot decide anything.** Four reasons, in the order they bite:

1. **`P` is a low-pass filter of the exposure waveform.** Both epithelial pro-inflammatory source
   terms in the ODE carry a multiplicative `F(WS)`:
   `P' = e5·WS·F(E_h) + e6·WS·F(E_d) + m6·WS·F(A)·(M1 + M1R) − m7·P`
   (the macrophage term carries `WS` too). With every source gated by exposure and a single linear
   decay, `P` rises when `WS` is on and relaxes when it is off, whatever the epithelial state does.
   Agreement with the chip on *direction* (`P` up under smoke) and *ordering* (exposed > control) is
   therefore near-automatic and tells us nothing about the tissue-layer claims.
2. **Gate A cannot discriminate A19a.** At the attractor `f_d` = 0.114, moving the damaged:healthy
   ratio from 1:1 to the ODE's 2:1 moves the epithelial `P` source by about 11 %
   (0.1 × 0.886 + 0.2 × 0.114 = 0.1114 vs 0.100). A normalized-shape comparison, which is the only
   comparison the pooled, n = 3–7 effluent data support, divides that amplitude out entirely. So
   H5a cannot tell a 2:1 world from a 1:1 world, and A19a is the claim that would have made Gate A
   worth gating on.
3. **A2's ordering holds by construction.** Both `P` sources sit on epithelial compartments
   (`E_h`, `E_d`). The fibroblast-only configuration has no epithelium, so its epithelial `P` is
   zero before the run starts. "Co-culture > monoculture on cytokine" is a property of the
   equations, not a prediction.
4. **A mismatch would be uninterpretable.** The comparison stacks: unknown dose placement on the
   chip (their own "exposure conditions need further optimization"), Calu-3 on the chip vs the A549
   data the submodel was validated on (Calcabrini 2004), a lumped `P` species against two named
   cytokines, pooled vascular-compartment effluent with no cell-type attribution, and n = 3–7
   devices. A fail could be any of those; none of them is a tissue-layer finding.

What A1–A3 still buy: a figure showing the ODE's `P` on the chip's 15-day clock next to their
IL-6/IL-8, which is the right opening for a collaboration ask to the Cheung/Carlsten group (2026-10-26
§6), and a dose figure from S3 if one exists.

## 2. Gate D moves ahead of Gate C

**New order: B → D → C → E.** Gate B (make the tissue layer honest) is unchanged in content and
still first. Gate D (the headline: focal arm, `spatial_stats.py` wired, focal vs diffuse at matched
total damage with the pre-registered Ripley's K criterion) runs **immediately after B**, over winter
break. Gate C (emit what the comparator measures) follows D.

**Why.** D is the only falsifiable test in the plan, and it decides which paper exists:

- D passes → there is an Original Research paper whose contribution is spatial, and Gate C is
  worth building so that §2 can be added to it.
- D fails → the paper is Hypothesis and Theory or a different paper altogether, and Gate C's
  tissue-layer `P` work would have been spent on a section of a paper that no longer has a spine.

Spending the one winter-break build window on C1 before knowing D's answer is the wrong bet. The
2026-10-26 §7 risk 1 said "know this by February"; under this order the answer comes in January.

## 3. C1 (spatial `P` field) becomes conditional

Build C1 **only if** (a) Gate D passes, (b) time remains before the drafting window, and (c) the
tissue-layer consumer question has been decided first.

**The consumer question.** A17 says, in its own words, that under A13 nothing in the v1 tissue
layer responds to the pro-inflammatory signal, so a spatial `P` field would be **dead weight**; `P`
is kept as an ODE scalar. The 2026-10-26 roadmap pulled `P` forward because the chip measures it,
but measuring it is an output argument, not a consumer. Nothing in the tissue today reads `P`:
fibroblasts chemotax on `G`, conversion gates on `G`, damage seeding gates on `f_d`. EMT, the
consumer A17 had in mind, **stays deferred** in the current plan (Zou: 3 of 8 rats; the
lineage-tracing literature; the focal-vs-diffuse confound). So before C1 is started, decide what in
the tissue responds to `P` — or accept that it responds to nothing and that C1 is a pure readout
layer.

**The cheap version, if `P` output is wanted regardless.** A `P`-analogue readout computed from
the existing epithelial state (H5 in `aoc_platform_impact_2026-10-11.md` §5): per MCS, a scalar
`P_analogue = e5·F(WS)·N_healthy_exposed + e6·F(WS)·N_damaged`, reported on the chip's clock
(days 3, 6, 12, 15). It is the ODE's own `P` source evaluated on the lattice's cell counts, it
inherits A19a's 2:1 directly, it needs no field, no solver and no consumer, and it folds into C2
(the readouts) as one more column. It gives up spatial structure in `P`, which is exactly the thing
nothing in the tissue uses yet.

## 4. Article type

Article type turns on **Gate D plus the real-sections question**, as it did before October
(`novelty_utility_review_2026-09-26.md` §4): Original Research if focal vs diffuse separates on the
spatial statistic and the paper can say plainly how the internal contrast relates to real tissue;
Hypothesis and Theory otherwise. **Not on Gate A.** The 2026-10-26 §3 line "Original Research if §2
lands" is read accordingly: §2 can strengthen an Original Research submission that D has already
earned, but it cannot create one.

## 5. Explicitly unchanged

- **Volume-occupying ECM cell type**: 5th in the v2 ranking, post-paper. The displacement gap is not
  on the critical path to this paper.
- **ASM demoted hard; annular geometry demoted.** As in 2026-10-26 §2.
- **The antioxidant intervention is cut from the current plan.** Its sign problem is unresolved, it
  is a spatial re-run of a published ODE result, and it operates partly through the `e4` repair
  term the tissue layer does not have until B1. Next paper.
- **Gate B in full**: B1 repair path from `e4`, B2 fibroblast re-anchor from Zajicek, B3 PSCAN with
  `iter_count` replicates, B4 one rebaseline after all three, with an n. Each pass/fail criterion
  written before running, per A18.
- **Bibliography batching** into one Zotero identifier run (2026-10-26 §5), with the A19a/A19b
  split and the non-monotonic-response reconciliation moved early.

## 6. The path, restated

| Order | Gate | Window | Decides |
|---|---|---|---|
| — | A1–A3 (not a gate) | Nov 2026, alongside B | Nothing. Consistency check; UBC material. |
| 1 | **B** — honest tissue layer | Nov–Dec 2026 | A baseline that post-dates B1–B3, with an n. |
| 2 | **D** — focal vs diffuse | Dec 2026 – Jan 2027 | **Which paper exists.** Original Research vs Hypothesis and Theory. |
| 3 | **C** — emit what the chip measures | Jan–Feb 2027, if D passes | Whether §2 is added. C1 only after the consumer decision; otherwise the `P`-analogue readout in C2. |
| 4 | **E** — write | Feb–May 2027 | Submit 1 May. |

Parked, unchanged from 2026-10-26: H1 (re-scoped), H2, H3/H4 (described, not built), the ECM cell
type, the antioxidant experiment, annulus, ASM, EMT, adventitia.
