# Gate B′ build plan, 2026-10-30

**What this is.** The build plan for Gate B′ of `roadmap_revision_2026-10-29.md` §3: a spatial
pro-inflammatory field `P` with three tissue consumers, an MMP field, and a volume-occupying ECM
cell type, all behind switches, followed by one rebaseline. Written at kickoff, before any code,
so the criteria in §2 are pre-registered (A18). The companion checklist is the B′ section of
`cc3d_v1_todo.md`; the parameter rows are in `calibration_table.md`.

**Where the code is.** `model/cc3d/subepithelial_fibrosis_draft/Simulation/` — `parameters.py`
(389 lines), `Subepithelial_Fibrosis.xml`, `Subepithelial_FibrosisSteppables.py` (1557 lines; the
ODE string lives there), `Subepithelial_Fibrosis.py` (steppable registration order),
`ParameterScanSpecs.json` (six-replicate PSCAN). Reference point for regression: commit `434bc94`
and `results/cc3d/v1-gateB-rebaseline20k/replicates_summary.csv` (seeds 200–205). Environment
`cc3d_490` (CC3D 4.9.0).

## 1. Scope, stated once

In: `P` field and its sources (epithelium under `WS`, `S_M1` pedestal); `P` consumer 1 (local
repair gating), consumer 2 (mitosis gate), consumer 3 (epithelial MMP secretion); MMP field with a
TIMP term; ECM cell type with budget, adjacent placement, MMP removal; new readouts in the summary
CSV; one rebaseline, n = 6. Out: EMT, ASM, annulus, adventitia, the antioxidant experiment, any
write-back to the SBML, any change to the focal arm (that is Gate D). The known-wrong activation
rate is a decision item (§6), not silently in or out.

## 2. Pre-registered criteria (frozen 2026-10-30)

1. **Regression.** All five switches off: the six B4 replicates reproduce exactly, every numeric
   column of `replicates_summary.csv`, tolerance 0, checked by `compare_replicates.py`. This is
   the first criterion and the one that lets everything else be trusted. Design rule that makes it
   achievable: code behind an off switch makes no `random` draw and writes no field.
2. **Clean single-switch runs.** Each switch alone (and `P` + each consumer), 3 pinned seeds,
   20k MCS: run completes; Tier 1 holds (sheet intact, no fragmentation, zero mesenchymal overlap,
   no `C` and no ECM cell in the lumen); `P` and `MMP` reach a quasi-steady band mean; the tissue
   damaged fraction tracks the ODE's `f_d` (mean |f_tissue − f_d| < 1/25, one cell's worth).
3. **Direction checks, one per loop, ordinal.** `P_GATES_REPAIR` lengthens mean damaged-cell
   lifetime vs off. `P_DRIVES_PROLIFERATION` raises fibroblast divisions vs off. `MMP_FIELD_ENABLED`
   lowers the final ECM-cell count vs ECM-only. `ECM_CELLS_ENABLED` gives a nonzero ECM pixel
   fraction confined to the subepithelial band. Lumen change is reported for every condition and
   pre-specified for none.
4. **Rebaseline.** All on, n = 6, seeds 200–205, 20k MCS, `-f 50` lattice snapshots on. Tier 1 in
   every replicate. Reported: lumen % change, ECM-cell area fraction, ECM count, myofibroblast
   count, divisions, repair events, mean damaged lifetime, `P` band mean, `MMP` band mean, H5
   `P`-analogue, on the chip clock where applicable. Destabilised means a sheet breach, an ECM cell
   above the sheet, or a diverging field in any replicate; that switch then runs off in Gate D.

## 3. Design decisions fixed now

- **Switches** in `parameters.py`, Model section: `P_FIELD_ENABLED`, `P_GATES_REPAIR`,
  `P_DRIVES_PROLIFERATION`, `MMP_FIELD_ENABLED`, `ECM_CELLS_ENABLED`, all `False`. Consumers
  require the field (`P_GATES_REPAIR` without `P_FIELD_ENABLED` raises at `start()`). The summary
  CSV gets one column per switch so no run is ambiguous.
- **Fields.** `P` and `MMP` are `DiffusionSolverFE` fields declared in the XML alongside `G` and
  `C`, with Neumann boundaries like the others, **but their secretion is written from Python**, not
  `<SecretionData>`: the `P` source is gated by the live `WS` read from the SBML each MCS, and the
  MMP source depends on `P_local`, neither of which the XML can express. The XML fields exist even
  when the switches are off (declaring a field with zero sources changes nothing in the Potts
  dynamics); this is checked by criterion 1.
- **Per-pixel loops** are the accepted pattern in this build (the `S_M2` pedestal already loops
  200 × 100 pixels every MCS because the vectorised setter crashes CC3D 4.9.0). `S_M1` and the
  `C`-decay term add two more. Budget ~3× the current pedestal cost; measured in Phase 1.
- **`P` sources.** Healthy epithelium `p_h · WS`, damaged `2 p_h · WS` per cell per MCS, written to
  the cell's boundary Medium pixels on the subepithelial side, the same geometry
  `secrete_epithelial_ecm` uses, so `P` is in the wall, not the lumen. `WS` pulses on the ODE clock
  (three one-hour windows per 24 ODE-hours = per 24 MCS); with a `P` half-life of hours on the
  tissue clock the field averages the pulses, which is the intended behaviour and the two-clock
  caveat stands.
- **`S_M1` pedestal** `k_M1 · (M1 + M1R)` added to every `P` pixel each MCS, with
  `k_M1 = p_h · (m6/e5) · Hm3^nm3/(A^nm3 + Hm3^nm3)`, read from the live SBML. No new freedom.
- **Consumer 1.** `apply_epithelial_repair` reads `local_P` per damaged cell and uses
  `p_repair / (1 + k_P P_local)`; the global `p_repair` from `ODESignalSteppable` is unchanged.
  Seeding still tops up to `f_d`, so matched damage is preserved.
- **Consumer 2.** `update_fibroblast_mitosis` gates on `G_local + k_prolif P_local ≥
  FIBROBLAST_MITOSIS_G_THRESHOLD`. Activation (`activate_fibroblast`) stays on `G` alone.
- **Consumer 3 / MMP source.** Epithelium writes `mmp_0 (1 + k_mmp P_local)` into the same boundary
  pixels as `P`. Myofibroblasts subtract `timp_rate` from MMP at their COM each MCS, clamped at 0.
  `C` decays at `0.0005 + k_C,mmp · MMP_local` (XML keeps 0.0005; Python subtracts the MMP term
  per pixel when the switch is on; optional, since `C` is stiffness-only now).
- **ECM cell type.** `ECM`, TypeId 6, passive (no chemotaxis, no secretion, no mitosis),
  `FluctuationAmplitude` 2 like the epithelium, no `ConnectivityGlobal`. Size: 7 µm at 1.25 µm/px
  is 5.6 px, so target volume 36 px (6 × 6); whether a new ECM cell is seeded at 2 × 2 px and grows
  to 36 or placed at 36 is open (§6). Contact energies are **not** copied from Chandrasegaran
  (their −2/−1/+1 are on a different J scale); first-pass values on this model's scale, to be
  verified in a 3k-MCS smoke run: ECM–ECM 2 (cohesive), Medium–ECM 8, ECM–Fibroblast and
  ECM–Myofibroblast 16, ECM–Epithelium 17.32 (mirrors Medium–Epithelium so the sheet sees matrix
  as it saw Medium and can still be displaced), ECM–OuterBoundary 0. `lambdaVolume` 10,
  `lambdaSurface` 0 (stiff but not surface-constrained).
- **ECM production.** Each myofibroblast accumulates `ecm_budget += ECM_BUDGET_INCREMENT` per MCS
  (*first pass 0.01 px/MCS, decided 2026-11-05, §6 item 10*)
  while it has a Medium neighbour (mirrors the `SecretionOnContact` condition; `C` secretion into
  the field stays as it is, so `c_norm` stiffening is unchanged; *superseded 2026-11-05, §6 item 9:
  no `C` under ECM cells, so no `c_norm` stiffening either*). When `ecm_budget ≥ ECM_QUANTUM`
  one ECM cell is created on a Medium pixel adjacent to the myofibroblast's boundary, chosen with
  weight ∝ exp(β · (y − y_min_candidate)) so placement is biased toward the sheet without being
  deterministic (β = 0 is uniform; β is a stated free parameter), and the budget drops by
  `ECM_QUANTUM`. Never a random domain position. No placement into the lumen band or above the
  sheet's current footprint (`compute_epithelial_column_bounds` already gives it).
- **ECM removal.** When `MMP_local ≥ MMP_thr` at an ECM cell's COM, `delete_cell`. Freed pixels
  become Medium. Counted in the CSV. *Superseded 2026-11-04 (§6 item 8): removal is rate-based,
  probability `K_ECM_MMP · MMP_local` per ECM cell per MCS; there is no `MMP_thr`.*
- **Myofibroblast volume.** Under `ECM_CELLS_ENABLED`, `MYOF_TARGET_VOLUME_GROWTH_FACTOR` is
  replaced by `MYOF_TARGET_VOLUME_GROWTH_FACTOR_WITH_ECM` (first pass 0.0; §6). The λ_volume
  stiffening with `c_norm` stays.
- **Readouts** added to `DiagnosticsSteppable.write_replicate_summary`: `n_ECM`,
  `ecm_area_frac_band`, `ecm_removed`, `mean_P_band`, `mean_MMP_band`, `P_analogue_H5`,
  `mean_damaged_lifetime_mcs` (needs a per-cell `damaged_since` stamp), the five switch flags, and
  a `ecm_centroids_<iter>.csv` dump at the final MCS for Ripley's K. `-f 50` snapshots for the
  rebaseline.
- **Steppable order** is unchanged: `ODESignalSteppable` (now also writes `S_M1` and exposes `WS`,
  `M1_tot`, the Hill factor) → `FibrosisModelSteppable` (reads `local_P`, `local_MMP`; `P` and MMP
  secretion; ECM budget and placement; removal) → `FibroblastMitosisSteppable` → `DiagnosticsSteppable`.

## 4. Build order

| Phase | Adds                                                                                                                                                      | Files                                                                   | Done when                                                                                                                                                           | Size                                                             |
| ----- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| 0     | Five switches; `tools/compare_replicates.py` (exact diff of two summary CSVs); this doc's §2 copied into the lab notebook                                 | `parameters.py`, new script                                             | Script passes B4 against itself and fails on a one-digit edit                                                                                                       | ½ session                                                        |
| 1     | `P` field in XML; Python secretion under `WS`; `S_M1` pedestal; `local_P`; `mean_P_band`, `P_analogue_H5` in CSV; wall-time check of the extra pixel loop | XML, steppables, parameters                                             | 3k-MCS smoke run: `P` quasi-steady in the band, zero in the lumen band, switch-off run bit-identical to B4 seed 200 at 3k                                           | 1 session                                                        |
| 2     | Consumers 1 and 2; `damaged_since` stamp and mean lifetime readout                                                                                        | steppables, parameters                                                  | Smoke runs show lifetime up under consumer 1 and divisions up under consumer 2, each vs switch-off, same seed                                                       | 1 session                                                        |
| 3     | MMP field; epithelial MMP source on `P_local`; TIMP subtraction; `C` MMP-decay term                                                                       | XML, steppables, parameters                                             | Smoke run: MMP quasi-steady, highest under damaged cells, lowered at myofibroblast COMs                                                                             | 1 session                                                        |
| 4     | `ECM` cell type; budget, placement, removal; `targetVolume` factor switch; ECM readouts and centroid dump                                                 | XML, steppables, parameters                                             | 3k and 20k smoke runs: ECM cells appear adjacent to myofibroblasts only, none above the sheet, Tier 1 holds, area fraction rises monotonically; MMP on removes some | 2 sessions                                                       |
| 5     | Criterion 1 (PSCAN, all off, n = 6, diff), criterion 2–3 (single-switch, 3 seeds each), criterion 4 (rebaseline PSCAN, all on, `-f 50`)                   | `ParameterScanSpecs.json` copies per condition, `results/cc3d/bprime-*` | All four criteria recorded in the notebook, CSVs in `results/`                                                                                                      | 2 sessions, mostly wall-clock (each 20k run ≈ 55 min; 3 workers) |
| 6     | Calibration-table statuses, A13/A14/A17 implementation notes, methods paragraph for Gate E                                                                | docs                                                                    | Spec and assumptions docs match the code                                                                                                                            | ½ session                                                        |

Eight to nine sessions. The ECM cell type is the largest piece and the one with its own switch
for a reason; if Phase 4 is not clean by mid-December, Phases 5–6 run without it and Gate D runs
conditions (0)–(3).

**Phase 1 status (2026-10-31).** Built and smoke-tested; details in `lab-notebook/2026/2026-10-31.md`.
Three departures from the §3 text, each stated in `parameters.py`:

- *Pedestal.* The ODE's macrophage term is `m6 · WS · Hill(A) · (M1 + M1R)` (found 10-30), so the
  implemented `S_M1` carries the `WS` gate the §3 formula omitted, and the `n_epi / N_band` spread
  that turns the per-cell `p_h` into a per-pixel rate (without it the pedestal would be ~800× the
  ODE's ratio to the epithelial term). It is added to the **subepithelial band only**, not every
  pixel: macrophages sit in the lamina propria, and a lumen pedestal would contradict the "zero in
  the lumen" check. Neither factor is a new freedom.
- *Lumen `P` is not zero and cannot be.* The sources write only into wall pixels (verified), but
  `P` diffuses with λ = 80 px and the epithelium is not a barrier (a `DiffusionCoefficient` of 0 in
  a cell type is a sink in the FE solver, not a wall, and consumer 1 needs `P` *inside* damaged
  cells anyway). At 3k MCS the flood-filled lumen mean is 0.98 against a band mean of 0.84: the
  lumen is 10–30 px from the basal source and is a dead-end reservoir, the band extends 67 px
  below it. Nothing in the lumen reads `P`, so this changes no result; it is a readout statement.
  **Decision for Marcella (item 5):** accept (lumen `P` reported, not constrained) or add a
  luminal sink (zero `P` on the flood-filled lumen pixels each MCS, an airway-surface clearance
  analogue; one more per-pixel loop). Recommendation: accept, state it in A13/A14.
  *2026-11-01:* accepted as a readout; boundary conditions cannot do it (they act at the lattice
  edges, the sheet is interior), the old `AirwayPlaceholder` decay sink stays rejected under A8, and
  a zero diffusion coefficient in the epithelial types would make the sheet a sink that starves
  consumer 1. The D = 0.10 decision above shortens λ to 12 px, which lowers lumen `P` on its own
  (numbers in the 11-01 notebook). The clearance sink stays available as a Gate D sensitivity.
- *`P` constants.* Decay takes the 10-30 pin (the ODE's `m7`, 6.93e-4 /MCS) and `p_h` = 3.44 is
  derived so the band mean at the attractor is ≈ 1 under a uniform-field approximation. **Diffusion:
  built 10-31 at the 10-30 pin (λ = 100 µm → D = 4.44, 44× `G`'s), then set to the §5 placeholder
  D = 0.10 = `G`'s on 2026-11-01 (Marcella):** TGF-β1 and IL-6 are the same molecular size, so the
  fields should differ by decay (latent, matrix-bound vs soluble, short-lived), not by D, and a 44×
  gap on one pin would produce effects with no comparative basis. At D = 0.10 λ_P = 12 px, 4× `G`'s
  3.2 px from the slower decay alone. The 100 µm pin is the stated sensitivity arm, and a literature
  pass for a λ *range* for both fields (`lab-notebook/2026/2026-11-01_lit_diffusion_ranges.md`)
  replaces the single pin; the range becomes a Gate D sensitivity axis. *Result (same day):* free D
  is the same for both molecules and unusable for either (λ > 600 px); the model's D is the
  binding-dressed value and the citable quantity is the range. `G`: ≤ 70 µm down to contact-only;
  `P`: 25–120 µm, 250 µm ceiling. **The shared D = 0.10 puts both fields below their ranges**
  (λ_G = 4 µm, λ_P = 15 µm). Gate D sensitivity axis: λ_G = 10, 20, 40, 70 µm (D = 0.64, 2.56,
  10.2, 31.4) and λ_P = 25, 50, 100, 120 µm (D = 0.28, 1.11, 4.44, 6.39), with D = 0.10 as the
  contact-only lower arm of each. The shared-D rule holds as a *ratio* (λ_P/λ_G = √(k_G/k_P) = 3.8,
  inside the 1–10 the sources allow); if kept, D = 2.5–4.5 puts both in range. **Decision for
  Marcella (item 6):** keep shared D and raise it to 2.5–4.5, or scan λ_G and λ_P separately with
  D = 0.10 as the build value. Also: read `G` as the lumped active + latent TGF-β pool so k_G = 0.01
  stands (active-only would be 0.0072–0.45 /MCS). *Decided 2026-11-02 (Marcella): **no shared-D
  rule** — there is no reason for one, and it must not get locked in; each field is pinned
  independently to a reasonable starting value from its own range, as the centre of its later
  scan. `P` therefore runs at **λ_P = 50 µm = 40 px, D = 1.11 px²/MCS**, the centre of 25–120 µm and
  the second scan point (`P_DIFFUSION_LENGTH_UM`; scan tuple and 250 µm ceiling in `parameters.py`).
  `G` stays at 0.10 for B′ because criterion 1 freezes the base model (its D is not behind a switch);
  its 10–70 µm range is a Gate D axis, and moving its build value is a base-model change with its own
  pre-registration. The lumped active + latent reading of `G` is still open.* CC3D 4.9.0's
  `DiffusionSolverFE` sub-steps automatically above its stability limit (20 calls/MCS at D = 4.44;
  `<ExtraTimesPerMCS>` is ignored), so the sensitivity run needs only the constant changed.

**Phase 2 status (2026-11-02).** Consumers 1 and 2 built as in §3 (`K_P` = 1.0, `K_PROLIF` = 0.5 ×
threshold, both read `local_P`; off, the B4 code path with the same random draws), plus the
`damaged_since` stamp and readouts. Details in `lab-notebook/2026/2026-11-02.md`. Two findings that
change how criterion 3 is read:

- *Realized repairs are too rare for a same-seed direction check.* At the attractor rate there is ~1
  repair per 10k MCS; the 10k seed-200 twin had the same single repair with and without consumer 1
  (the draw fell below the gated probability too). Added two deterministic columns:
  `expected_repairs` (sum of per-cell, per-MCS gated probabilities) and `expected_damaged_lifetime_mcs`
  (damaged cell-MCS over expected repairs). Consumer 1 **doubles** the expected lifetime (12,074 →
  24,508 MCS at 3k; `P_local` ≈ 1.6 at a damaged cell, factor 1/(1 + 1.6)). Criterion 3's first check
  reads this column; the realized `mean_damaged_lifetime_mcs` is reported alongside.
- *The mitosis gate is saturated by `G`.* Band `G` passes the 0.225 gate by MCS 1400 and sits at 1.5–1.7
  thereafter (the raised myofibroblast secretion, A14), so `P` opens the gate only in the first ~1500
  MCS or far from sources: `p_tipped_gate_frac` = 0.3 % of fibroblast cell-MCS at 3k. Divisions were 9
  vs 9 at 3k and 33 vs 35 at 10k, and the fibroblast pool is fully converted by ~6k in both runs.
  Consumer 2 cannot raise divisions in this regime; criterion 3's second check reads
  `p_tipped_gate_frac` > 0 and the early-window timing shift (first divisions 1–11 MCS earlier), and
  the Gate D ablation measures the loop as-is. A `k_prolif` that mattered would need either a lower
  `G` background (the A14 drift) or a much larger coefficient; neither is changed here.
  *Decided 2026-11-02 (Marcella): accepted for now.* The `G` background and the gates it drives
  (`FIBROBLAST_MITOSIS_G_THRESHOLD` 0.225, `FIB_TO_MYOF_G_THRESHOLD` 0.45) are re-pinned together
  when Jones assays 1, 2 and 4 report (secretion rates, the α-SMA EC50 and time course, the
  proliferation dose), with the roadmap's one allowed rebaseline rerun (§2.4 of the 10-29 revision);
  the activation-rate fix is §6 item 2. If the assays have not reported by Phase 5, the rebaseline
  runs with the drift and the methods say so. Insurance that needs no assay: a Gate D sensitivity
  arm at the pre-2026-08-11 myofibroblast `G` rate (0.001), which restores a gate `P` can tip.

Also: `mean_abs_fd_gap` (criterion 2) is 0.007–0.009 in every run, against the < 0.04 bound. One
`P` + consumer 2 run showed one mesenchymal cell overlapping the sheet footprint at the final MCS of
the 3k twin (0 at 0, 1000 and at 10k): a single-snapshot flicker of the kind the FPP links were added
for, noted for the Phase 5 Tier 1 check rather than acted on.

Also added: `lumen_P_mean` as a third CSV column; a `WS` floor of 1e-6 below which the `P` sources
write nothing (the sigmoid `WS` is ~1e-38, not 0, between pulses); the H5 `P`-analogue defined as
the run mean of `WS · (n_h + 2 n_d) / n_epi` (≈ 0.139 at the attractor), the epithelial-state
readout A17 asked for, available in off runs too.

**Phase 3 status (2026-11-02).** MMP field built as in §3 (details and the twin table in
`lab-notebook/2026/2026-11-02.md`, "Evening: Gate B′ Phase 3"). Constants are the 10-30 pins, not
the §5 placeholders: λ_MMP = 10 µm = 8 px with decay 0.01 /MCS, so D = 0.64 px²/MCS (the §5 row said
"as `G`", 0.10); `MMP_0` = 3.08 derived like `P_H` (band mean 1 at the attractor, uniform-field
approximation, against the sheet-level `P` = 1.6 the Phase 2 consumers are normalized to); `K_MMP` = 1;
`TIMP_RATE` = 0.1 · `MMP_0`; `K_C_MMP` = 0.001 behind its own `C_MMP_DECAY_ENABLED` (on by default
when the MMP switch is on), run every 10 MCS with the rate × 10 (`C_MMP_DECAY_PERIOD_MCS`; the
per-MCS loop measured 57 s per 3k MCS in-process, more than the MMP source loop's 45 s, so the §7
fallback applies; numbers in the notebook). Regression: switches off reproduces the reference exactly; MMP on with the `C` term off is
identical to off on every B4 column (no consumer until the `C` term or Phase 4). Three things to
know before Phase 4:

- *The field is peaked under the sheet, as λ = 8 px implies, and the uniform-field target is
  crude for it.* At 3k MCS (seed 200): band mean 0.68 against the design 1.0, sheet-level value at
  the source pixels 6.2–6.3, domain max ≈ 11, lumen mean 0.74, and it falls off as e^(−d/8 px) into
  the band. **`MMP_thr` is expressed against the band mean** (§5 as written); at that threshold ECM
  removal happens only within ≈ 18 px (≈ 2 λ ln(sheet/band)) of the sheet, i.e. where ECM cells
  placed next to sheet-pressing myofibroblasts will sit, and nowhere deeper. If removal should reach
  deeper, the threshold has to be set against the field at the ECM cells' own positions, not the
  band mean — a Phase 4 decision, flagged for Marcella. *Decided 2026-11-04: no threshold at all;
  removal is rate-based (§6 item 8).*
- *"Highest under damaged cells" does not hold as a mean comparison, and cannot at λ_P = 40 px.*
  MMP under the three damaged cells 6.22 vs 6.34 under the 22 healthy ones. The MMP source reads
  `P_local` at the cell's COM, and the 11-01 literature pass already said that at this range the 2:1
  damaged:healthy `P` contrast survives only as a band-scale difference (measured: a damaged cell
  sits 0.03–0.06 above its healthy neighbours on a `P_local` of 1.2–1.5, ≈ +3 % in the MMP source;
  the per-cell MMP spread from source-pixel geometry is 5.2–10.8, and the three edge cells with 2–3
  source pixels are what lift the healthy mean above the damaged one). So the MMP map follows the
  sheet, not the damage pattern; what makes it "epithelium-localized" (Zou 2014) is the source
  geometry, and what would make it damage-localized is a shorter λ_P (the 25 µm scan arm) or an
  explicit damaged-cell MMP factor like `G`'s 10:1 (A19b), which the plan deliberately does not have.
  Reported, not fixed: criterion 3 has no MMP-under-damaged check, and Gate D's focal-vs-diffuse
  question is exactly whether the damage pattern reaches the matrix.
- *"Lowered at myofibroblast COMs" holds locally, not against the band mean.* The field at
  myofibroblast COMs (0.98 at 3k) is above the band mean because myofibroblasts press against the
  sheet where MMP is 3–10× the band mean; the TIMP sink shows as a dip at the COM pixel against its
  four neighbours (per-myofibroblast table at the end of the log: 0.32 = `TIMP_RATE` at the 5
  myofibroblasts near the sheet, against neighbours 2.2–3.6), and the clamp at 0 means the 8 deep in
  the band remove nothing (2335 units removed over 3k MCS against ≈ 5100 nominal). The CSV column
  stays the plan's `mean_MMP_at_myof_com`; the dip is the readable check.

The `C` term, on (seed 200, 3k, vs the MMP-only twin): band `C` 0.626 → 0.192 (−69 %), because `C` is
deposited exactly where MMP peaks (myofibroblasts on contact near the sheet, the epithelial basal
pixels) and there `k_C,mmp · MMP` is 12–22× the base decay; lumen −1.05 → −0.97 %; myofibroblasts 13 →
11 (fibroblasts 11 → 13), `G` 0.472 → 0.429, divisions 9 → 9; Tier 1 clean. One seed, so the
population differences are RNG divergence through the changed mechanics (`c_norm` feeds λ_volume and
the myofibroblast `targetVolume`), not a direction result. Whether the term stays on in the rebaseline
is a Phase 4 question (if ECM cells carry the matrix, MMP removal of ECM cells is the loop and the `C`
term may double-count); recommendation: keep it on, since `C` remains the stiffness signal.

## 5. Parameters and constants B′ introduces or touches

Status: **inherit** (no new freedom, from the ODE or existing values), **pin** (literature can set
it now; candidate for a separate calibration chat), **assay** (Jones lab, later; placeholder until
then), **free** (stated as scanned). "Blocks" says whether the rebaseline should wait for it.

| Parameter                                             | Role                                              | Build placeholder                                                                                              | Pinned by                                                                                                                                 | Status                     | Blocks rebaseline? |
| ----------------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ------------------ |
| `p_h`                                                 | healthy exposed epithelium `P` rate               | set so the `P` band mean at the ODE attractor ≈ 1 (dimensionless, like `G`)                                    | IL-6 fold-change under smoke extract (Jones assay 1); only sets the field's scale, so `k_P`, `k_prolif`, `k_mmp` are expressed against it | assay                      | No                 |
| damaged : healthy `P` ratio                           | A19a                                              | 2 : 1                                                                                                          | ODE `e6/e5`                                                                                                                               | inherit                    | —                  |
| `k_M1`                                                | `S_M1` pedestal                                   | `p_h · (m6/e5) · Hill(A)`                                                                                      | ODE `m6`, `Hm3`, `nm3`                                                                                                                    | inherit                    | —                  |
| `P` diffusion                                         | field                                             | 0.10 px²/MCS (same as `G`, placeholder)                                                                        | IL-6 D in tissue (~ 1e-6 cm²/s class) → px²/MCS at 1.25 µm/px, 62.4 s/MCS; diffusion length √(D/k) of a few cell widths                   | **pin**                    | Yes                |
| `P` decay                                             | field                                             | ODE `m7` = 0.04 /h → 6.9e-4 /MCS (t½ ≈ 17 h) as the ODE-consistent fallback                                    | IL-6 half-life in tissue/medium (literature; Jones assay 1 time course)                                                                   | **pin** (fallback inherit) | Yes                |
| `k_P`                                                 | repair gating                                     | 1.0 (halves repair at `P` = 1)                                                                                 | IL-6 effect on epithelial barrier/repair rate (literature)                                                                                | **pin**                    | Yes                |
| `k_prolif`                                            | mitosis gate                                      | 0.5 · threshold / 1 (so `P` = 1 alone meets half the gate)                                                     | IL-6 fold-increase in lung fibroblast proliferation (literature; Jones assay 4)                                                           | **pin** / assay            | Yes                |
| `mmp_0`, `k_mmp`                                      | epithelial MMP source                             | chosen so MMP band mean ≈ 1 at the attractor; `k_mmp` = 1                                                      | MMP-2/-9 fold-change under smoke extract and IL-6 (Zou 2014 qualitative; Jones assay 3)                                                   | **pin** (fold) / assay     | No                 |
| MMP diffusion, decay                                  | field                                             | as `G` (0.10, 0.01)                                                                                            | MMP-9 (92 kDa) D; MMP half-life in matrix                                                                                                 | **pin**                    | Yes                |
| `timp_rate`                                           | TIMP subtraction                                  | 0.1 · `mmp_0` per myofibroblast per MCS                                                                        | TIMP-1 : MMP-9 ratio (Zou 2014 raised both; Jones assay 3)                                                                                | **pin** (ratio) / assay    | No                 |
| `MMP_thr`                                             | ECM removal                                       | the MMP band mean at the attractor with all on (so removal happens where MMP is above average)                 | none; Chandrasegaran's rule                                                                                                               | free                       | No (scanned in D)  |
| `k_C,mmp`                                             | `C` decay term                                    | 0.001                                                                                                          | collagen turnover under MMP induction                                                                                                     | **pin** (weak)             | No                 |
| `ECM_QUANTUM`                                         | px per ECM cell placed                            | 36 px (6 × 6); `ECM_BUDGET_INCREMENT` = 0.01 → one cell per 3,600 MCS of contact (§6 item 10; was 0.08)        | PICP per myofibroblast per day (Jones assay 2 for the fibroblast : myofibroblast ratio; absolute stays free)                              | assay / free               | No, but see §6     |
| ECM cell size                                         | TypeId 6 target volume                            | 36 px = 7.5 µm square                                                                                          | Chandrasegaran 7 µm; collagen bundle scale                                                                                                | inherit (borrowed)         | —                  |
| ECM contact energies, λ_volume, fluctuation amplitude | mechanics                                         | §3 values                                                                                                      | this model's J scale; verified by smoke run, not by literature                                                                            | free, stated               | No                 |
| placement bias β                                      | toward-sheet weight                               | 0.2 /px                                                                                                        | none                                                                                                                                      | free                       | No                 |
| `MYOF_TARGET_VOLUME_GROWTH_FACTOR_WITH_ECM`           | myofibroblast swelling once matrix carries volume | 0.0                                                                                                            | design (matrix is the volume now)                                                                                                         | design (§6)                | —                  |
| activation rate (existing, known wrong)               | `0.02 · G` per MCS                                | keep 0.02 for the regression; `ACTIVATION_RATE_PER_MCS` parameterised                                          | 1–3 days to α-SMA+ at saturating TGF-β1 → ~1/(1440–4320 MCS) ≈ 2.3e-4 to 6.9e-4 per MCS of saturating signal (Jones assay 2 time course)  | **pin** now, assay later   | decision (§6)      |
| damaged : healthy `G` ratio (A19b, existing)          | 10 : 1                                            | 10 : 1                                                                                                         | Jones assay 1                                                                                                                             | assay                      | No                 |

**For a separate calibration chat** (the "pin" rows, in the order they block): `P` diffusion and
decay; `k_P`; `k_prolif`; MMP diffusion and decay; the activation rate; then `k_C,mmp`,
`timp_rate` and the MMP fold-change as weaker literature items. Each needs a value in real units
with a citation and the conversion to px²/MCS or /MCS on the tissue clock (1 px = 1.25 µm,
1 MCS = 62.4 s, `HOURS_PER_MCS` = 0.01733). Output goes into `calibration_table.md` as a status
change and into the `parameters.py` Biological section with the cite key.

## 6. Decisions for Marcella before Phase 4

1. **ECM seeding size.** Seed each new ECM cell as one pixel with `targetVolume` 36 and let the
   volume constraint grow it over a few MCS (robust, no overwriting of neighbours), or draw the 6 × 6
   square at once (immediate volume, but it overwrites whatever is there). Recommendation: seed
   small and grow. *Decided 2026-11-04 (Marcella): seed small and ramp.* A new ECM cell is seeded
   on free Medium pixels only (a 2 × 2 patch at the chosen site where four are free, fewer
   otherwise, never overwriting a cell) with `targetVolume` equal to its seeded volume, and the
   target then rises by `ECM_GROWTH_PX_PER_MCS` (first pass 0.5, so full size in ≈ 65 MCS ≈ 1.1 h;
   a free mechanical parameter, stated) until `ECM_TARGET_VOLUME` = 36. Not 36 at birth: at
   λ_volume 10 a 1-px cell with target 36 gains 690 per pixel taken, against 22.5 for an
   epithelial cell's first lost pixel (202 for its fifth), so it would fill out in a few MCS from
   whatever touches it, next to the sheet; the "no overwriting of neighbours" above does not hold
   for that form. Under the ramp the drive stays near 10–30, the scale of the contact energies,
   and the long-run pressure on the sheet is unchanged because the final target is still 36. No
   permanent deficit cap (it would stop the matrix from ever pressing on the sheet). The budget
   still drops by `ECM_QUANTUM` at creation, so a seedling deleted by MMP costs a full quantum
   (accepted; continuous deposition, the target tracking the budget, was the alternative considered
   and set aside as more bookkeeping). Caveat recorded: fibroblast mitosis already makes a one-shot
   target jump of similar size and the sheet has survived it, so the unramped form is a Tier 1
   risk, not a certainty; **Phase 4 opens with a 500-MCS scratch comparison of the ramped and
   unramped forms next to the sheet.** Coupled and still open: the `MMP_thr` rule (a seedling near
   the sheet sits at MMP 2–6, above a band-mean threshold of ≈ 0.7, so it would be deleted at birth).
2. **Activation rate.** Fix it in the rebaseline (behind `ACTIVATION_RATE_PER_MCS`, old value kept
   for criterion 1) or leave it until the Jones time course reports. Recommendation: fix it now
   with the literature 1–3 day range, since every B′ rebaseline number depends on how fast the
   mesenchymal pool converts, and rerun once if the assay moves it (the roadmap already allows one
   rerun for assay results). *Decided 2026-11-02: fixed at the start of Phase 5, bundled with item 7
   below as one pre-registered base-model change.*
3. **Myofibroblast `targetVolume` growth with `c_norm`** under ECM cells: 0 (matrix is the
   volume) or a reduced factor (say 0.5). Recommendation: 0, and let the rebaseline show whether
   displacement survives. *Decided 2026-11-04 (Marcella): 0.*
   `MYOF_TARGET_VOLUME_GROWTH_FACTOR_WITH_ECM` = 0.0, so under `ECM_CELLS_ENABLED` a
   myofibroblast keeps `TARGET_VOLUME_MYOF` and matrix volume is carried by ECM cells only; the
   λ_volume stiffening with `c_norm` stays *(amended 2026-11-05 by item 9: `C` itself goes under
   ECM cells, so the stiffening lapses with it)*. The swelling was the stand-in for matrix volume while
   `C` was a field only (its own comment in `parameters.py` says so), so keeping both would count
   the same collagen's volume twice. Size of what is removed (Gate B4, 20k, n = 6): 42–62
   myofibroblasts at mean `c_norm` 0.08–0.20, i.e. ≈ 400–560 px of swelling over the band, ≈ 20 %
   of the occupied band volume and ≈ 1 % of what the ECM budget would deposit over the same run, so
   the choice is about attribution, not magnitude. **Consequence for Gate D:** the ECM switch then
   changes two things (swelling off, matrix on), so one control arm is added to the sensitivity
   list, ECM cells off with the swelling factor also 0 (a base-model variant, not the frozen
   base), to separate the matrix effect on the lumen from the lost swelling. 0.5 set aside (no
   basis, keeps the double count); 2.0 unchanged was the alternative (purely additive switch, no
   control arm needed). **Flagged, not decided:** at B4's myofibroblast numbers the §5 budget
   (`ECM_BUDGET_INCREMENT` = 0.08 px/MCS per myofibroblast in Medium contact) deposits ≈ 60,000 px
   over a 20k run against ≈ 11,600 px of free band, so the band would pack within a few thousand
   MCS of the population appearing; whether that is met by lowering the budget, by doing the item 7
   base-model change before Phase 4, or by letting the Medium-contact condition limit it, waits on
   a scratch run of the new base's myofibroblast count (lab-notebook 2026-11-04). *Resolved
   2026-11-05, item 10: the budget is lowered to 0.01 px/MCS and item 7 stays in Phase 5.*
4. **Placement bias β.** Uniform among adjacent Medium pixels (β = 0) or biased toward the sheet.
   Recommendation: β = 0.2 /px, reported as free; β = 0 as a sensitivity run in Gate D if time.

7. **Myofibroblast `G` secretion back to 0.001 (decided 2026-11-02, Marcella).** The 0.1 set on
   2026-08-11 was a displacement experiment, not a biological claim (A14), and it saturates every
   `G` gate: band `G` sits at 1.5–1.7 against thresholds of 0.225 (mitosis) and 0.45
   (differentiation), so the lesion is diffuse whatever `S_M2` does and the Phase 2 mitosis gate is
   inert (`p_tipped_gate_frac` 0.3 %). The stiffness-gated autocrine loop (Wipff 2007) has no stiffness
   feedback here, which is why 08-07 kept it low. **How:** at the start of Phase 5, before any
   criterion run, (i) move the four `G` secretion literals out of the XML `<SecretionData>` into
   `parameters.py` (Model section, each with its calibration-table row) so they are tracked like
   everything else; (ii) set the myofibroblast rate to 0.001 and the activation rate to the
   literature value (item 2; `ACTIVATION_RATE_PER_MCS`, 7.2e-4 per MCS of saturating signal divided
   by the `G` that means saturating TGF-β1, see `calibration_table.md`); (iii) record a **new
   criterion-1 reference**: the switches-off n = 6 PSCAN at the new base, replacing B4 as the exact-
   regression target (B4 stays the historical comparison point; the Gate B finding about initial
   occupancy is unaffected); (iv) then criteria 2–4 as written. Phases 3 and 4 keep building against
   the current reference (`results/cc3d/bprime-ref-3k-seed200/`, local), since their smoke tests are
   about field and cell-type mechanics. 0.1 becomes a Gate D sensitivity arm. Unknown until run: the
   effect size at the current geometry (no 0.001 run exists since the 09-17 rescale; pre-rescale the
   `G` mean sat near 0.02, two orders below the gates), so Phase 5 starts with a 3k seed-200 smoke at
   the new base to see conversions, `C` and the tipped-gate fraction before the n = 6 reference run.
   *Run 2026-11-05 (scratch, seed 200, 20k; item 10): the change as written raises the
   myofibroblast count (350 against 59) and needs a proliferation limit decided with it.*

8. **ECM removal rule: rate-based, not a threshold (decided 2026-11-04, Marcella).** A departure
   from the §3 design text and from the borrowed Chandrasegaran threshold rule; the §2 criteria are
   untouched (criterion 3 asks only that MMP lowers the final ECM-cell count vs ECM-only). **Rule:**
   each ECM cell is removed (`delete_cell`, pixels to Medium, counted in the CSV) with probability
   `K_ECM_MMP · MMP_local` per MCS, `MMP_local` read at its COM; the cell-based twin of the Phase 3
   `C` term (`K_C_MMP · MMP · C` per pixel), first-order in MMP. One `random` draw per ECM cell per
   MCS, made only when `ECM_CELLS_ENABLED` and `MMP_FIELD_ENABLED` are both on, so the off-switch
   rule holds. **Why not `MMP_thr`:** the Phase 3 field spans three decades between the sheet and
   the deep band (≈ 5.8 · e^(−d/8 px) below the sheet; 1.8–3.6 at the five sheet-adjacent
   myofibroblasts, 0.000–0.005 at the eight deep ones, seed 200, 3k), so a threshold at the band
   mean (0.7) deletes every ECM cell within ≈ 17 px of the sheet at birth and never removes one
   deeper. That (i) forbids matrix exactly where subepithelial fibrosis is defined and where it
   must accumulate to press on the sheet, (ii) makes the Gate D scan of `MMP_thr` a plateau
   (identical outcome for any value from ≈ 0.005 to ≈ 1.8) followed by a cliff, and (iii) leaves a
   knife edge that drifts as the field rises with `P`; a threshold at the sheet-level value only
   moves the knife edge. **Placeholder:** `K_ECM_MMP` = 1e-4, a mean ECM lifetime of ≈ 3,300 MCS
   (2.4 days) at MMP = 3; with one cell deposited per 450 MCS of contact that settles near 7 ECM
   cells per sheet-adjacent myofibroblast (*about 0.9 at the 2026-11-05 budget, one cell per 3,600
   MCS; item 10*), and a ramping seedling (item 1) survives its ≈ 65 MCS of
   growth with probability ≈ 0.98. Not `K_C_MMP`'s 0.001: a 330-MCS lifetime is shorter than the
   deposition interval, so matrix would again not accumulate under the sheet. Free, stated; **the
   Gate D scan axis is `K_ECM_MMP` ∈ {0, 3e-5, 1e-4, 3e-4, 1e-3}, replacing the `MMP_thr` scan** of
   the §5 table. Considered and set aside: a deterministic dose rule (each cell accumulates
   `MMP_local` and is removed past a limit; same mean lifetime, no random stream, but synchronized
   removals and a form that does not match the `C` term). Caveat: the near/deep split of
   myofibroblasts is one seed at 3k in the `G`-saturated regime, which item 7 changes; the argument
   rests on the field's steepness, not on that split.

9. **No `C` field under ECM cells (decided 2026-11-05, Marcella).** With matrix carried by ECM
   cells it makes no sense to keep the collagen field beside them: under `ECM_CELLS_ENABLED`
   nothing writes `C` and nothing reads it. Supersedes §3's "`C` kept for stiffness only" and
   amends item 3. With the switch off `C` is the base model's matrix, unchanged (criterion 1).
   What the decision removes under the switch, from the code as of `a05a95c`:
   - *Sources:* the XML `SecretionOnContact` (myofibroblast on Medium, 0.08) and the Python-side
     epithelial basal secretion (0.01 per wall-side pixel).
   - *Consumers:* myofibroblast λ_volume = 12 · (1 + 2 `c_norm`) (mean `c_norm` 0.08–0.20 in Gate B4,
     so λ ≈ 14–17 against a base 12; ≈ 31 at the maximum); the myofibroblast `targetVolume` growth
     (already 0, item 3); the fibroblast λ_volume factor (1 + `c_norm`), which in the current code
     is live only for dividing fibroblasts, since `activate_fibroblast` overwrites it with
     1 + activation progress in the same MCS for every other fibroblast (a base-model quirk,
     noted, not changed); and the Phase 3 `C` MMP-decay term.
   - *Readouts:* `mean_C_subepithelial`, `lumen_C_max` and the `c_norm` diagnostics read 0 under
     the switch. Tier 1's "no `C` in the lumen" is carried by "no ECM cell in the lumen"
     (criterion 2 already lists both).

   Follows from it, *proposed 2026-11-05 and to be confirmed by Marcella*: (a) **no replacement
   stiffening**: real ECM cells obstruct their neighbours mechanically, which is what the λ proxy
   stood in for, the same logic as item 3 (the alternative would be λ_volume scaled by the share
   of a cell's boundary in contact with ECM cells); (b) **the epithelial matrix output lapses**
   under the switch: only myofibroblasts have an ECM budget (it was 0.01 against their 0.08, and
   the reticular basement membrane is a v2 item). Closed by the decision: whether the `C` term
   stays on with ECM cells (nothing is left for it to act on). The term stays for Gate D's
   MMP-without-ECM condition, where it is MMP's only consumer.

   *Implementation, Phase 4:* the myofibroblast source is an XML literal that a Python switch
   cannot remove on its own. Preferred: give that element an id and set its value to 0 at
   `start()` under the switch (CC3D XML steering), so `C` is identically zero like `P` and `MMP`
   when they are off, and check with the off twin that the id alone changes nothing; fallback:
   leave the field running and unread (no effect on the dynamics, one unused field). Whether
   solver secretion constants can be steered in 4.9.0 is to be checked in a scratch project.
   *Gate D:* matrix is then measured in different units across conditions, the `C` band mean
   without ECM cells and the ECM pixel fraction with them, so cross-condition matrix comparisons
   are ordinal, or use the spatial statistic on each condition's own measure. *Phase 6:* A14's
   text ("non-diffusing accumulator field", the B′ note on `c_norm`) and the `ECM_CELLS_ENABLED`
   comment in `parameters.py` ("C kept for stiffness only") need this recorded.

10. **Item 7 stays in Phase 5; `ECM_BUDGET_INCREMENT` = 0.01 px/MCS for Phase 4 (decided
   2026-11-05, Marcella).** The question from item 3's flag: at B4's myofibroblast counts the
   0.08 px/MCS budget deposits several times the band's free space, so either the producers are
   cut first (item 7 moved ahead of Phase 4) or the budget is lowered. **Evidence** (scratch
   copies, seed 200, 20k MCS, all switches off, committed base untouched; lab-notebook
   2026-11-05, logs in `results/cc3d/scratch-newbase-seed200-20k/`): with myofibroblast `G`
   secretion at 0.001 the model makes 13 / 84 / 350 myofibroblasts at 5k / 10k / 20k against
   26 / 47 / 59 on the current base. Band `G` stays at 0.19–0.31 and never reaches the 0.45
   activation gate, so the fibroblast pool is never used up and keeps dividing (393 divisions
   against 28; band 96.5 % cells by 20k, lumen −8.6 %). With the activation rate also at the
   literature value (7.2e-4, `G_sat` = 1.0 assumed) it is worse: 629 fibroblasts and no lumen
   from MCS 7,400. One seed per condition; the direction does not need replicates, the counts
   are not a reference.
   - **Timing.** The item 7 base-model change stays at the start of Phase 5, as pre-registered
     on 2026-11-02. Moving it ahead would give more producers, not fewer, and a band that fills
     with cells before any matrix exists is not a usable criterion-1 reference. Phases 3 and 4
     keep the current base (42–62 myofibroblasts in B4, capped by ≈ 6k, band 15 % occupied).
   - **Budget.** `ECM_BUDGET_INCREMENT` = 0.01 px/MCS per myofibroblast in Medium contact (was
     0.08 in §5): one 36-px ECM cell per 3,600 MCS ≈ 2.6 days of contact. On the six B4
     replicates (522,200–835,300 myofibroblast-MCS over 20k) that is nominally 5,200–8,400 px,
     45–72 % of the ≈ 11,600 px free band; 0.014–0.022 would nominally fill it, and 0.08 gave
     3.6–5.8×. Nominal because the budget accrues only on Medium contact and MMP removes ECM
     near the sheet. First pass, free, stated; a candidate Gate D sensitivity axis (values to be
     set with the Gate D list). Enters `parameters.py` in Phase 4.
   - **Consequence for item 8, flagged, not decided.** The `K_ECM_MMP` placeholder (1e-4) was
     sized against one cell per 450 MCS, about 7 ECM cells per sheet-adjacent myofibroblast at
     steady state. At one cell per 3,600 MCS the same lifetime (≈ 3,300 MCS at MMP = 3) gives
     about 0.9, so next to the sheet removal roughly balances deposition; the scan value 3e-5
     gives about 3. The Phase 4 smoke run will show whether matrix accumulates under the sheet
     at 1e-4; the placeholder is revisited there, not now.
   - **Raised for Phase 5, open.** Item 7 as written removes the model's only brake on
     fibroblast proliferation: on the current base the saturating `G` converts the whole pool
     by ≈ 6k and myofibroblasts do not divide, while the 0.225 mitosis gate is always open
     (every fibroblast reads local `G` 0.27–0.48 from its own and its neighbours' secretion).
     It needs a proliferation limit decided with it (candidates, none built or tested: contact
     inhibition on the mitosis clock; the two gates rethought together; lower fibroblast `G`
     secretion), plus `G_sat` for the activation-rate fix; and at 0.001 a myofibroblast
     secretes less `G` per pixel than a fibroblast (0.005). Biology to choose, with a
     literature check, before Phase 5.

## 7. Risks

- **ECM cells destabilise the sheet or fill the lumen band.** Mitigated by its own switch, the
  no-placement-above-footprint rule, and the Phase 4 smoke run before anything long.
- **RNG drift breaks criterion 1.** Any `random` call behind an off switch shifts every later
  draw. The rule in §3 and the Phase 0 diff script catch it immediately.
- **Wall time.** Three per-pixel loops per MCS instead of one; measured in Phase 1. If a 20k run
  goes past ~90 min, move the pedestals to every 10 MCS with the rate scaled ×10 (Module 8.2:
  frequency and rate are coupled).
- **Two clocks.** `WS` pulses every 24 MCS; `P` decay on the tissue clock smooths them. State it;
  do not reconcile it in B′.
- **Borrowed energies.** Chandrasegaran's contact values are on their J scale; copying them
  unchanged would make matrix either invisible or impenetrable here. Hence the §3 first-pass values
  and the smoke-run check, not a literature pin.
