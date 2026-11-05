# CC3D v1 to-do — last reconciled 2026-09-26 (sections are dated individually; older bands/plateau figures predate the 2026-09-18 epithelial rescale)

Supersedes the 2026-08-11 version of this doc. Tracks
`model/cc3d/subepithelial_fibrosis_draft/`, not `Subepithelial_Fibrosis-02/` — work moved to
the `_draft` copy on 2026-08-08 per user instruction; `-02` was left untouched and is no longer
current. Checked against the actual `.xml`/`.py` on disk and the last three lab-notebook entries
(2026-08-07, 2026-08-08 main entry + 3 addenda) on 2026-08-09.

**2026-10-27 update (Gate B4), read this first — replicate baseline superseded:** after Gate B
(B1 epithelial repair path, B2 `FIBROBLAST_INITIAL_NUMBER` 80 → 11, B3 PSCAN replicates; commit
`2cdca3f`) the 20k n = 6 rebaseline (seeds 200–205) gives **−0.3% to −4.2% at MCS 20000 (mean
−2.5%, SD 1.4)**, replacing the 2026-09-26 −8.6% to −17.2% (mean −12.3%) measured at 80. Welch
t = 7.2, p < 0.001; the sets do not overlap. Tier 1 (every replicate narrows, sheet intact, no
overlap, no lumen collagen) passes; repair events 1–7 per run; final mesenchymal count 42–62 (vs
102–114). Finding, not a target: initial subepithelial occupancy is the dominant control on
narrowing on this geometry. The 2026-09-26 figures below are kept for provenance and are no longer
the comparison point. Details and criteria: `lab-notebook/2026/2026-10-27.md`; CSV and logs in
`results/cc3d/v1-gateB-rebaseline20k/`.

## Gate B′ — build the loops (added 2026-10-30; window Nov–Dec 2026)

Source: `docs/roadmap_revision_2026-10-29.md` §2–3. Build plan with phases, parameter list and
open decisions: `docs/gate_Bprime_plan_2026-10-30.md`. Everything below is switch-gated in
`parameters.py`, **all off by default until B′ closes**, and every off-run must reproduce `434bc94`
(the Gate B4 rebaseline, seeds 200–205) line-for-line in `replicates_summary.csv`.

**Switches:** `P_FIELD_ENABLED`, `P_GATES_REPAIR`, `P_DRIVES_PROLIFERATION`, `MMP_FIELD_ENABLED`,
`ECM_CELLS_ENABLED`. Rule: a steppable path behind an off switch makes **no `random` draw and no
field write**, so the RNG sequence and the fields are untouched.

**Pre-registered criteria (A18; written before any code):**

1. *Regression.* All five switches off: the six B4 replicates reproduce exactly (every numeric
   column of `results/cc3d/v1-gateB-rebaseline20k/replicates_summary.csv`, tolerance 0). Checked
   by a diff script, not by eye.
2. *Clean single-switch runs.* Each switch on alone (`P` alone, then `P` + each consumer, MMP alone,
   ECM alone), 3 pinned seeds, 20k MCS: run completes; Tier 1 holds (sheet intact, no
   fragmentation, zero mesenchymal overlap, no `C` and no ECM cell in the lumen); `P` and `MMP`
   reach a quasi-steady band mean with no blow-up; the tissue damaged fraction tracks the ODE's
   `f_d` (mean |f_tissue − f_d| below one cell's worth, 1/25).
3. *Direction checks, one per loop (ordinal, per A18):* `P_GATES_REPAIR` lengthens the mean
   damaged-cell lifetime vs off; `P_DRIVES_PROLIFERATION` raises fibroblast divisions vs off;
   `MMP_FIELD_ENABLED` lowers the final ECM-cell count vs ECM-only; `ECM_CELLS_ENABLED` yields a
   nonzero ECM pixel fraction confined to the subepithelial band. Lumen change is **reported, not
   pre-specified**, for every condition.
4. *Rebaseline.* All switches on, n = 6, seeds 200–205, 20k MCS: Tier 1 in every replicate;
   report lumen % change, ECM-cell area fraction, ECM count, myofibroblast count, divisions, repair
   events, mean damaged lifetime, `P` band mean, `MMP` band mean, H5 `P`-analogue on the chip clock.
   This replaces B4 as the comparison point for Gate D. Destabilised = any replicate with a sheet
   breach, an ECM cell above the sheet, or a diverging field; the offending switch is then run off
   in Gate D (the ablation design allows it).

**Build order (one phase per session or two):** 0 switches + regression script → 1 `P` field,
sources, pedestal, readouts → 2 `P` consumers (repair gating, mitosis gate) → 3 MMP field, TIMP,
`C` decay term → 4 ECM cell type, budget, adjacent placement, removal, readouts → 5 regression,
single-switch runs, rebaseline → 6 docs and methods paragraph. Phase checklist in the plan doc.

- [x] Phase 0 — switches in `parameters.py`, `compare_replicates.py` diff script, criteria above
      frozen in the lab notebook. *Done 2026-10-30:* five switches (all `False`) with an import-time
      check that a consumer is never on without its field; one lower-cased column per switch appended
      to `replicates_summary.csv`; `model/cc3d/tools/compare_replicates.py` matches rows on
      `iter_count`, compares every reference column at tolerance 0, lists extra candidate columns
      without failing. Verified: B4 CSV against itself passes; a one-digit edit, a missing row fail;
      extra switch columns pass.
- [x] Phase 1 — `P` field (XML field; Python secretion gated by live `WS`; `S_M1` pedestal;
      `local_P` in `read_local_fields`; band mean + `P`-analogue in the summary CSV).
      *Done 2026-10-31:* `P` declared in the XML (decay 6.93e-4 /MCS from the ODE's `m7`; D built at
      4.44 from λ = 80 px, run at `G`'s 0.10 on 11-01, pinned 11-02 at λ = 50 µm = 40 px, D = 1.11, the
      centre of `P`'s own 25–120 µm range, independently of `G`; see the plan's status note); epithelial source `P_H · WS` (healthy) / `2 P_H · WS` (damaged,
      `e6/e5` live) per cell per MCS split over the wall-side Medium neighbours; `S_M1` pedestal over
      the subepithelial band from live `WS · Hill(A) · (M1+M1R)`; `local_P` per cell; CSV columns
      `mean_P_band`, `lumen_P_mean`, `P_analogue_H5`. 3k seed-200 smoke runs: switches-off twin
      bit-identical to HEAD (27 CSV columns, 258 log lines); `P`-on twin identical on every B4
      column; band mean 0.84 at 3k (87 % of steady state, projects to ~0.97 vs design 1.0).
      **Finding:** with λ = 80 px the lumen is not `P`-free (lumen mean 0.98 > band mean 0.84;
      the sheet is no barrier) — accepted as a readout 2026-11-01. Literature λ-range pass done 11-01
      (`G` ≤ 70 µm, `P` 25–120 µm; Gate D scan axis in the plan and calibration table).
- [x] Phase 2 — `P` consumers: per-cell `p_repair / (1 + k_P P_local)`; mitosis gate on
      `G + k_prolif P`. *Done 2026-11-02:* `K_P` = 1.0 and `K_PROLIF` = 0.5 × threshold in
      `parameters.py`; `damaged_since` stamp; CSV columns `mean_damaged_lifetime_mcs`,
      `mean_damaged_age_final_mcs`, `mean_abs_fd_gap`, and two deterministic companions,
      `expected_repairs` / `expected_damaged_lifetime_mcs` (sum of per-cell gated probabilities) and
      `p_tipped_gate_frac` (fibroblast cell-MCS where only `P` opened the mitosis gate). Seed-200
      twins: switches off reproduces HEAD exactly; consumer 1 doubles the expected damaged lifetime
      (12,074 → 24,508 MCS at 3k) while realized repairs are too rare to differ at one seed (1 per 10k
      in both runs); consumer 2 tips the gate in only 0.3 % of fibroblast cell-MCS because band `G`
      (≥ 0.225 from MCS 1400, 1.5–1.7 later) already holds it open, so divisions do not rise (33 vs
      35 at 10k). `f_d` tracking gap 0.007–0.009 (criterion 2 asks < 0.04). Direction checks in
      criterion 3 therefore read the expected-rate columns, not realized counts.
- [x] Phase 3 — MMP field; epithelial secretion `mmp_0 (1 + k_mmp P_local)`; TIMP subtraction at
      myofibroblast COM; `C` decay `0.0005 + k_C,mmp MMP` (per-pixel, optional).
      *Done 2026-11-02:* `MMP` declared in the XML (λ = 10 µm = 8 px, D = 0.64, decay 0.01 /MCS;
      literals cross-checked at `start()` like `P`'s); epithelial source `MMP_0 (1 + K_MMP · P_local)`
      per cell per MCS, every MCS, healthy and damaged alike, into the `P` source pixels
      (`MMP_0` = 3.08 derived like `P_H` for a band mean of 1, `K_MMP` = 1); TIMP `0.1 · MMP_0` per
      myofibroblast per MCS at its COM, clamped at 0; `C` MMP-decay term `K_C_MMP · MMP · C` per band
      pixel (`K_C_MMP` = 0.001, `C_MMP_DECAY_ENABLED`, period parameter); `local_MMP`; CSV columns
      `mean_MMP_band`, `lumen_MMP_mean`, `mean_MMP_at_myof_com`, `mean_MMP_under_damaged`,
      `mean_MMP_under_healthy`. Seed-200 3k twins: switches off reproduces the reference exactly
      (27 columns, 258 log lines); MMP on with the `C` term off is identical to off on every B4
      column; MMP on + `C` term removes 69 % of band `C` (0.63 → 0.19), Tier 1 clean. **Field shape
      (3k):** band mean 0.68, under the sheet 6.2–6.3, max ≈ 11, lumen 0.74 — peaked under the sheet
      as λ = 8 px implies; `MMP_thr` (Phase 4) is expressed against the band mean. **Two direction
      checks do not read as written:** MMP under damaged cells (6.22) is not above healthy (6.34),
      because at λ_P = 40 px a damaged cell's own 2× `P` barely raises `P_local` (band-scale contrast,
      11-01 finding), and the field at myofibroblast COMs (0.98) is above the band mean because
      myofibroblasts sit near the sheet; the TIMP sink shows as a local dip against neighbours
      instead (per-cell tables in the log). Cost (in-process timers, per 3k MCS): MMP source loop
      45 s, TIMP 0.2 s, `C` term 57 s at period 1, so the `C` term runs every 10 MCS with the rate
      × 10 (`C_MMP_DECAY_PERIOD_MCS` = 10).
- [x] **Next session, before Phase 4 (set 2026-11-04):** scratch count of myofibroblasts at the new
      base. Copy of the project with the myofibroblast `G` `<Secretion>` literal 0.1 → 0.001 (XML
      only; committed base untouched, all B′ switches off), seed 200, 20k MCS (≈ 1 h; myofibroblasts
      only appear after ≈ 2,500 MCS). Read: n_MyoF at 5k / 10k / 20k, band `G` against the 0.225 and
      0.45 gates, divisions, lumen. Optional second copy with the activation rate at the literature
      value once the `G` level that means saturating TGF-β1 is chosen (plan §6 item 7 ii). Then
      decide: move the §6 item 7 base-model change ahead of Phase 4 (new criterion-1 reference
      first, dated amendment to the pre-registered schedule), or keep it in Phase 5 and lower
      `ECM_BUDGET_INCREMENT` (at B4's 42–62 myofibroblasts it deposits ≈ 5× the band's free space).
      *Done 2026-11-05 (scratch copies, seed 200, committed base untouched; lab notebook 11-05,
      logs in `results/cc3d/scratch-newbase-seed200-20k/`):* at `G` = 0.001 the model makes
      13 / 84 / 350 myofibroblasts at 5k / 10k / 20k against 26 / 47 / 59 on the current base:
      fewer until ≈ 7k, then about six times more and still rising. Band `G` stays 0.19–0.31
      (never reaches 0.45), so the fibroblast pool is never used up and keeps dividing (393
      divisions against 28; the mitosis rule has no contact inhibition, and every fibroblast reads
      local `G` 0.27–0.48 from its own secretion, so the 0.225 gate is always open, on the current
      base too). Band 96.5 % cells by 20k, lumen −8.6 %, Tier 1 clean. With the activation rate
      also at 7.2e-4 (`G_sat` = 1.0 assumed): 629 fibroblasts, lumen gone from MCS 7,400. Budget on
      the current base: 522,200–835,300 myofibroblast-MCS (B4, n = 6), 3.6–5.8× the free band at
      0.08 px/MCS. **Recommendation, awaiting Marcella:** keep item 7 in Phase 5 and lower
      `ECM_BUDGET_INCREMENT` (first pass ≈ 0.01 px/MCS); see the two items below.
- [x] **Marcella, before Phase 4 (from the 11-05 scratch run):** confirm that plan §6 item 7 stays
      in Phase 5, and set the Phase 4 value of `ECM_BUDGET_INCREMENT` (0.014–0.022 px/MCS nominally
      fills the ≈ 11,600 px free band by 20k at B4's myofibroblast counts; recommended first pass
      ≈ 0.01, a Gate D scan parameter). *Decided 2026-11-05 (Marcella; plan §6 item 10):* item 7
      stays in Phase 5, and `ECM_BUDGET_INCREMENT` = 0.01 px/MCS for Phase 4.
- [ ] **Marcella, before Phase 5 (from the 11-05 scratch run):** plan §6 item 7 as written removes
      the model's only brake on fibroblast proliferation (total conversion by ≈ 6k). Choose a
      proliferation limit to go with it (candidates, none built: contact inhibition on the mitosis
      clock; rethinking the 0.225 / 0.45 gates against the 0.27–0.48 a fibroblast reads from its
      own secretion; lower fibroblast `G` secretion), set `G_sat` for the activation-rate fix, and
      note that at 0.001 a myofibroblast secretes less `G` per pixel than a fibroblast (0.005).
- [ ] Phase 4 — `ECM` cell type (TypeId 6; contact energies, λ, fluctuation amplitude rescaled to
      this model's J scale, not copied); per-myofibroblast budget; adjacent placement biased toward
      the sheet; `delete_cell` when `MMP_local ≥ MMP_thr`; `MYOF_TARGET_VOLUME_GROWTH_FACTOR`
      reduced under the switch; ECM pixel fraction, count and centroid dump for Ripley's K.
      *Seeding decided 2026-11-04 (plan §6 item 1):* seed on free Medium pixels only (≤ 2 × 2), then
      ramp `targetVolume` to 36 at `ECM_GROWTH_PX_PER_MCS` (first pass 0.5), not 36 at birth. First
      step of the phase: a 500-MCS scratch comparison of the ramped and unramped forms next to the
      sheet. *Removal decided 2026-11-04 (plan §6 item 8):* rate-based, each ECM cell removed with
      probability `K_ECM_MMP · MMP_local` per MCS (placeholder 1e-4, lifetime ≈ 3,300 MCS at MMP 3),
      replacing the `MMP_local ≥ MMP_thr` threshold above: on a field that spans three decades a
      threshold deletes all matrix within ≈ 17 px of the sheet and none deeper. Gate D scans
      `K_ECM_MMP`, not `MMP_thr`. *Myofibroblast volume decided 2026-11-04 (plan §6 item 3):*
      `MYOF_TARGET_VOLUME_GROWTH_FACTOR_WITH_ECM` = 0 (matrix volume is carried by ECM cells only;
      λ_volume stiffening stays), with a Gate D control arm, ECM off and swelling factor 0, to
      separate the matrix effect from the lost swelling. *`C` field decided 2026-11-05 (plan §6
      item 9):* no `C` under ECM cells, nothing writes it and nothing reads it (sources: the XML
      `SecretionOnContact` and the epithelial basal secretion; consumers: myofibroblast and
      fibroblast λ_volume stiffening, the `C` MMP-decay term). That closes "the `C` term on/off".
      Proposed with it, to confirm: no replacement stiffening, and no epithelial matrix output
      under the switch. Build note: zero the XML source by steering it at `start()` (check in a
      scratch project that 4.9.0 allows it; fallback, leave the field unread), and fix the
      `ECM_CELLS_ENABLED` comment in `parameters.py` ("C kept for stiffness only"). Still open
      before the build: §6 item 4 and the two confirmations above. *Budget decided 2026-11-05
      (plan §6 item 10):* `ECM_BUDGET_INCREMENT` = 0.01 px/MCS (one 36-px ECM cell per 3,600 MCS
      of Medium contact, nominally 45–72 % of the free band over 20k at B4's counts; was 0.08,
      3.6–5.8×). Watch in the smoke run: at this rate the `K_ECM_MMP` placeholder (1e-4) leaves
      about one ECM cell per sheet-adjacent myofibroblast at steady state, not seven.
- [ ] Phase 5 — **first** the pre-registered base-model change (plan §6 item 7, decided 2026-11-02):
      `G` secretion literals into `parameters.py`, myofibroblast `G` rate 0.1 → 0.001, activation rate
      to the literature value, 3k seed-200 smoke, then a NEW criterion-1 reference (switches-off
      n = 6 PSCAN at the new base). Then regression (criterion 1 against that reference), single-switch
      runs (2, 3), rebaseline PSCAN (4), `-f` lattice snapshots on for the rebaseline so Gate D has
      point patterns.
- [ ] Phase 6 — A13/A14/A17 implementation notes, calibration table statuses, methods paragraph
      drafted for Gate E. Includes A14's wording for the 2026-11-05 decision (no `C` field under
      ECM cells; matrix measured as `C` band mean without ECM cells and as ECM pixel fraction with
      them, so cross-condition matrix comparisons in Gate D are ordinal).

**Parameters B′ introduces** (all in `docs/calibration_table.md`, "to set" until pinned): `p_h`,
`P` diffusion and decay, `k_M1` (inherited from the ODE's `m6`), `k_P`, `k_prolif`, `mmp_0`,
`k_mmp`, MMP diffusion and decay, TIMP rate, `MMP_thr`, `k_C,mmp`, ECM quantum, ECM cell size and
energies at this scale. Plus the known-wrong activation rate (0.02 per MCS of signal). Which of
these block the rebaseline, and which are scanned, is tabulated in the plan doc §5.

**2026-08-14 reconciliation note:** three working sessions (2026-08-12 `7858a83`, 2026-08-13
`d718a23`, 2026-08-14 lumen-diagnostic fix + full-run result) landed after the 2026-08-11 version
of this doc and are folded in below — see the updated **PRIORITY 0** status, the reconciled
**Links (FPP)** subsection, and the new **Next session priorities** section up front. Full detail
for all three sessions is in `lab-notebook/2026/2026-08-14.md`'s "Context carried in from prior
sessions" note and its own Did/Results sections.

## Next session priorities (added 2026-08-14; updated 2026-09-03/04/06/18)

**2026-09-18 update — epithelial cell-height rescale applied (48 → 64 px, 8 × 8), read before comparing
any narrowing number.** Details in `lab-notebook/2026/2026-09-18.md`. Band geometry is no longer the y-bands
quoted elsewhere in this doc (written for the 6-row epithelium): the epithelial band is now *derived* from
`EPITHELIAL_CELL_HEIGHT` in `parameters.py` — epithelium y = 72–79, lumen fixed at 80–99, subepithelial
4–71 (68 rows). **All narrowing figures in this doc (2.5–5.5%, "plateau by MCS 300–400", the −10% 300-fibroblast
tests) predate this change and are not comparable with post-change runs**: the rescaled sheet narrows more
(about −8.6% vs −3.3% at MCS 3000 in 4 matched seeds each; cause not isolated — likely the softer rescaled
lambdas/J, not yet separated from the taller cell). Rebaseline before reading anything into step 3b/4/5.
Full 20,000-MCS confirmation done 2026-09-20 (`results/cc3d/v1-epi64-derivedband-20k-run.log`): clean, −14.7%
lumen narrowing at MCS 20000 (−8% by MCS 1000, still drifting after MCS 10000), one unseeded run.
Python `random` is now seeded from the XML `<RandomSeed>` (done 2026-09-20, `b7530f6`): a pinned seed
reproduces a run exactly, and the log banner says whether a run was pinned. **Residual isolated 2026-09-21**
(3 configs x 3 pinned seeds): the taller cell alone (correctly seeded) does not move narrowing (config B
tracked config A); the rescaled `LAMBDA_VOLUME_EPITHELIAL`/`LAMBDA_SURFACE_EPITHELIAL`/epithelial-J values do
(config C narrowed more on every matched seed) — a real, expected consequence of a softer, lower-adhesion
sheet, not an artifact. **Containment check fixed 2026-09-22**: `compute_epithelial_column_bounds()`
replaces the fixed-band comparison with genuine pixel-level overlap against the sheet's current
footprint; verified directly against the isolation run's config C seed 13 (identical trace) — old
check read 0/6/8 at MCS 0/1000/3000 with sheet integrity clean throughout, new check reads 0/0/0 on
the same run, confirming the old counts were the vacated-space false positive. **Confirmed over full
20,000-MCS runs 2026-09-26** (7 runs, all clean, overlap 0 at MCS 0/1000/20000). **Item 3b replicate
spread, new geometry: −8.6% to −17.2% at MCS 20000 (mean −12.3%, SD 3.0, n = 6 pinned), plus two
unpinned runs at −10.5% and −14.7%.** No plateau on this geometry: most runs keep drifting through
MCS 20000, and none reaches the ~22% Higham target (widest −17.2%). Details in
`lab-notebook/2026/2026-09-18.md`; logs in `results/cc3d/v1-epi64-reps20k/`.

**2026-09-03/04 update, read this first:** a diagnostic session (2026-09-03,
`lab-notebook/2026/2026-09-03.md`) traced the PRIORITY 0 displacement plateau to a population gap
— the subepithelial compartment never gets crowded enough to actually push the sheet — and a
literature session the same evening (2026-09-04, `lab-notebook/2026/2026-09-04.md`) cited both
outstanding A7 calibration anchors and, in the course of that, surfaced a timescale finding that
reframes the whole plateau discussion (see item 1). **The user then paused item 2 deliberately:
before building fibroblast mitosis (a cellular-crowding fix), they want to think through whether
displacement-via-cell-crowding is biologically motivated at all, versus accepting that v1 won't
show much displacement until v2 introduces a volume-occupying ECM representation (PRIORITY 0 plan
step 5, currently the "last resort" fallback).** This is exactly the tension A14 already named
when it chose ECM-as-field over ECM-as-cell-type for v1: real airway-wall thickening in fibrosis
is predominantly matrix (collagen), not cellular hyperplasia, so a fix that displaces the sheet by
adding *cells* (mitosis, higher `R_fib`) may be pushing the right readout for the wrong modeled
reason — solving 3a's diagnosed gap with a mechanism that isn't what actually thickens fibrotic
tissue in vivo. Do not implement mitosis next session without first resolving this — see the new
**item 0** below.

0. **[DECIDED 2026-09-06] Both.** Fibroblast mitosis is a real fibroblast characteristic and
   belongs in the model on its own biological merits — but it is explicitly **not** the
   answer to the displacement plateau. Two consequences, not a single either/or:
   - **Fibroblast mitosis: built** (`FibroblastMitosisSteppable`,
     `FibrosisModelSteppable.update_fibroblast_mitosis`, 2026-09-06). GF-gated on *where/whether*
     a fibroblast divides (Molina et al. 2025's localized-clonal-expansion finding), held at the
     literature cell-cycle rate (`p.FIBROBLAST_CYCLE_MCS` ≈1730 MCS, from the cited 25-34h
     doubling time — Mio1992/Holz2004 found **no** disease-driven speedup of the cycle itself, so
     the rate is not tunable-up as a displacement lever without contradicting its own citations).
     Deliberately kept at this reasonable/low level, not calibrated against the Higham ~22% target.
   - **v2's volume-occupying ECM cell type is prioritized**, not left as the "last resort" PRIORITY
     0 plan step 5 fallback — that mechanism (matter that actually occupies lattice space) is
     closer to what really thickens fibrotic tissue than cell-mass crowding is, and the 2026-09-03
     diagnosis (volume-frustration checks: myofibroblasts never contest the sheet even at ~35-38%
     local occupancy) already suggests cell-crowding alone won't close the gap to 22% regardless of
     how much mitosis adds to the population. See `docs/ecm_field_vs_celltype_assessment.md` for
     the reference implementation this can build from.
   Record of the reasoning: real airway-wall thickening in fibrosis is predominantly matrix
   (collagen), not cellular hyperplasia (A14's own field-vs-cell-type reasoning for ECM already
   makes this point) — so mitosis is scoped as *a real process worth representing*, not as *the
   fix* for the displacement question, and the fix for that question moves to v2.

1. **Timescale and physical-scale calibration — µm/px now cited and resolved; s/MCS still
   open, and its resolution changes how to read the plateau.** 2026-09-04 literature session
   (`lab-notebook/2026/2026-09-04.md`, `docs/validation_targets.md` §7, `docs/citation_todo.md`):
   - **µm/px: 1.25 µm/px** (was the uncited 1.5625 from 2026-08-14). `EPITHELIAL_CELL_WIDTH=8px`
     against a cited 10 µm airway epithelial cell width (Devalia et al. 1990, 10.2±1.0 µm human
     bronchial; Mariassy & Plopper 1984, 9.3 µm Clara/secretory cell; Plopper 2020 confirms small
     airway = simple cuboidal, not the large-airway columnar epithelium the old 10-15 µm range
     described). Domain is now 250×125 µm. **Reinterpretation, not a rescale** — pixel count per
     cell is unchanged, so no `lambdaVolume`/adhesion-energy rescaling follows (Module 8.2 rule
     doesn't fire).
   - **s/MCS: measured, pending one anchor pick.** The isolated-fibroblast scratch run (2026-09-04
     continued session, `lab-notebook/2026/2026-09-04.md`) gave **mean |ΔCOM| = 0.1484 px/MCS**
     (5000-MCS run, single `Fibroblast`, real model's own Contact/Chemotaxis/diffusion physics,
     max excursion 12.65px so the `NoFlux` boundary never biased it). That closes
     `s/MCS = v × 1.25 ÷ v_lit` to two candidate numbers depending which `Tisler2020` condition
     anchors it: **109.5 s/MCS** (normal/normal, 6.1 µm/h — clears the ~120s ceiling by only ~9%)
     or **62.4 s/MCS** (IPF/IPF, 10.7 µm/h — comfortable margin). **Not yet picked** — this
     model's fibroblasts are undergoing wood-smoke/PM2.5-driven activation, not sitting at
     baseline, which leans toward IPF/IPF as more representative, but the exposure isn't the same
     etiology `Tisler2020` used, so the lean is weak, not decisive. Next session should close this.
   - **Consequence for the 2026-09-03 plateau diagnosis — read this before scoping item 0/2:**
     with a measured 62.4-109.5 s/MCS (narrower than the earlier 27-120 s/MCS placeholder range),
     a 20,000-MCS run is **14.4-25.3 days of biological time**, not the 24 weeks `Li2024` and other
     exposure sources imply. "Displacement plateaus by MCS ~300-400" (2026-08-14) now has a
     measured timestamp too: **5.2-12.2 hours** of biological time depending on the anchor — well
     under a day either way. Strong reason to read the plateau as a saturating mechanism rather
     than a slow-progression one, and confirmation the *current run length* is far short of the
     exposure timescale A11 scopes, independent of whatever fixes the population gap. Whatever
     item 0 decides, a much longer run (in MCS) will be needed before any displacement number —
     cell-crowding-driven or ECM-driven — is a fair comparison to the ~22% Higham target.
   - **Still open:** verify the `Tisler2020` migration figures against the source (currently read
     off Fig. 3B, marked *(verify)*, not tabulated); find a second pixel↔µm anchor independent of
     epithelial cell width (fibroblast spread area doesn't work — Asano et al. 2017 report 2D
     substrate footprint, 20-40× larger than `TARGET_VOLUME_FIB`'s tissue cross-section); decide
     the epithelial cell height (`TARGET_VOLUME_EPITHELIAL=48px` at 8px width is 7.5µm tall vs. a
     measured 9.6µm Clara-cell height — 64px/8×8 would match but *would* need the `lambdaVolume`
     rescale check, unlike the width change); find a small-airway-specific *human* epithelial width
     source (not found in the 2026-09-04 pass); find a wood-smoke/biomass-specific fibroblast
     figure (everything cited so far is IPF/bleomycin/emphysema, same exposure-specificity gap
     already logged for A19). Full list in `docs/citation_todo.md`.
2. [x] **Fibroblast mitosis gated on growth factor — built 2026-09-06.**
   `FibroblastMitosisSteppable` + `FibrosisModelSteppable.update_fibroblast_mitosis`,
   `Subepithelial_FibrosisSteppables.py`. Standard CC3D volume-doubling mitosis
   (`MitosisSteppableBase`): a fibroblast's `mitosis_clock` accumulates only while local
   `G >= p.FIBROBLAST_MITOSIS_G_THRESHOLD` (paused, not reset, below it), and once it reaches
   `p.FIBROBLAST_CYCLE_MCS` (~1730 MCS, from the cited 25-34h doubling time via `p.S_PER_MCS`)
   the cell grows to 2x targetVolume and splits. **Decided (item 0, top of this doc): scoped
   as biological completeness, not a displacement fix** — gates *where/whether* a fibroblast
   divides on local `G` (Molina et al. 2025's localized-clonal-expansion finding), holds the
   cycle at the literature rate rather than tuning it up (in-culture doubling time is not
   reduced by fibrotic disease per Mio1992, and is *lengthened* in emphysema per Holz2004 — so
   speeding up the cycle to force displacement would contradict the citation motivating it).
   **Confirmed 2026-09-06 with a division-count print + full 20,000-MCS run against the
   committed project** (`results/cc3d/v1-mitosis-confirm20k-run.log`): clean, no traceback, no
   assertion failures, sheet integrity `fragmented=0 isolated=0` at MCS 0/1000/20000, 0
   mesenchymal cells in the epithelial band at every checkpoint, runtime 39m58s (negligible
   overhead vs. pre-mitosis full runs). **3 total divisions over the full run** (MCS ~8000-9000,
   none after) — a shorter 2500-MCS scratch check with the same print showed 7 divisions by MCS
   ~1856, confirming the mechanism fires as designed; the full run's low total is an emergent
   consequence of differentiation (~50 MCS to complete once G>=0.45) being much faster than
   mitosis (~1730 MCS at G>=0.225), so a fibroblast in a high-G region almost always
   differentiates before it could divide, and by MCS ~9000 domain-wide G (mean 2.7 by MCS 20000)
   is high enough everywhere that new recruits differentiate immediately too — exactly the
   "reasonable/low level, not a lever" behavior decided in item 0, obtained without hand-tuning.
   Lumen narrowing at MCS 20000: -4.6%, within the same 2-7% stochastic range seen without
   mitosis — confirms it does not meaningfully move the displacement plateau, as intended.
   Parameters moved to `parameters.py` alongside this change (see item 3 below).

3. [x] **Parameters-file hygiene pass — done 2026-09-06.** All CPM/tissue-layer constants moved
   from bare module-level values in `Subepithelial_FibrosisSteppables.py` into
   `model/cc3d/subepithelial_fibrosis_draft/Simulation/parameters.py`, split into
   Biological/Model/Conversion sections per Module 8.2 (Sluka), each with units and a citation or
   an explicit "arbitrary/uncalibrated" note (A19's own convention when no anchor exists).
   `UM_PER_PX` and `S_PER_MCS` are now *computed* from their Biological/Model inputs rather than
   hardcoded, so the two can't drift out of sync silently. `TISSUE_SIGNAL_MODEL` (the Antimony/SBML
   sub-model) deliberately stays in the steppables file — it's a self-contained model with its own
   densely-commented internal constants, not simple CPM scalars. A basic-units docstring (1px/1MCS)
   was added at the top of `Subepithelial_FibrosisSteppables.py` per Module 8.2's guidance. Not done
   this pass: the PSCAN/`iter_count` replicate-run setup (`lab-notebook/2026/2026-09-04.md`'s
   "Next steps" still lists it) — **closed 2026-10-27 (Gate B3)**: `Simulation/ParameterScanSpecs.json`
   with a dummy `iter_count`, a per-replicate pinned seed (`REPLICATE_SEED_BASE + iter_count`, set on
   CC3D's generator and Python's `random`), and one combined `replicates_summary.csv` per scan.

4. [ ] **Choose, add, and test readouts against the chosen validation targets** (added
   2026-09-26). Today the model reports lumen area, sheet position, occupancy and cell counts;
   it does **not** compute the endpoints `docs/validation_targets.md` is written around:
   collagen area fraction (§3.1, the A12 primary endpoint), subepithelial thickness (§3.2),
   myofibroblast density (§3.3), or fibroblast number over time (§3.4). The spatial statistic
   (§3.6) exists as post-processing (`model/analysis/spatial_stats.py`) but is not wired to model
   output. Three steps, in order:
   - **Choose.** Decide which targets are in scope for v1; the §5 minimal validation set is the
     starting list. Write the pass/fail criterion for each *before* running (Tier 2 direction,
     ordering or ratio, per A18), not after seeing the numbers.
   - **Add.** Implement each chosen readout (in `DiagnosticsSteppable` or an output file), with
     its denominator fixed: §6 still asks whether Islam et al. (2023) report collagen area
     fraction over the whole domain or a tissue subregion, and which `d` the K curves use.
   - **Test.** Run against the targets on the **post-2026-09-18 geometry** (older numbers are not
     comparable). Several targets depend on unbuilt pieces: the focal damage arm (headline
     experiment), an `R_fib` sweep (Hoshino correlation), and scenario/`S_M2` scans (PSCAN).
5. [x] **Re-anchor `FIBROBLAST_INITIAL_NUMBER` (currently 80) to the Zajicek et al. (1992)
   anchor** (decided 2026-09-26). **Done 2026-10-27 (Gate B2): 80 → 11, ratio reading; recorded in
   `parameters.py` and A7's anchor notes; rebaselined in Gate B4 (`lab-notebook/2026/2026-10-27.md`).** The 80 came from a deliberate 2026-08-11 displacement
   experiment, not a calibration (it was 10 before that), and gives about 0.3 fibroblasts per
   epithelial cell at `t = 0` against a literature ratio of about 0.45 (2.2 epithelial : 1
   fibroblast). Decide the target in `parameters.py` with the citation, choosing between two
   readings of the same source: **match the ratio** (25 epithelial cells → ~11 fibroblasts), or
   **match the linear density** (6.6 fibroblasts per 100 µm × the 250 µm domain ≈ 16–17), which
   differs because the model's 10 µm epithelial cell is wider than the ~6.8 µm the source implies.
   Verify the source first (abstract-level, hamster, SE not SD). Expect the change to shift
   crowding, recruitment and early narrowing, so **rebaseline the replicates afterwards**: the
   −12.3% mean at 20,000 MCS was measured with 80. **Rebaselined 2026-10-27 at 11: mean −2.5%
   (−0.3% to −4.2%, n = 6) — see the 2026-10-27 update at the top.**

**2026-08-09 reconciliation note (committed 2026-08-11):** the Priority 2 section below (and
the code it describes) was actually finished 2026-08-09, in the same working session as
everything else on this page, but was left uncommitted and this doc was never updated to
match — it still said "not started." Reconciled: the code is unchanged, this doc is corrected
to describe it accurately.

**2026-08-11: priorities reshuffled.** Epithelial layer restructuring (below) now leads,
ahead of the Priority 1/2 work carried from 2026-08-09 — see **PRIORITY 0**. Two problems
motivated the reorder: the y-band ordering was nonintuitive to read in the Player (see PRIORITY 0
for why), and Priority 1's own item 5 ("does thickening measurably displace the sheet") couldn't
give a legible answer against a 40-row lumen where even real displacement reads as noise.

Design authority, in order of precedence: `docs/model_assumptions_for_slides.md` (A1–A18) →
`docs/model_spec_v1_v2.md` → `docs/ode_tissue_coupling_options.md` → this doc.

---

## PRIORITY 0 — Epithelial layer reorder (2026-08-11)

**Status: geometry reorder implemented, smoke-tested, and confirmed clean over a full
20,000-MCS run (2026-08-11). The apical/basal/lateral question is reviewed and deferred (below).
The displacement plan's steps 1-3 are now done (2026-08-12/13/14, see below) — `targetVolume`
coupling landed, epithelial FPP cohesion links added, the lumen-collagen diagnostic bug is fixed
and confirmed clean over a full run. Result: real displacement now exists but is small and
plateaus early (2.5-5.5% narrowing vs. the ~22% Higham target, most of it within the first ~400
MCS of a 20,000-MCS run). **2026-09-03: the plateau's cause is now diagnosed (plan step 3a,
below) — the subepithelial compartment never gets crowded enough to actually push on the sheet
(myofibroblasts reach ~97-100% of targetVolume without contesting it; the epithelium's own
volume/targetVolume ratio stays at ~1.000 throughout). Next step is step 4: raise population at
the interface via `R_fib` and/or fibroblast mitosis, not further per-cell signal tuning.**

**2026-08-12/13/14 update, folded in from `lab-notebook/2026/2026-08-14.md`:**
- `7858a83` (2026-08-12): plan step 3 landed — myofibroblast `targetVolume` now grows with
  local `c_norm(C)`, not just `lambdaVolume`. `K_C` recalibrated 160 → 20 against real run
  numbers (the old value assumed a secretion rate never actually committed).
- `d718a23` (2026-08-13): epithelial `FocalPointPlasticity` cohesion links added between
  neighboring epithelial cells, after the `targetVolume` coupling run surfaced a flickering
  sheet-breach risk. **This reopens the Links (FPP) question the subsection below had closed as
  "not needed for v1" — see the reconciliation note there.**
- 2026-08-14: found and fixed a diagnostic bug in the lumen-collagen check (`field C lumen max`
  used a fixed `y >= LUMEN_MIN_Y` band instead of the same flood-fill `compute_lumen_area`
  already used, so it scored collagen under displaced-but-intact epithelium as a false-positive
  "leak" — climbed to ~89 in the pre-fix `v1-fpp-stability20k` run). Fixed in
  `DiagnosticsSteppable` (`flood_fill_lumen_pixels()` now shared by both readouts). Full
  20,000-MCS confirmation under the fix: **0 real leakage at all 201 checkpoints**, but
  displacement itself is only 2.5% narrowing (vs. 5.5% in the pre-fix run under identical
  parameters — run-to-run stochastic variance, not a parameter difference) and **plateaus by
  MCS ~300-400**, barely moving for the remaining ~19,600 MCS. Both runs are well short of the
  ~22% Higham target. See `lab-notebook/2026/2026-08-14.md` Results for full numbers.
- Also 2026-08-14: wrote `docs/ecm_field_vs_celltype_assessment.md`, a basic comparison against
  Chandrasegaran, Sluka & Shanley (2025)'s cell-type-based ECM, prompted by the diagnostic fix.
  Recommendation: stay on the field-based representation for now — the plateau looks like a
  calibration question, not evidence the representation itself is structurally incapable — but
  flagged as closer to the "if calibration can't get there" fallback condition than it looked
  before this run.

### Why

Two separate problems, both raised 2026-08-11:

1. **Layer order was nonintuitive in the Player.** CC3D renders y increasing upward. The
   pre-2026-08-11 band order (low-to-high y) was Lumen (0–39) → Epithelium (40–45) →
   Subepithelial (46–95) → OuterBoundary (96–99) — which puts the frozen wall at the *top* of
   the view and the airway lumen at the *bottom*, backwards from how everyone reads the
   anatomy off the slides (lumen at top, wall at the outside/bottom).
2. **Not enough displacement headroom to see the effect the model is built to show.** Priority
   1 item 5 ("does subepithelial thickening measurably displace the epithelial sheet") was
   never actually checked (see Priority 1 below) partly because a 40-row lumen buries a small
   real displacement in noise — even a few pixels of genuine inward movement barely registers
   against 40 rows of lumen, so the readout wouldn't be legible even once wired up.

### Decision and implementation

Layer order flipped (low-to-high y): **OuterBoundary (0–3) → Subepithelial (4–73) → Epithelium
(74–79) → Lumen/Medium (80–99)** — "airway space above the epithelium above the subepithelial
space above the frozen outer boundary," reading top-to-bottom in the Player as stated. The lumen
band is halved (40 rows → 20, y 80–99); the 20 rows freed up were **not** left as unclaimed
Medium (which would have just re-inflated the lumen and undone the halving) — they went to the
subepithelial band (50 rows → 70, y 4–73), directly in service of problem 2: more room for the
subepithelial compartment to accumulate cell mass/ECM before running out of space.

- [x] `Subepithelial_FibrosisSteppables.py`: `OUTER_BOUNDARY_Y_MIN/MAX`,
      `SUBEPITHELIAL_Y_MIN/MAX`, `EPITHELIAL_Y_MIN/MAX` reassigned to the new bands; the old
      `LUMEN_MAX_Y` (upper bound of a low-y lumen) replaced with `LUMEN_MIN_Y` (lower bound of a
      high-y lumen).
- [x] Every directional check tied to the old geometry updated to match, not just the
      constants: `secrete_epithelial_ecm`'s subepithelial-side-only write condition (was `ny <
      SUBEPITHELIAL_Y_MIN`, now `ny > SUBEPITHELIAL_Y_MAX`), the fibroblast wrong-direction
      guard in `update_fibroblasts` (was `yCOM < SUBEPITHELIAL_Y_MIN`, now `yCOM >
      SUBEPITHELIAL_Y_MAX`), `recruit_fibroblasts`'s boundary-adjacent band (was anchored to
      `SUBEPITHELIAL_Y_MAX`, now to `SUBEPITHELIAL_Y_MIN`), and `DiagnosticsSteppable`'s lumen
      collagen-leak check (was `y <= LUMEN_MAX_Y`, now `y >= LUMEN_MIN_Y`).
- [x] The disabled `create_airway()` block (dead since the 2026-08-08 A8 decision, see Priority
      1) flagged in a comment as stale against the new geometry too, in case anyone resurrects
      it without rereading it.
- [x] Smoke-tested: 500-MCS run on a scratch copy (`Steps` temporarily reduced), clean —
      `fragmented=0 isolated=0` at MCS 0 and 499, no mesenchymal cell inside the epithelial
      band, field `C` lumen max stayed 0 throughout (collagen-free lumen confirmed under the new
      geometry), `R_fib` recruitment fired twice (MCS 234, 276) at y=5 and y=7 — inside the new
      boundary-adjacent band as intended, not the old one. XML validated. No traceback.
- [x] **Full 20,000-MCS confirmation run — done and clean 2026-08-11**
      (`results/cc3d/v1-reorder-clean20k-run.log`), against committed defaults (no experiment
      parameters — see the note on the parallel experiment run below).
      `fragmented=0 isolated=0` at MCS 0, 1000, and 19999. **Mesenchymal cells with COM inside
      the epithelial band: 0 at every checkpoint** (0, 1000, 19999) — same clean containment as
      the pre-reorder runs, confirming the reorder itself introduces no leak. Field `C` lumen
      max stayed 0 at all ~200 checkpoints across the full run. Runtime 34m29s (2069s), close to
      the pre-reorder ~24–29 min baseline (an earlier attempt at this same run took 3h+ purely
      because the laptop repeatedly entered Modern Standby mid-run — confirmed via
      `Get-WinEvent`/Kernel-Power events, not a code or performance issue; this run kept the
      machine awake throughout).
      A parallel run was also done same-day with a deliberate parameter experiment layered on
      top of the same reorder (`FIBROBLAST_INITIAL_NUMBER=80`, `EpitheliumDamaged`/
      `EpithelialHealthy`/`Myofibroblast` G secretion raised, `Fibroblast` chemotaxis
      unrestricted and `Lambda` raised to 1000 — committed separately, see
      `69aae36 experiment: raise G secretion, fibroblast count, unrestrict chemotaxis`). That
      run showed 4 mesenchymal cells with COM inside the epithelial band at MCS 1000 and 19999,
      attributable to the experiment (steeper G gradients pulling fibroblasts closer to the
      epithelium, per the removed `ChemotactTowards` restriction), not the reorder — confirmed
      by this clean run's 0-at-every-checkpoint result under identical geometry. Note also that
      the "mesenchymal cells with COM inside band" check compares against the fixed
      initialization constants (`EPITHELIAL_Y_MIN`/`MAX`), not the sheet's actual current
      position — if the sheet is genuinely displaced, this check can't distinguish "cell in
      vacated space the sheet moved out of" from "cell overlapping the current sheet." Not an
      issue for this 0-result clean run, but relevant to how the experiment run's 4-count should
      be read, and a reason to build real sheet-position tracking (plan step 1 below) rather
      than lean on this diagnostic for displacement conclusions either way.

### Apical/basal/lateral compartments and Links (FPP) — reviewed, not adopted for v1

Reviewed `cc3d expertise/Module Transcripts/Module 5.1 Copmpartmental cells.txt` (+ Day 5's
"Cell Compartments" slides) and `Module 7.3 Epithelial Cells and Folding.txt` (+ Day 7's "Tissue
Folding" slides), plus Day 6's "Links — Basics"/"Links — Applications" slides (no transcript for
6.2/6.3, slides only — confirmed "Links" is just the workshop's name for the
FocalPointPlasticity/FPP plugin, same plugin Module 7.3 uses for folding).

- **Apical/lateral/basal compartments — not required for v1's displacement mechanism, deferred.**
  Module 5.1's exercise builds exactly this structure (ECM cell type at the bottom, then basal,
  lateral, apical, Medium above — the same stack this reorder just built at the tissue level)
  using `ClusterId` to group the three sub-cells into one compartmentalized epithelial cell, a
  `ContactInternal` plugin for low internal (within-cell) energies, and directional external
  energies (basal↔ECM low, apical↔Medium low, apical↔ECM and basal↔Medium both very high,
  lateral high to both) so the compartments stay polarized and aligned between neighbors. This
  would give the model a biologically motivated basal→ECM adhesion preference the current
  single-type epithelium can't express (`Contact(Medium, EpithelialHealthy)` is one number
  regardless of which side of the sheet the Medium pixel is on). But v1's displacement mechanism
  (A8) is a bulk volume-exclusion effect — subepithelial cell/ECM mass grows, the frozen outer
  boundary directs that growth inward, the sheet is pushed because Medium is the path of least
  resistance — and that doesn't depend on sub-cellular polarity. Adopting it now would also be a
  substantial rearchitecture (new cell types, `ClusterId` bookkeeping, `ContactInternal`, and
  every place that currently loops over `EPITHELIALHEALTHY`/`EPITHELIUMDAMAGED` — damage
  seeding, ECM secretion, sheet-integrity checks — would need a three-compartment-aware rewrite).
  Left as a v1.5/v2 realism upgrade, not a blocker for the displacement question below.
- **Links (FocalPointPlasticity) and tissue folding — not needed for *active* folding, but
  adopted 2026-08-13 for passive cohesion (reconciled 2026-08-14).** The judgment below about
  *active* force generation (apical constriction, crawling, convergent-extension, tissue
  folding) still stands — v1 doesn't need any of that, and hasn't adopted it. But
  `d718a23` (2026-08-13) added FPP links between neighboring epithelial cells for a narrower,
  different purpose: passive structural cohesion, added after the `targetVolume` coupling
  (PRIORITY 0 plan step 3) surfaced a flickering sheet-breach risk — mesenchymal cells briefly
  slipping between adjacent epithelial cells under compression before `ConnectivityGlobal`
  caught it. The links hold neighboring epithelial cells at a fixed target distance without
  actively contracting anything, i.e. a stiffer seam, not a force generator. This doesn't
  contradict the "active force mechanics not needed" conclusion below; it does mean "not
  adopted" was premature as a blanket statement — should have been scoped to "not adopted *for
  active folding*" from the start. Confirmed clean over the 2026-08-14 full run (`fragmented=0
  isolated=0` throughout, 0 mesenchymal cells in the epithelial band at every checkpoint).
  Original reasoning for the active-mechanics judgment, unchanged: FPP
  links are for *active* force generation between specific cell/compartment pairs: Module 7.3
  uses them for apical constriction (locally increasing link `Lambda`/decreasing target distance
  between neighboring apical compartments to actively bend/invaginate the sheet); Module 6.2/6.3
  use the same plugin for cell crawling, anchors, and convergent-extension. All of those are
  active contraction or migration mechanics. v1's core displacement mechanism is the opposite: a
  *passive* compression/volume-exclusion push from an expanding neighboring compartment, which
  the existing `Contact` + `VolumeLocalFlex`/`SurfaceLocalFlex` + `ConnectivityGlobal` + `Freeze`
  plugins already express without any active force term. Tissue folding specifically (Module
  7.3's stated motivation — gastrulation, neural tube closure) is also the wrong phenomenon:
  those are shape changes (bending/invagination) driven by localized contractile forces, not the
  bulk translation of a flat sheet that lumen narrowing calls for here.

### Plan: epithelial displacement in response to ECM deposition

**Is displacement expected/necessary at all?** Necessary, yes — it's the model's headline
readout. The validation target (`docs/validation_targets.md` §3.5, Higham et al., ~22% lumen
narrowing) is stated as lumen narrowing, and A8 deliberately chose lumen = Medium + frozen outer
boundary specifically so narrowing is *produced by* epithelial-sheet displacement rather than
being a separate term bolted on. There's no version of this model's core claim that doesn't
require this to work.

**Is it expected to actually happen with current parameters?** No — and not because the reorder
is wrong. Two structural gaps, found while reasoning through the new geometry's numbers:

1. **The subepithelial compartment is nowhere near capacity.** `FIBROBLAST_INITIAL_NUMBER = 10`
   at `TARGET_VOLUME_FIB = 30` is ≈300 px of cell volume against a 70×200 = 14,000-px
   subepithelial band — ≈2% occupied at t=0. `R_FIB = 0.001` was deliberately set low
   2026-08-09 ("roughly doubling the initial pool... not dominating it," see Group 3 above), so
   it doesn't change this picture much over a full run. A CPM sheet only gets pushed when the
   neighboring compartment runs out of empty (Medium) pixels to grow into; at this occupancy
   there's abundant slack, so there's no crowding pressure against the epithelium to speak of.
2. **Field `C` has no volume-occupying representation.** A14/A8 decided ECM/collagen is a
   non-diffusing accumulator field, which is right for tracking burden — but nothing currently
   converts accumulated `C` into pixel-claiming mass. `C` only feeds into `lambdaVolume` scaling
   (stiffens cells that are already there) via `c_norm`; it never grows a cell's `targetVolume` or
   otherwise claims lattice space. So even where `C` is very high (mean 6.2 / max 79.9 by MCS
   20000, per the 08-09 Group 3 run), that accumulation currently has zero mechanical consequence
   for the compartment's footprint.

Net: displacement is likely near-zero right now, for reasons unrelated to this reorder. The
reorder (halved lumen, larger subepithelial band) makes a real displacement legible once one
exists; it doesn't by itself create one.

**Recommended order of work:**

1. [x] Run the full 20,000-MCS confirmation under the new geometry, and actually measure
   epithelial sheet position drift (mean apical-boundary y of epithelial cells, MCS 0 vs.
   19999) — quantify whatever displacement already exists, however small, before changing
   anything. **Done 2026-08-11** (`compute_epithelial_sheet_position`, mean/min/max yCOM).
2. [x] Implement the lumen-area readout (Priority 1 item 4, unchanged by this reorder): a
   connected-region flood-fill from a lumen seed point each checkpoint. **Done 2026-08-11**
   (`compute_lumen_area`); **the parallel `field C lumen max` collagen-leak check still used a
   fixed y-band until 2026-08-14**, when it was refactored to share the same flood-fill
   (`flood_fill_lumen_pixels()`) rather than re-deriving a separate fixed-band definition of
   "lumen" — see the PRIORITY 0 status block above for what that fix found.
3. [x] **Close gap 2 — the load-bearing fix.** Couple local `C` to myofibroblast `targetVolume`
   growth, not just `lambdaVolume`. **Done 2026-08-12** (`7858a83`), `K_C` recalibrated
   160 → 20. **Result (confirmed 2026-08-14 under the corrected diagnostic): produces real but
   small displacement that plateaus almost immediately** — 2.1% narrowing by MCS ~300-400,
   2.5-5.5% by MCS 19999 depending on run (stochastic spread), vs. the ~22% Higham target. Not
   the zero-displacement result gap 1/2 predicted, but not enough on its own either.
3a. [x] **Diagnose the early plateau before touching (4) or (5) — done 2026-09-03, root
   cause identified.** Four hypotheses tested in sequence on 3000-MCS scratch runs (see
   `lab-notebook/2026/2026-09-03.md` for full numbers), each ruling in/out the next:
   - **`c_norm(C)` saturation — ruled out.** Mean `c_norm` was only 0.02 at MCS 300-400 (the
     plateau's onset) and just 0.17 by MCS 2999, nowhere near the 0.9 threshold, while field
     `C` and the myofibroblast population both kept climbing the whole run.
   - **FPP-link mechanical lock (`EPITHELIAL_FPP_LAMBDA` 50→0 test) — not the primary
     cause.** Narrowing plateaued almost identically with links off; at most a small secondary
     drift, not the plateau itself. Sheet integrity stayed clean either way.
   - **Interface under-occupancy — ruled out, and backwards.** A 10-row band directly under
     the epithelium was *more* crowded than the bulk subepithelial compartment throughout
     (38% vs. 22% by MCS 2000), still visibly climbing, while narrowing stayed flat.
   - **Volume frustration — decisive.** Interface myofibroblasts reach ~97-100% of their
     (growing) `targetVolume` throughout — not losing an energy competition against the sheet.
     The epithelium's own volume/targetVolume ratio sits at essentially exactly 1.000 the
     entire run — **it is not being meaningfully compressed at all.**

   **Root cause: the subepithelial compartment, even at its most crowded point directly under
   the sheet (~35-38% occupied), still has enough empty Medium pixels nearby for myofibroblasts
   to satisfy their `targetVolume` growth without ever needing to push against the epithelium.**
   The sheet isn't losing a fight it's currently in — it isn't in a fight yet. This confirms
   (rather than supersedes) the original gap-1 diagnosis further up this doc, from before the
   `targetVolume` coupling landed ("subepithelial compartment nowhere near capacity"): the
   coupling fix (gap 2) made individual myofibroblasts grow with local `C`, but growth into
   abundant local slack isn't the same as growth that contests a boundary. The small narrowing
   that does happen (2-7% across today's and prior runs) looks like occasional stochastic
   pixel-copy wins at the sheet edge, not sustained mechanical pressure — consistent with
   plateauing fast and then only drifting. **Unblocks step 4 below with a specific target: raise
   population (via `R_fib` and/or mitosis) enough to push interface occupancy well past today's
   ~38% ceiling, not "more signal per cell."**
3b. [x] **Done 2026-09-26 on the new geometry: 6 pinned + 2 unpinned full runs, −8.6% to −17.2%
   at MCS 20000 (mean −12.3%, SD 3.0), no plateau — see the 2026-09-26 update at the top of this
   doc. The 2.5% vs 5.5% pair below is old-geometry and no longer comparable.** Original item:
   **New, 2026-08-14 — run at least one more full-run replicate** (different stochastic
   seed) before drawing conclusions from the 2.5% vs. 5.5% gap between the two runs so far —
   not yet known whether that's the real spread or an outlier pair.
4. [x] **(3a) is done and confirms this is the load-bearing gap. [DECIDED 2026-09-06,
   see "Next session priorities" item 0]: fibroblast mitosis is built, but scoped as a
   biologically-motivated feature in its own right (proliferation is a real fibroblast
   characteristic), NOT tuned as the fix for this gap — a v2 volume-occupying ECM cell
   type is prioritized as the actual displacement mechanism instead.** Mitosis
   (`FibroblastMitosisSteppable`) is GF-gated on *where/whether* a fibroblast divides
   (Molina et al. 2025), held at the literature cell-cycle rate (~1730 MCS from the cited
   25-34h doubling time, Mio1992/Holz2004 — deliberately not raised to force displacement).
   **Confirmed 2026-09-06** on the full 20,000-MCS committed XML (`results/cc3d/v1-mitosis-confirm20k-run.log`):
   clean, 3 total divisions over the run (see item 2 above for why that's the expected,
   reasonable-and-low outcome, not a bug), -4.6% lumen narrowing — within the same stochastic
   range as without mitosis, confirming it doesn't move this plateau. A same-day `FIBROBLAST_INITIAL_NUMBER=80→300` scratch test (3.75x, two
   replicates) found the 10-row interface-band average is the wrong thing to design against: it
   stayed a misleading 44-61% throughout while displacement actually happened, and only a new
   **single boundary-row occupancy** measure (`y=SUBEPITHELIAL_Y_MAX` only, i.e. the pixels
   literally touching the epithelium) tracked the real event — it peaked at 72.5% right when
   narrowing ran from -4.3% to -10.4% (MCS 100-300), then relaxed back to 26.5% by MCS 2999
   while narrowing stayed locked at -10.6% to -10.9% (`ConnectivityGlobal`/FPP hold the won
   position; the boundary doesn't need to *stay* dense once it's pushed). **Design target for
   the fixes below: spike boundary-row occupancy toward confluence, not sustain a bulk crowding
   level.** Raise population at the epithelial interface via `R_FIB` and/or the fibroblast-mitosis
   item (2026-08-14 next-session priority, GF-gated mitosis via `MitosisSteppableBase`) — scope
   both together now that both are on the table, since they're two routes to the same target
   (more cells transiently confluent at the boundary) rather than independent fixes. `R_FIB`
   itself is tied to a literature correlation (A15, Hoshino et al. 1998), so revisit its
   magnitude deliberately against that source rather than tuning it up freely; mitosis needs its
   own rate parameter (fibroblast proliferation/doubling time in fibrotic lung tissue — citation
   in progress, 2026-09-03). Note the two 300-fibroblast replicates (-7.8%, -10.6%/-10.9%) both
   ran above the -2% to -7% stochastic range seen at 80 fibroblasts but on a small sample — not
   yet strong enough to call "crowding definitely works," just strong enough to justify building
   the real fix rather than testing raw initial-count further.
5. **Last resort, not recommended unless (3)+(3a)+(4) together still don't move the sheet:** a
   literal volume-occupying ECM cell type, mirroring Module 5.1's ECM compartment and/or
   Chandrasegaran et al.'s discrete ECM cells (see `docs/ecm_field_vs_celltype_assessment.md`,
   written 2026-08-14 specifically to have this reference ready). This would reintroduce a
   static-mass cell type running parallel to field `C` — duplicates what `C` already tracks and
   reopens the "burden vs. density" question A14 already settled. Only worth it if the
   field-based route is structurally incapable of producing displacement even with (3)+(4).
6. Once displacement is measurable at a scale worth checking, rerun Priority 1 item 5's
   acceptance check, restated for the new geometry: sheet stays continuous
   (`ConnectivityGlobal` should already guarantee this — no fragmentation, confirmed clean
   through 2026-08-14), and additionally check the sheet doesn't buckle non-uniformly (patches
   outrunning neighbors) or fully consume the 20-row lumen and jam against the domain's
   `NoFlux` top boundary at y=99 (the new failure mode this reorder introduces, replacing the old
   "crushed against the frozen wall" framing — the wall is no longer adjacent to the epithelium).

Apical/basal/lateral compartmentalization is not part of this plan — see above, it's orthogonal
to the displacement mechanism, which is a bulk volume-exclusion effect independent of
sub-cellular polarity.

---

## Completed — verified against full 20,000-MCS runs

### Mechanics and sheet integrity (Group 1, done 2026-08-08)
- [x] Per-type `FluctuationAmplitude` (2/2/10/6 for Eh/Ed/Fibroblast/Myofibroblast) — cold
      epithelium, warm mesenchyme, without `Freeze`.
- [x] `ConnectivityGlobal` penalty 1e6 on both epithelial types.
- [x] `ChemotactTowards="Medium,Fibroblast,Myofibroblast"` + `SaturationCoef="1.0"` on both
      `ChemotaxisByType` entries, so chemotaxis can't drive cells through the epithelium.
- [x] Myofibroblast chemotaxis `Lambda` decided and set to **0** (not the inherited 120) —
      myofibroblasts are ECM producers, not GF-seekers, per `model_spec_v1_v2.md`.
- [x] `SurfaceLocalFlex` wired: `cell.targetSurface = cell.surface`,
      `cell.lambdaSurface = LAMBDA_SURFACE_EPITHELIAL`, set once in `start()`, confirmed live
      (`surface=22.0 targetSurface=22.0` at MCS 0).
- [x] `J(EpithelialHealthy, EpitheliumDamaged)` 5 → 2.
- [x] Frozen `OuterBoundary` cell type added (`TypeId=5`, `Freeze=""`), wall at y=96–99,
      contact energies set.
- [x] Sheet integrity confirmed clean (`fragmented=0, isolated=0`) at MCS 0, 1000, **and the
      true final MCS (19999)** — the `finish()`-checkpoint bug (literal `20000` never firing)
      was found and fixed, then re-verified.
- [x] Epithelial count conservation (`n_Eh + n_Ed`) held for the entire run, every run, via a
      per-MCS assertion that never fired.
- [x] No mesenchymal cell center-of-mass ever inside the epithelial y-band.
- [x] Hallucinated `<NoFlux/>` boundary-condition XML (invalid `Plane` child) found and fixed
      on both fields → `<ConstantDerivative Value="0.0"/>` on both axes (zero-flux equivalent).
- [x] `DiagnosticsSteppable` added: field min/max/mean every 100 MCS, count-conservation
      assertion, fragmentation/gap check, mesenchymal-containment check.

### ODE-to-tissue coupling (`S_M2` pedestal only — `f_d` still untouched, see Priority 2)
- [x] `S_M2` uniform additive pedestal on field `G` implemented (`ODESignalSteppable`,
      registered before `FibrosisModelSteppable` so same-MCS reads see the update).
- [x] Route 1 (precomputed `M2_TOT_REFERENCE = 0.4464` scalar) verified over a full run —
      stable, bounded, matches energy-budget prediction.
- [x] Route 2 (live Tellurium/SBML integration inside CC3D, `TISSUE_SIGNAL_MODEL` copied
      verbatim from `supplementary.ipynb` cell 21) implemented and **fully verified**: discrete
      `WS` events replaced with a smooth sigmoid rule (fixed a CVODE convergence failure and,
      after that, an `exp()` overflow at `WS_STEEPNESS=50`). Full 20,000-MCS run clean, `M2_tot`
      holds a stable periodic attractor band (0.4388–0.4558) matching the notebook-derived
      prediction (0.4464). Documented step-by-step in `docs/tellurium_connection_walkthrough.md`.
- [x] Manual pixel-loop pattern confirmed as the only safe field read/write form on this CC3D
      4.9.0 Windows build (`np.array(field[...])` and vectorized `field[:,:,:] += x` both crash
      the C++ backend, exit `-1073740791`). Used consistently everywhere fields are touched.

### Cleanup (Group 4, partial)
- [x] `deposit_ecm()` removed — it duplicated the XML's own `<Secretion Type="Myofibroblast">`
      on field `C` and scanned all 20,000 lattice sites per myofibroblast per call (was the
      dominant runtime cost: 6× speedup after removal, 20k-MCS run 562.9s → then 1638–1751s
      once the ODE coupling was added back).
- [x] `FIBROBLAST_INITIAL_NUMBER` reduced 80 → 10 (perf, pending `R_fib` recruitment design).

### Design decisions recorded (not yet all implemented — see Priority 1)
- [x] **A8 addendum, 2026-08-08: lumen = Medium, narrowing = epithelial-sheet displacement**
      (Option 1), against three rejected/deferred alternatives. Recorded in
      `docs/model_assumptions_for_slides.md`.
- [x] **ECM/collagen decided as a non-diffusing accumulator field** (D ≈ 0), only the
      growth-factor field diffuses. Recorded alongside A8/A14.

---

## PRIORITY 1 — Epithelial sheet displacement / ECM as an accumulation field

**Status (updated 2026-08-14): mechanism implemented and producing real displacement, but small
and plateauing early — see PRIORITY 0's status block and plan (steps 3/3a/3b) for the current
numbers and open diagnosis work.** The 2026-08-08 design note (A8) commits to a specific
mechanism — subepithelial cell mass thickens, the frozen outer boundary directs that expansion
onto the epithelial sheet, the sheet slides luminally into Medium while staying intact — and as
of 2026-08-12's `targetVolume` coupling, the code now does produce this, just not yet at the
magnitude the Higham ~22% target calls for. Points 1-2 below (lumen semantics, `C` diffusion)
were prerequisites and remain accurate as a record of what was checked.

Working point by point, in this order (2026-08-09):

1. [x] **Lumen is not Medium — done, checkbox was stale.** `create_airway()` was already
      commented out 2026-08-09 (see the code comment in `TissueInitializationSteppable.start()`)
      and this item was never checked off to match. Re-confirmed 2026-08-11 in the Priority 0
      smoke test: field `C` lumen max stayed 0 throughout a 500-MCS run, i.e. the lumen band
      (now y ≥ `LUMEN_MIN_Y` post-reorder) is genuinely open `Medium`, not a soft-frozen
      placeholder.
2. [x] **Field `C` diffusion — already 0.0 in the XML (checked 2026-09-18); this item was stale.**
      Originally: `Subepithelial_Fibrosis.xml` set
      `GlobalDiffusionConstant=0.01` for field `C`, not ≈0. Small, but nonzero — collagen can
      currently leak sideways/into the lumen, which A9 (subepithelial only, not intraluminal)
      and the A8 addendum both rule out. Set to `0.0` (or as close as the solver allows) and
      re-verify the field stays subepithelial.
3. [x] **Mechanism to produce displacement — implemented, insufficient at current calibration.**
      Three candidates were considered, in order of how directly they match A8's own language
      ("subepithelial cell mass... thickens"):
      - **`R_fib` recruitment — implemented 2026-08-09** (Group 3, `R_FIB = 0.001`, GF-biased
        placement at the boundary). Tested alone against the displacement claim in PRIORITY 0's
        2026-08-11 plan: found insufficient by itself (subepithelial compartment far under
        capacity even with recruitment running).
      - **Couple local `C` to myofibroblast `targetVolume` growth — implemented 2026-08-12**
        (`7858a83`, `K_C` recalibrated 160 → 20). This is the one that produced real
        displacement, but small and plateauing early (2.5-5.5% narrowing vs. ~22% target,
        confirmed 2026-08-14 under the corrected lumen diagnostic) — see PRIORITY 0 plan steps
        3/3a/3b for the open diagnosis of why it plateaus and what's next.
      - Literal volume-occupying ECM cell type: not implemented, held as PRIORITY 0 plan step 5
        fallback; `docs/ecm_field_vs_celltype_assessment.md` (2026-08-14) has the reference
        implementation (Chandrasegaran et al.) written up in case it's needed.
4. [x] **Lumen readout — implemented 2026-08-11, diagnostic bug fixed 2026-08-14.**
      Connected-region flood-fill from a known lumen seed point each checkpoint
      (`compute_lumen_area`/`flood_fill_lumen_pixels`), used for both the area readout against
      A12/the Higham ~22% target and (as of 2026-08-14) the `field C` lumen-collagen check,
      which previously used an independent fixed-y band and produced a false-positive "leak"
      signal — see PRIORITY 0 status block above.
5. [x] **Verify the actual claim — done, result recorded in PRIORITY 0.** Superseded by
      PRIORITY 0's "Plan: epithelial displacement in response to ECM deposition" above: the
      2026-08-14 full run confirms real, non-artifactual displacement exists (2.5-5.5%
      narrowing) but plateaus far short of the ~22% target. Diagnosing the plateau (PRIORITY 0
      plan step 3a) is the open work, not "does displacement happen at all" anymore.

**Status of the R_fib full-run confirmation (Group 3): complete, clean** — see Group 3 above.
Point 3's `R_fib`-alone displacement test is now unblocked.

## PRIORITY 2 — Damaged-epithelium seeding from the ODE (`f_d`)

> **Reopened 2026-10-23: the tissue layer dropped the ODE's repair path.** Re-reading
> Torres et al. shows `E_d` is a **reversible, sub-lethal** state — repair `E_d → E_h` runs at
> `e4 = 0.002 h⁻¹`, damaged cells die at the same natural rate as healthy ones and still
> proliferate, and in the full model M2 and anti-inflammatory cytokine **enhance** repair
> (Eq. 16: `e4(1 + e8(M2 + M2_R) + e10 A)`). v1's damage is one-directional, which makes the
> tissue layer more irreversible than the signal layer feeding it, and the published antioxidant
> intervention runs partly through the repair term it is missing.
>
> - [x] **Add a repair path for `EpitheliumDamaged`**, rate derived from `e4` scaled to MCS
>       (at 62.4 s/MCS, `e4 = 0.002 h⁻¹` is ≈ 3.5e-5 per MCS per damaged cell). Decide whether to
>       carry the M2/`A` enhancement term in v1 or defer it with the rest of the ODE gain.
>       **Done 2026-10-27 (Gate B1):** `FibrosisModelSteppable.apply_epithelial_repair`, `e4` read
>       live from the SBML on the tissue clock; the Eq. 16 enhancement **is carried**
>       (`EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT`, ≈ 8.3e-5 per MCS at the attractor) because the
>       `f_d` the seeding rule tracks is the ODE's enhanced-repair balance; see `parameters.py`.
> - [x] **Rerun the committed 20k baseline after adding it.** This changes what every readout
>       measures, so it belongs **ahead of** todo item 4 (readouts), not after. **Gate B4,
>       2026-10-27**, together with B2/B3 — result in `lab-notebook/2026/2026-10-27.md`.
> - [x] Record in A14/A19 that the one-directional choice was a v1 simplification, not an ODE
>       inheritance. (Correction already written into `model_assumptions_for_slides.md` A19 and
>       `docs/aoc_platform_impact_2026-10-11.md` §2A; A19 "applied" note added 2026-10-27.)


**Status: diffuse arm implemented and verified 2026-08-09; left uncommitted and undocumented
until this 2026-08-11 reconciliation pass — the code was ahead of this doc.** This section
previously said "not started" and "zero executable uses of `f_d`" based on the last *committed*
state (`efb4037`); the actual working copy already had the items below done. Reconciled here
without re-deriving them from scratch, since the docstrings in
`Subepithelial_FibrosisSteppables.py` record the reasoning inline and cite "lab discussion
2026-08-09."

- [x] **Read `f_d` from the live ODE.** `ODESignalSteppable.step()` reads
      `Ed / (Eh + Ed)` from `self.sbml.tissue_signal` each MCS (same pattern as `S_M2`) and
      exposes it via `self.shared_steppable_vars['f_d']` for `FibrosisModelSteppable` to consume
      the same step, before the ODE advances.
- [x] **Replaced the continuous accumulator with binary state + probability**, per
      `ode_tissue_coupling_options.md` §2 Option A. `update_epithelial_damage`/
      `update_epithelial_repair` and the old `damage_inc`/`repair_rate` formulas (hardcoded
      `TGFB_LEVEL`/`PRO_INFLAMMATORY_LEVEL`/`M2_LEVEL`/`ANTI_INFLAMMATORY_LEVEL` floors,
      `DAMAGE_THRESHOLD`/`REPAIR_THRESHOLD` hysteresis) are gone, replaced by
      `FibrosisModelSteppable.apply_damage_seeding`: `P(healthy → damaged) = max(0, (f_d −
      f_current) / (1 − f_current))` applied as an independent Bernoulli trial per healthy cell
      each step. `DAMAGED` (via `cell.type`) is persistent and one-directional — there is no
      repair path back to `EPITHELIALHEALTHY` in this version, a real behavior change from the
      old hysteresis band worth remembering when reading run output.
- [ ] **Focal vs. diffuse placement rules — diffuse only.** What's implemented (independent
      per-cell Bernoulli trials at a shared `p_convert`) *is* the diffuse arm — the docstring on
      `apply_damage_seeding` says so explicitly. Focal placement (seed `k` foci at t=0, then
      convert preferentially among neighbors of already-damaged cells, probability ∝ count of
      damaged neighbors) is not implemented. This is still the independent variable of the
      headline experiment (A18) and still open.
- [x] **Gate fibroblast→myofibroblast differentiation on local `G` only.**
      `activate_fibroblast` now sets `activation_signal = G if G >= FIB_TO_MYOF_G_THRESHOLD else
      0.0` — the placeholder `TGFB_LEVEL`/`M2_LEVEL` blend is gone and `FIB_TO_MYOF_G_THRESHOLD`
      is referenced.
- [x] **Normalize `C` at point of use — resolved, though not quite as originally scoped.** The
      original item listed four call sites needing `C_norm = C/(C+K_C)`: `damage_inc`,
      `repair_rate`, `activation_signal`, and the fibroblast/myofibroblast `lambdaVolume`
      scalings. The first three no longer exist — `apply_damage_seeding` doesn't take `C` as an
      input at all (it's driven by `f_d` only), and the G-only `activation_signal` above dropped
      `C` too. Only the `lambdaVolume` stiffening in `update_fibroblast_state` and
      `update_myofibroblast_state` still consumes raw `C`, and both now go through the `c_norm()`
      helper. Net effect matches the item's intent (no more raw unbounded `C` feeding a 0–1
      signal) even though it happened by removing call sites rather than normalizing all four.
- [ ] **Acceptance test (decisive), not yet run:** zeroing every field must prevent phenotype
      conversion entirely. Nothing in the code or run logs confirms this was checked.
- [ ] **Acceptance test, not yet possible:** focal and diffuse arms must produce measurably
      different spatial statistics at matched total injury (`model/analysis/spatial_stats.py`) —
      blocked on the focal arm above not existing yet.
- [x] ~~**Normalize `C` at point of use.**~~ Duplicate of the resolved item above (done via the
      `c_norm()` helper, `K_C` in `parameters.py`); the stale unchecked copy was removed 2026-09-26.
      The two acceptance tests below were also listed twice; the two entries above are the live ones.

---

## Group 4 cleanup — done 2026-08-09

- [x] Removed `migration_factor` entirely (dict init for Fibroblast/Myofibroblast, and every
      assignment in `update_fibroblast_state`, `activate_fibroblast`, `convert_to_myofibroblast`,
      `update_myofibroblast_state`) — it was computed in four places, read nowhere; actual
      mobility differences come only from the XML chemotaxis lambdas.
- [x] Removed `wall_stress` — was read in `update_epithelial_damage` via `.get("wall_stress",
      0.0)` but never written or initialized for epithelial cells, so it always evaluated to
      0.0; dropped the dead `0.005 * wall_stress` term from `damage_inc`.
- [x] Removed unused constants `EPITHELIAL_REPAIR_THRESHOLD`, `ECM_HIGH_THRESHOLD`.
- [x] Removed `ecm_rate` — write-only since `deposit_ecm`'s removal (set in four places, read
      nowhere); no readout mechanism consumes it, so removed rather than kept for a hypothetical
      future one.
- [x] `update_epithelium`, `update_fibroblasts` now iterate over `list(cell_list_by_type(...))`
      rather than the live iterator, since `update_epithelial_damage`/`update_epithelial_repair`/
      `activate_fibroblast` can mutate `cell.type` mid-loop.
- [x] Removed the empty `ECMRemodelingSteppable`/`DataOutputSteppable` stubs (both were
      registered but `pass`-only) and their registrations in `Subepithelial_Fibrosis.py`.
- [x] Verified: 500-MCS smoke test on a scratch copy (`Steps` temporarily reduced) — clean,
      `fragmented=0 isolated=0` at MCS 0 and 499, epithelial/mesenchymal counts conserved, no
      traceback. **Full 20,000-MCS confirmation run completed 2026-08-09: clean** —
      `fragmented=0 isolated=0` at MCS 19999, no mesenchymal cell ever inside the epithelial
      band, field `C` plateaus at mean 2.4 / max 62.1 (matching the pre-cleanup 08-08 numbers,
      mean 2.4 / max ~63.2 — confirms the cleanup didn't change field dynamics).

## Group 3 (other missing ODE-interface / model components)

- [x] **Fibroblast GF secretion** — added `<Secretion Type="Fibroblast">0.005</Secretion>` to
      field `G`'s `SecretionData` (half the epithelial rate, first-pass/not calibrated).
- [x] **Myofibroblast GF secretion, low rate** — added
      `<Secretion Type="Myofibroblast">0.001</Secretion>` to field `G` (about 1/10 the
      epithelial rate, per the 2026-08-07 literature note: the autocrine loop is
      stiffness-gated and v1 has no stiffness feedback, so a high rate would run away).
- [x] **`R_fib` recruitment across the outer boundary** — implemented 2026-08-09 as a Bernoulli
      trial per MCS (`R_FIB = 0.001`, expected ~20 new fibroblasts over a full 20,000-MCS run —
      **kept deliberately very low for this first pass**, per explicit instruction, roughly
      doubling the initial pool of 10 rather than dominating it). Placement is GF-biased
      (`ode_tissue_coupling_options.md` §3 Option F.2): candidate empty pixels within a 5-row
      band adjacent to the frozen outer boundary (`y=91–95`) are weighted by local `G`, not
      chosen uniformly. New `recruit_fibroblasts()` in `FibrosisModelSteppable`; shared
      `init_fibroblast_cell()` helper factored out so t=0 seeding and recruits can't drift into
      differently-initialized fibroblasts.
      **Design decision, 2026-08-09: kept the existing uniform `S_M2` pedestal as-is** — the
      boundary-localized/macrophage-sourced `G` question raised alongside this item was
      explicitly deferred ("stick with the original plan"), not resolved either way. Still open,
      see `docs/ode_tissue_coupling_options.md` §3 and the A14 "why additive rather than
      multiplicative" note — revisit before reading too much into recruitment spatial pattern,
      since right now `G`'s only boundary-adjacent structure comes from diffusion off the
      epithelial/mesenchymal sources, not from any macrophage proxy.
      **Verified:** 3000-MCS smoke test — 4 recruitment events (MCS 374, 602, 2522, 2898), all
      placed within the intended band, x-positions spread across the domain (115, 163, 88, 197)
      consistent with GF-weighted rather than fixed placement, sheet integrity clean at MCS 1000
      and 2999. **Full 20,000-MCS confirmation run completed 2026-08-09: clean.** 18 recruitment
      events over the full run (close to the expected 20 at `R_FIB=0.001`), sheet integrity
      `fragmented=0 isolated=0` at MCS 0, 1000, and 19999. Myofibroblast count grew 10 → 28 by
      run's end as recruits differentiated. Field `C` now reaches mean 6.2 / max 79.9 by MCS
      20000 (up from mean 2.4 / max 62 without recruitment) — expected, more myofibroblasts
      secreting more collagen. Runtime 1433s (~24 min).

## Remaining — infra / carried

- [ ] **`np.array(field[...])` / vectorized-write crash** (`task_221d4c01`): reproduce standalone
      and fix/caveat `.claude/skills/cc3d-expert/references/steppable-patterns.md` — confirmed
      on both read and write sides, on CC3D 4.9.0 and 4.10.0, but not yet filed upstream or
      documented in the skill.
- [ ] Fix or rename the broken `cc3d` conda env, or repoint `CLAUDE.md`/`model/cc3d/README.md`
      at whichever env name is actually correct per machine (currently `cc3d_490` here).
- [ ] The manual pixel-loop performance cost for `ODESignalSteppable`'s field write is
      unresolved (~60% of steppable runtime); every vectorized alternative tried crashes.
      Tolerable at ~29 min/full run, not free — revisit if run count goes up.

## Documentation drift to fix

- [ ] Slide 8 of the lightning-talk deck calls ECM a "density field" — A14 decided it's
      **burden**, not density (2026-08-02, reaffirmed 2026-08-08). Update the slide. (The decks
      were removed from the repo 2026-09-06, `e4e20e6`; any copy still in use lives outside it.)
- [x] `docs/cc3d_v1_kickoff_groups1-2.md` named `Subepithelial_Fibrosis-02/` as the working copy;
      a pointer note to `subepithelial_fibrosis_draft/` was added at its top 2026-09-26.
- [x] `AirwayPlaceholder` lumen cell: resolved 2026-08-09, not kept (A8 decision). The cell type
      and its contact energies are commented out in the XML, so no new assumption is needed.
- [ ] Reconcile the spec/assumption docs with the implemented model (done for the four known
      drifts 2026-09-26: `model_spec_v1_v2.md` status note, A7 height rescale, A7 plateau
      timescale, A14 secretion rates; recheck after any further parameter changes).
- [x] **Superseded by numbered item 5 at the top of this doc (decided 2026-09-26: re-anchor).**
      Original: check the model's fibroblast:epithelial ratio against Zajicek et al.
      (1992), the only dimensionless in-tissue anchor (≈ 2.2 epithelial : 1 lamina-propria
      fibroblast in normal hamster bronchus; abstract-level, SE not SD, *(verify)*). At
      `t = 0` the model has 25 epithelial cells and `FIBROBLAST_INITIAL_NUMBER = 80`, i.e. about
      0.3 : 1 against an implied ~11 fibroblasts for 25 epithelial cells. That 80 was set
      2026-08-11 as a deliberate displacement experiment, not a calibration; decide whether the
      baseline should be re-anchored to the ratio or the departure stated as intentional.
