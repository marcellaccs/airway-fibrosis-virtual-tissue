# Impact of the Bennet et al. (2026) airway-on-a-chip on this model

**Date:** 2026-10-11. Companion to `novelty_utility_review_2026-09-26.md`, which this partly
supersedes. Read §3 of that doc (utility) with this one.

**Source:** Bennet, T. J., et al. (2026). Engineering a multilayer microfluidic airway-on-a-chip with
tunable GelMA hydrogel for physiologically relevant aerosol exposure studies. *Scientific Reports*.
https://doi.org/10.1038/s41598-026-69468-5. Full platform description and results are summarized in
`lab-notebook/2026/2026-10-11.md`.

## 1. Verdict

The work is not superseded. The chip is an **experimental companion**, not competing prior art: it
occupies the same compartment and exposure as the model and produces none of the same observables.
Its existence raises the value of the model in three ways and damages it in one.

The one place it damages the model is the important part, so it goes first.

## 2A. Correction, 2026-10-23: the challenge was aimed at the wrong layer

*Added after re-reading the project's own ODE paper (Torres et al., Development of a Mathematical
Model of the Innate Immune Response to Inhaled Toxicants; PDF in `literature/math_models_lit/`).
§2 below is kept as written for provenance, but its conclusion is superseded by this section.*

**The published ODE already predicts the chip's result.** Bennet et al. corroborate the signal
layer rather than contradict it:

| ODE fact | Source in the paper | Consequence |
|---|---|---|
| `E_d` is **reversible and sub-lethal**: repair `E_d → E_h` at `e4 = 0.002 h⁻¹` | Table 1 reaction scheme; Eqs. (1)–(2); Table 2 | Nothing in the "damaged" state would release LDH |
| Damaged cells die at the **same** natural rate as healthy ones (`e2 = 0.001`) and still proliferate | Table 1 | "Damaged" ≠ dying |
| `r = e3/(e2 + e4)` is defined as damage creation over removal **by repair or natural death** | stability analysis, §3 | Reversibility is structural, not incidental |
| Healthy epithelium secretes pro-inflammatory cytokine **under exposure**: `e5 F(WS) F(E_h)`, `e5 = 0.1` vs `e6 = 0.2` damaged | Eq. (3), Table 2 | The ODE's damaged:healthy ratio is **2:1**, and it is gated by **exposure**, not by damage |
| M2 and anti-inflammatory cytokine **enhance** repair: `e4(1 + e8(M2 + M2_R) + e10 A)` | Eq. (16) | Repair is load-bearing; the published antioxidant intervention runs partly through it |
| Subsystem validated against Calcabrini et al. (2004): A549, PM2.5, IL-6 and TNF-α over 72 h | §2.4.1 validation | Validated on **cytokine release, not viability** — the same readout class the chip reports |

So reading (2) in §2 — that LDH is blind to the sub-lethal stressed state v1's "damaged" label
actually denotes — is **confirmed by this project's own signal layer**, not merely plausible.
Readings (1) and (3) are not refuted but are no longer needed to reconcile the chip.

**What is actually challenged: three tissue-layer departures from the ODE.**

1. **One-directional damage.** The ODE has `e4`, plus M2-enhanced repair. The tissue layer dropped
   both, making v1 more irreversible than the signal layer feeding it. A repair path should be
   added, with the rate derived from `e4` scaled to MCS. This changes what every readout measures,
   so it belongs **ahead of** todo item 4.
2. **The 10:1 secretion ratio has no ODE provenance.** The ODE's ratio is 2:1. The 10:1 was a
   first-pass tissue-layer choice and was never inherited from anywhere.
3. **The output species was swapped.** The ODE's epithelium produces pro-inflammatory `P`. A19 has
   damaged epithelium producing the **growth-factor** field `G` — a different claim wearing the
   ODE's label. Not unfounded (Kumar 2004, López-Guisa 2012, Checa 2016 support epithelial TGF-β),
   but it must be argued on that evidence rather than inherited from the ODE.

**Split A19** into A19a (pro-inflammatory secretion, ~2:1, ODE-anchored) and A19b (growth-factor
secretion, uncalibrated ratio, tissue-layer assumption).

**Revisions to the hypotheses in §5.**

- **H1 is re-scoped.** `f_d = 0` with the pedestal alone now tests whether the *GF-from-damaged-
  epithelium* channel is necessary, not whether damage is. Lesion forms → A19b is dispensable in
  v1. No lesion → A19b is load-bearing and needs the stronger evidentiary case.
- **H2's range is wrong.** Scan the **pro-inflammatory** ratio around the ODE's 2:1. The GF ratio
  has no ODE anchor and stays a scanned parameter.
- **H5 gains a cheaper sibling, H5a.** The ODE already emits `P`, and the chip measures IL-6 and
  IL-8. Comparing the ODE's `P` trajectory against Bennet Fig. 6c needs **no tissue-model code at
  all** — it is the Calcabrini validation redone against a whole-smoke, ALI, co-culture dataset.
  Run it first.
- **New: a repair path in the tissue layer** (above), ahead of the readouts.

## 2. The challenge to A14 / A19: signal without damage

Whole wood smoke raised IL-6 and IL-8 significantly and MUC5AC and endogenous TGF-β1 modestly, with
**no significant LDH release**. Their own framing: the exposure conditions "did not induce widespread
cell death," and the responses represent "the initiation of early epithelial and profibrotic
responses."

The v1 model's causal chain is damage-first:

- `f_d` from the ODE drives per-cell Bernoulli damage trials.
- `EpitheliumDamaged` secretes GF at **0.1**; `EpithelialHealthy` at **0.01**. A 10:1 ratio.
- Damage is one-directional. No repair path exists.

So in-model, essentially all exposure-driven growth-factor signal above the healthy baseline comes
from cells that have been damaged. The chip produces the signal without the damage.

Three readings, and they are not equally likely:

1. **Dose.** Their proof-of-concept exposure may sit below the damage threshold while still above
   the signaling threshold. Plausible — they say exposure conditions need further optimization and
   that dose-response work is future. If so the model is right about the mechanism and wrong only
   about where the chip sits on the curve.
2. **LDH is insensitive.** LDH detects lytic death. Sub-lethal epithelial stress, barrier
   disruption, or a senescent/activated phenotype would not show. The model's "damaged" state may
   correspond to something LDH cannot see, in which case the label is wrong rather than the
   mechanism.
3. **The ratio is too steep.** Healthy epithelium under exposure may secrete far more than 1/10 of
   the damaged rate, making damage a modifier rather than a gate.

(2) and (3) both argue the 10:1 ratio is the wrong number and that it was never calibrated — it is
first-pass and the docs already say so. (1) argues it is fine. **The model can distinguish them**,
which is the point of H1 and H2 below.

A19's separate decision — that healthy epithelium secretes at a **nonzero** rate rather than 0 — is
**supported** by this paper. Without it the chip's result would be unreproducible in-model at any
parameter setting.

## 3. What the platform gives the model

**3.1 The timescales already agree.** Their culture-and-exposure window is 15 days; co-cultures were
established for 15 days before exposure, with effluent sampled at days 3, 6, 12 and 15. A
20,000-MCS run at A7's 62.4 s/MCS is **14.4 days**. The model's natural run length is the chip's
experimental window, with no recalibration and no new judgment call. Model output should be reported
at days 3, 6, 12, 15 as well as at MCS checkpoints.

**3.2 Their TGF-β1 delivery is `S_M2`.** 50 ng/mL perfused continuously and uniformly through the
upper microchannel is a spatially uniform additive pro-fibrotic source applied to a fibroblast
population in 3D ECM. That is A14's uniform pedestal, built in PDMS. The docs currently present the
pedestal as a simplification to be defended; against this platform it is the **matched condition**.
Reframe it wherever it appears.

**3.3 The stiffness knob exists.** They selected 6% GelMA/0.6% LAP for a Young's modulus inside the
native lung range (0.44–7.5 kPa), and state explicitly that tuning GelMA stiffness toward the
fibrotic ECM range (~17 kPa) is a route to disease-specific microenvironments. The planned v2
mechanism — stiffness-gated activation of latent TGF-β, the only thing that makes remodeling
self-sustaining — now has an experimental counterpart with a named target value. A model prediction
about the stiffness at which activation becomes self-sustaining is testable on their platform by
changing one reagent concentration.

**3.4 Geometry.** Their patterned lumen is ~250 µm in diameter; the model domain is 250 µm wide
(200 px at 1.25 µm/px). Their upper channel is 1 mm, matched to a bronchiole. This does **not** argue
for rebuilding the model as an annulus: their fibroblast compartment is a bulk hydrogel surrounding a
vascular lumen, not a radially organized airway wall, so an annular model would not be better matched.
It does mean the two can be drawn at the same scale in a figure.

**3.5 Prior art framing is unchanged and slightly strengthened.** Still no cell-based model of the
small-airway wall under biomass exposure. The chip's existence makes the modeling gap more
conspicuous, not less: there is now a platform generating data in this exact niche and no model to
interpret it.

## 4. What it does not give

- **No collagen.** No area fraction, no thickness, no Masson or picrosirius quantification. The
  fibrotic endpoint the model produces is not measured on this platform yet.
- **MMP-2 below LLOQ** (0.5 ng/mL) throughout. They call this a functional baseline against which
  future exposure-induced remodeling can be evaluated. Useful to cite, not usable as a target.
- `Zou2014` therefore remains the only exposure-matched quantitative anchor. Nothing in
  `validation_targets.md` §8.1 changes.
- **Cell lines, not primary.** Calu-3 lacks ciliated and club cells; HFL1 is fetal. They flag both.
  Any model-vs-chip comparison inherits this limitation and should say so.
- **Diffuse injury only.** Smoke arrives by tangential airflow with gravity-driven deposition across
  the whole epithelial surface. There is no focal-injury configuration. The headline focal-vs-diffuse
  question is therefore **not** validatable on this platform — which preserves its novelty and
  removes it as a validation route in the same breath.
- **Pooled effluent.** Under air-tissue-interface operation they collect from the vascular
  compartment only, so cytokine origin cannot be assigned to a cell type. A model that predicts
  per-cell-type contributions cannot be checked against their numbers at that resolution.
- **Small n.** 3–7 devices per condition. They name low statistical power as a limitation. Model
  predictions should be stated as directions and orderings, not as effect sizes to match.

## 5. Hypotheses and mechanisms, in priority order

**H1. Signal without damage (run this first; no new code).**
Set `f_d = 0`, leave the `S_M2` pedestal at the level standing in for perfused TGF-β1, pin the seed,
run 20,000 MCS. Does a lesion still form?
- Lesion forms → the chip's no-LDH result is reproduced and damage is not the gate. Good.
- No lesion → the model predicts the chip **must** show cytotoxicity at any dose producing
  remodeling. That is falsifiable and worth stating, but it also means the architecture carries more
  weight than its calibration supports. Rethink before writing.

**H2. The damaged:healthy secretion ratio as a scanned parameter.**
Sweep 1:1 → 10:1 (currently 10:1, uncalibrated, first-pass). Locate the value at which lesion
formation becomes damage-dependent. That value is a prediction about where their dose-response turns
cytotoxic, and it converts an arbitrary constant into a result. Pairs with the existing
`citation_todo` item on the damaged:healthy ratio.

**H3. Stiffness threshold for self-sustaining remodeling.**
Implement the v2 latent/active TGF-β split with a local-ECM stiffness proxy, calibrated so healthy
maps to 0.44–7.5 kPa and fibrotic to ~17 kPa. Predict the stiffness at which fibroblast activation
persists after the pro-fibrotic input is withdrawn. Cheap for them to test (polymer concentration).
Cites Hall et al. (2024) as the modeling precedent for stretch/stiffness-gated latent release.

**H4. Reversibility and the point of no return.**
They state the platform supports studying "recovery following repeated or chronic exposures." Run
exposure-then-withdrawal at a range of durations; predict the exposure duration past which withdrawal
no longer resolves the lesion. Requires H3's feedback loop to exist. **The most publishable
prediction in this list**, because no in vitro study has the time resolution to find it by brute
force and the model's whole architecture is built to produce it.

**H5. Emit what they measure.**
Add an IL-6/IL-8-analogue readout on the pro-inflammatory channel. The model's observables and their
assay panel currently do not overlap at all: the model emits lumen area, cell counts and field stats;
they emit IL-6, IL-8, MUC5AC, TGF-β1, MMP-2, LDH, vWF. Fold into todo item 4 alongside the collagen,
thickness and myofibroblast-density readouts.

**H6. Report on their clock.**
Add days 3, 6, 12, 15 to the reporting schedule alongside the MCS checkpoints. Costs nothing, makes
every figure directly comparable.

**H7. Culture-configuration ablation (best near-term validation).**
They ran fibroblast monoculture, epithelial–fibroblast co-culture, and epithelial–fibroblast–
endothelial tri-culture. The model can run the first two: fibroblasts with no epithelial GF source,
and the full epithelium-plus-fibroblast configuration. Reproducing the **ordering** of αSMA⁺ and
cytokine response across configurations is a Tier 2 validation needing no units, no collagen, and no
new biology. Note the model has no endothelium, so tri-culture is out of reach.

**H8. Geometry — explicitly deprioritized.**
Do not rebuild as an annulus for this paper. Their stromal compartment is bulk hydrogel around a
vascular lumen, not a radially organized wall; the annulus would not improve the match. Keep the slab
and describe it as a local approximation of a wall segment.

## 6. Consequence for the paper

The `novelty_utility_review_2026-09-26.md` §4 recommendation was route 1 (reframe around epithelial
injury geometry, build only the focal arm) with Hypothesis and Theory as the fallback article type if
real sections never materialize.

**That recommendation is upgraded.** A paper structured as:

1. focal vs diffuse at matched total injury — the contribution only a model can make; plus
2. model predictions for the Bennet platform, validated retrospectively against their published
   mono-/co-culture configurations (H7) and extended forward to stiffness and reversibility
   (H3, H4);

is a stronger **Original Research** submission than (1) alone, and it fits the special issue better.
The topic is epithelial–immune crosstalk; IL-6 and IL-8 are epithelial-derived cytokine output, which
is squarely in scope, where subepithelial mechanics is not.

It also addresses the §3.7 gating problem a different way. The blocker was obtaining real
biomass-exposed small-airway sections for a measured Ripley's K curve. A collaboration with the
Cheung/Carlsten group is a more tractable ask than tissue-bank access, and even without one, their
published data supports H7 today.

**Still unresolved and still blocking:** the antioxidant sign problem (spec §6) if that experiment
stays in the paper, and the readouts (todo item 4), which now gate more targets than before.
