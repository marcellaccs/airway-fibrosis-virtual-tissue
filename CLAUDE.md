# Working conventions (read me first, every session)

You are my research assistant working in this repository. Follow these conventions.

## Repository map
- `docs/` design docs, status, digitized notes, diagrams.
- `lab-notebook/` dated markdown entries — the research journal.
- `model/cc3d/` CompuCell3D project (steppables `.py`, `.xml`, `parameters.py`).
- `model/ode/` Tellurium notebooks/scripts.
- `data/raw` read-only source data (never edit); `data/processed` derived data.
- `results/` generated outputs (gitignored).
- `literature/references.bib` citations; reading notes in `literature/notes/`.

## Every session
1. Start by reading the most recent file in `lab-notebook/` for context.
2. At the end of the session, write or update today's entry
   `lab-notebook/YYYY/YYYY-MM-DD.md` (copy `lab-notebook/TEMPLATE.md`):
   what we did, decisions made, commands run, results, and next steps.
3. Then do the Notion wrap-up below.

## Task tracking: Notion (added 2026-10-01)
Marcella's task list and progress bars live in Notion ("Command Center" > "Academic HQ").
This repo is the project "Toxicology Virtual Tissue", with sub-projects "CC3D model v1",
"Citations & evidence dossier" and "Write the paper". Sign entries as `Claude`.
- Academic Projects: `collection://<private>`
- Academic Tasks: `collection://<private>`
- Academic Agent Log: `collection://<private>`

The lab notebook stays the detailed record. At the end of a session in Notion:
1. Add ONE Academic Agent Log entry: one-line summary, Project, Local Path = today's
   lab-notebook file, Next Step, Needs (Marcella or Nobody).
2. Check Done on finished tasks; add new tasks (e.g. new `docs/cc3d_v1_todo.md` items or
   open `docs/citation_todo.md` items) to the right sub-project.
3. When you check off an item in `cc3d_v1_todo.md` or `citation_todo.md`, check off the
   matching Notion task too, so the two lists don't drift.
Simulation files and data stay local; never upload them to Notion or Drive.

## Git
- Commit small and often. Messages: present-tense imperative + the why,
  e.g. `add fibroblast cell type to cc3d model` not `changes`.
- Before committing notebooks, **clear all outputs**.
- Commit straight to `main` (solo project); create a branch only for risky experiments.

## Never commit
- Article PDFs (they live in Zotero), anything in `data/raw` that is large,
  `results/`, virtual envs, `__pycache__`, `.sqlite`, secrets/API keys.

## Environments
- **`cc3d`** — CompuCell3D (spatial model). Activate before any CC3D work: `conda activate cc3d`.
- **`tox-ode`** (the env from `environment.yml`) — Tellurium/ODE work. Keep it SEPARATE from
  `cc3d`; installing extra packages into `cc3d` can break libRoadRunner and force a reinstall.
- Environments live in conda's central dir, not the repo, and are not tracked in git.
  Recreate per machine (see `model/cc3d/README.md`).

## CompuCell3D
- Activate first: `conda activate cc3d` (installed per `model/cc3d/README.md`; record the
  version with `python -c "import cc3d; print(cc3d.__version__)"` in the lab-notebook entry).
- Headless run / parameter scans: `python -m cc3d.run_script -i model/cc3d/<project>.cc3d
  --output-dir results/cc3d/<run-name>` (`python -m cc3d.run_script --help` for all flags).
- **Where outputs land — always pass `--output-dir results/…`.** With no `--output-dir`, CC3D
  writes a timestamped `<project>_cc3d_<date>_<hash>/` folder into the *current working
  directory*, so a run from the repo root litters the root and a run from `model/cc3d/` litters
  that. Those names match no `.gitignore` rule, so they show up untracked and get swept into
  `git add`, polluting the record. `results/` is already gitignored; if a bare run is
  unavoidable, add `*_cc3d_*/` to `.gitignore`.
- Interactive: `python -m cc3d.player5` (GUI Player); `python -m cc3d.twedit5` (editor).
- If the Player crashes after moving windows/monitors, delete the `_settings.sqlite` in the
  project's `Simulation/` folder (already gitignored).

## CompuCell3D best practices (from CC3D Workshop Module 8.2, Sluka)
Source: `cc3d expertise/Module Slides/Module 8.2 Best Practices for Parameters and Layouts
Sluka.pptx.pdf`. Apply these by default, not just when debugging a problem they'd have caught.

- **`<Steps>` off-by-one: use N0001, not N0000** (e.g. `20001`, not `20000`). `<Steps>N</Steps>`
  simulates MCS 0 through N-1, so a `finish()`/final-checkpoint steppable keyed to the literal
  step count never fires — this bit us once already (the `finish()`-checkpoint bug, 2026-08-08).
  Run one extra MCS so end-of-run steppables, image saves, and final diagnostics actually run.
- **`NeighborOrder`**: use 2 or 3, not the default 1, unless there's a specific reason not to.
- **Always state the model's basic units, even provisionally.** A multiline docstring/comment at
  the top of the steppables file: 1 pixel = ? µm, 1 MCS = ? (seconds/minutes/hours). State it
  before it's fully calibrated — "provisional, see `docs/model_assumptions_for_slides.md` A7"
  is fine; leaving it unstated is not. If cells divide, cell-cycle time is often the best guide
  to the MCS-to-time mapping (aim for ≥1000 MCS/cell-cycle).
- **Track parameters in one place, not scattered through the code**: a `parameters.py` in
  `Simulation/`, split into Biological / Model / Conversion sections, each parameter carrying
  units and a reference (PMID, "arbitrary", or a doc pointer) — not bare unlabeled constants.
  Import it (`import parameters as p`) rather than duplicating values across files.
- **Keep a biological description alongside the code**: domain/goal, cell types, diffusing
  fields, and processes modeled (`docs/model_assumptions_for_slides.md` / `model_spec_v1_v2.md`
  already serve this role here — keep them current, don't let the code drift ahead of them).
- **Rescaling is not free.** If the pixel/µm ratio or reference cell width changes, adhesion
  energies (`J`) and `lambdaVolume`/`lambdaSurface` must be rescaled against their reference
  values (`J = J_ref * D_ref/D_actual`; `lambdaVolume = lambdaVolume_ref * V_ref/V_actual`;
  `lambdaSurface = lambdaSurface_ref * D_ref/D_actual`) — don't assume old values transfer
  unchanged to a new resolution.
- **Steppable call frequency and rates are coupled.** If a steppable's `frequency` changes (e.g.
  every MCS → every 10 MCS), any per-call rate/increment inside it must scale accordingly, or
  the effective rate silently changes.
- **Use `<RandomSeed>` in the XML (and `random.seed()` in Python, separately, if `random` is
  imported in steppables) when a run needs to be exactly reproducible** — e.g. isolating whether
  a change in output came from a code change vs. stochastic variation. Doesn't work as expected
  with `NumberOfProcessors > 1`.
- **For replicate runs or small parameter sweeps, prefer CC3D's built-in Parameter Scan (PSCAN)**
  over hand-copying the project and running each variant manually — it tracks which parameter
  sets are done, resumes cleanly if interrupted, and (with a log-writing steppable) gives one
  combined output file instead of scattered run logs. A dummy `iter_count`-style parameter with
  no effect on the model is the standard trick for getting N replicates out of a scan.

## Citations
- Add references to `literature/references.bib` (export BibTeX from Zotero). Use the cite key
  in notes and manuscript. Do not paste PDFs into the repo.