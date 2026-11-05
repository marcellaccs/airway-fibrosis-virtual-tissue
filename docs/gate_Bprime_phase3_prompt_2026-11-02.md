# Prompt for the Phase 3 chat (Gate B′, MMP field) — written 2026-11-02

Paste everything below the line into a new Claude Code chat opened in this repository.

---

Begin Phase 3 of `docs/gate_Bprime_plan_2026-10-30.md`: the MMP field. Read `CLAUDE.md`, then
`lab-notebook/2026/2026-11-02.md` and `2026-10-31.md` (Phases 1–2, the decisions, and the twin-run
pattern), the plan's §3 (design), §4 Phase 3 row and §5 (parameters), and the MMP rows of
`docs/calibration_table.md`. Code is in `model/cc3d/subepithelial_fibrosis_draft/Simulation/`
(`parameters.py`, `Subepithelial_Fibrosis.xml`, `Subepithelial_FibrosisSteppables.py`). Environment
`cc3d_490` (CC3D 4.9.0), run with `conda run -n cc3d_490 …`; `conda run` buffers all output until the
run ends.

**What Phase 3 adds (plan §3, all behind `MMP_FIELD_ENABLED`, which already requires `P_FIELD_ENABLED`):**

1. `MMP` as a third `DiffusionSolverFE` field in the XML, declared whether or not the switch is on, no
   `<SecretionData>`, Neumann boundaries like `G`/`C`/`P`. Constants from the calibration table's B′
   pins: pericellular range λ_MMP ≈ 10 µm = 8 px (`Collier2011`), decay 0.01 /MCS (t½ 72 min), so
   D = λ²k = 0.64 px²/MCS. Put them in `parameters.py` the way `P` is done (`P_DIFFUSION_LENGTH_UM`
   stated, D derived in the Conversion section, `*_XML` literals cross-checked at `start()` by
   `ODESignalSteppable.check_p_field_constants`, extend that check).
2. Epithelial source, Python-side (not `<SecretionData>`, it depends on live `local_P`): every
   epithelial cell (healthy and damaged alike, no 2:1) writes `MMP_0 · (1 + K_MMP · P_local)` per MCS
   into its wall-side Medium pixels, reusing `FibrosisModelSteppable.epithelial_p_source_pixels`
   (same geometry and fallback as the `P` source). `K_MMP` = 1. `MMP_0` is set so the MMP band mean at
   the attractor ≈ 1, derived like `P_H` (uniform-field approximation, stated; with λ = 8 px the
   field will be strongly peaked under the sheet, so report the measured band mean and sheet-level
   value and state which one the removal threshold in Phase 4 will be expressed against). Not
   WS-gated: the exposure enters through `P_local`.
3. TIMP: each myofibroblast subtracts `TIMP_RATE` = 0.1 · `MMP_0` from the MMP field at its COM pixel
   each MCS, clamped at 0.
4. `C` MMP-decay term, optional in the plan: `C` loses `K_C_MMP · MMP_local · C` per pixel per MCS
   (`K_C_MMP` = 0.001) on the subepithelial band, the XML keeping its 0.0005 base decay. This is a
   13,600-pixel loop like the `S_M1` pedestal; measure its cost, and if it matters run it every 10
   MCS with the rate ×10 (Module 8.2: frequency and rate are coupled). Put it behind its own constant
   (`C_MMP_DECAY_ENABLED`, default True when the MMP switch is on) so the MMP-only twin can be run
   with it off first.
5. `local_MMP` per cell in `read_local_fields` (0.0 when off); MMP in `print_field_stats` when on;
   CSV columns after the existing `P`/Phase 2 columns and before the switch columns: `mean_MMP_band`,
   `lumen_MMP_mean`, `mean_MMP_at_myof_com` (mean field value at myofibroblast COMs), and
   `mean_MMP_under_damaged` vs `mean_MMP_under_healthy` (field value at each epithelial cell's basal
   source pixels, averaged by type) — those two are the plan's "highest under damaged cells" check.

**Rules that are not negotiable (from the plan and the last three days):**
- Code behind an off switch makes no `random` draw and writes no field. Reads and dict writes are fine.
- ASCII only in every `.py` and `.xml` (the PSCAN templating rewrites files in the Windows codepage).
- Phase 1/2 settled: `P` runs at λ = 50 µm (D = 1.11), pinned independently of `G`; `P_H` is set by the
  band mean; `K_P` = 1.0 against sheet-level `P` (≈ 1.6), `K_PROLIF` = 0.1125 against band-level `P`
  (≈ 0.8). Do not change `G`, `P` or any base-model value: the base model is frozen until Phase 5's
  pre-registered change (plan §6 item 7).
- Steppable order is unchanged (`ODESignalSteppable` → `FibrosisModelSteppable` →
  `FibroblastMitosisSteppable` → `DiagnosticsSteppable`); MMP secretion and TIMP go in
  `FibrosisModelSteppable.step` after `secrete_epithelial_P`.
- A single ad-hoc `rm -rf "$VAR"` is blocked by the harness; use literal paths or `find … -exec rm -r {} +`.
  Bash heredocs containing `'''` fail to parse here; write Python edit scripts with the Write tool and
  run them.

**Verification (the twin pattern; every run at seed 200, 3k MCS, headless, output dir outside the project):**
- Make scratch copies of the project with `<Steps>3001</Steps>` plus `<RandomSeed>200</RandomSeed>`
  in the XML and the `ParameterScan` line removed from the `.cc3d`; set the switches in the copy's
  `parameters.py`; `python -m cc3d.run_script -i <copy>/subepithelial_fibrosis_draft.cc3d -o <out>`.
- **Regression:** the switches-off copy must reproduce `results/cc3d/bprime-ref-3k-seed200/` exactly:
  `python model/cc3d/tools/compare_replicates.py results/cc3d/bprime-ref-3k-seed200/replicates_summary.csv <out>/replicates_summary.csv --key rng_seed`
  (PASS) and `python model/cc3d/tools/compare_run_logs.py results/cc3d/bprime-ref-3k-seed200/run.log <run>.log`
  (IDENTICAL). Declaring the MMP field changes nothing (true for `P`; check it again).
- **MMP on, `C` term off:** must be identical to the off twin on every B4 column (MMP has no consumer
  until the `C` term or Phase 4's ECM removal). MMP quasi-steady in the band (report band mean,
  sheet-level peak, lumen mean, 3k is ~95 % of steady state at k = 0.01), highest under damaged cells
  (`mean_MMP_under_damaged` > `mean_MMP_under_healthy`), lowered at myofibroblast COMs
  (`mean_MMP_at_myof_com` below the band mean once myofibroblasts exist), no NaN, no negative values.
- **MMP on, `C` term on:** B4 columns are now allowed to differ (`c_norm` changes); report lumen %,
  `C` band mean and myofibroblast count against the off twin, Tier 1 (fragmented/isolated/overlap 0,
  `lumen_C_max` 0), and the `C` term's wall-time cost (three runs alone, not concurrent, for a clean number).
- Wall time of the MMP-only run vs off, run alone.

**Record (CLAUDE.md "Every session"):**
- `lab-notebook/2026/<today>.md` from `TEMPLATE.md`: what was built, the derivation of `MMP_0`, the
  twin results table, wall time, decisions, next steps (Phase 4: ECM cell type; plan §6 items 1, 3, 4
  are its open decisions, recommendations stated there).
- `docs/cc3d_v1_todo.md`: check Phase 3 with a done-summary like Phases 1–2. `docs/gate_Bprime_plan_2026-10-30.md`:
  a "Phase 3 status" note after the Phase 2 one. `docs/calibration_table.md`: the MMP rows (`mmp_0`,
  `k_mmp`, MMP diffusion/decay, `timp_rate`, `k_C,mmp`) from "to set" to set, with the values and the
  normalization statement. A13/A14 only if the implementation departs from what they say.
- Commit straight to `main`, small and often, present-tense imperative + the why; stage only the files
  you changed (there may be unrelated uncommitted files in the tree; leave them). End commit messages
  with the attribution line the session gives you.
- Notion wrap-up per `CLAUDE.md`: one Academic Agent Log entry (Project "CC3D model v1", Local Path =
  today's notebook file, Next Step, Needs); check the task "B′ Phase 3: MMP field …" Done in Academic
  Tasks and add a Phase 4 task; update the sub-project's Next Step. Sign as `Claude`.

Report at the end: the three twin results in one table, the regression verdicts, the `MMP_0` value and
what the field looks like (band / sheet / lumen / at myofibroblasts), anything that departed from the
plan text, and the open decisions for Marcella before Phase 4.
