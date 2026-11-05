# Toxicology Virtual Tissue Model

> Public snapshot (2026-11-05) of a private working repository. Student names, private
> document links and two publisher-copyright figures have been removed; the commit history
> stays in the private repository.

Spatial CompuCell3D ("virtual tissue") model of the small-airway inflammatory response to
inhaled wood-smoke particulate matter, extending our published ODE model. This repo is also the
**template** for future research projects (see `SETUP.md`).

## What's here

| Path | Contents |
|---|---|
| `docs/` | Project status, digitized design notes, diagrams, research-materials index |
| `lab-notebook/` | Dated markdown lab-notebook entries (your version-controlled research journal) |
| `model/cc3d/` | CompuCell3D project: steppables, XML, parameters |
| `model/ode/` | Tellurium ODE notebooks / scripts (the signal-generating layer) |
| `data/` | `raw/` (read-only source data) and `processed/` — large data is gitignored |
| `results/` | Generated figures/outputs — gitignored (reproducible from code) |
| `literature/` | `references.bib` + reading notes. **PDFs live in Zotero, not here.** |
| `manuscript/` | LaTeX/Overleaf mirror (optional) |

## Quick start

1. Read `docs/2025_project_status.md` first — full project context and next steps.
2. Set up the environment (see below), then run the ODE notebooks in `model/ode/`.
3. Install CompuCell3D separately and open the project in `model/cc3d/`.
4. Every work session: pull, work, commit, push (see `SETUP.md`).

## Environment

Python deps: `pip install -r requirements.txt` (or `conda env create -f environment.yml`).
CompuCell3D is installed separately — see https://compucell3d.org (conda channel `compucell3d`)
or via NanoHub. Record your CC3D version in your lab-notebook entry.

## Conventions

Working conventions for both you and the Claude Code agent are in `CLAUDE.md`.
