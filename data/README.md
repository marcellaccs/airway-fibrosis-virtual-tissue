# data/

- `raw/` — original, read-only source data (experimental cytokine measurements, etc.).
  **Never edit files here.** Large raw data is gitignored; if a raw file is small and
  shareable, force-add it with `git add -f data/raw/<file>`.
- `processed/` — data derived from raw by scripts/notebooks. Reproducible, so gitignored
  by default.

Document the provenance of every dataset (where it came from, when, how) in your lab-notebook.
