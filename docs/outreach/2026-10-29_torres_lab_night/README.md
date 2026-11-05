# Torres Lab night for undergraduates, 2026-10-29

Materials for the evening presentation to biology/chemistry students: a slide deck, a looping
model animation for the iPads, printable handouts, and the supporting figures. Assembled by Claude
on 2026-10-29; see `lab-notebook/2026/2026-10-29.md` for the session record.

## What is where

| Item | Location | Notes |
|---|---|---|
| Slide deck (18 slides, speaker notes) | https://claude.ai/artifact/QgxMyfqK1DV7jCYgsFPQ11 | Present from the laptop in the browser (Present mode), or Share > Export for a PowerPoint/PDF copy. Private to Marcella's account. |
| PowerPoint copy of the deck (editable, basic fonts) | `The_Torres_Lab_2026-10-29.pptx` in this folder (not in git) | Built with `build_deck.js` (pptxgenjs) from the same content and images as the web deck; present offline from the laptop. |
| iPad page: looping animation + explainer | https://claude.ai/artifact/2x95JCWm2jrXk7tK4Up3qS | Open in Safari on each iPad (signed in to claude.ai). Tap "Hide the explanation" for a bigger video. |
| Animation files | `results/outreach/virtual_airway_14days.mp4`, `results/outreach/virtual_airway_14days.gif` | The GIF loops in the iPad Photos app with no sign-in needed: AirDrop or email it, save to Photos, open. `results/` is gitignored. |
| Handouts (print PDF) | `handouts_2026-10-29.pdf` in this folder | Letter landscape: model schematic (current), target model schematic, proposed-analysis figure with measurements overlaid on a real section and on a model frame, histology plate with credits. |
| Figures used on slides | `figures/` | JTB Fig 1 and Fig 2 (not included in this public copy: publisher copyright; see doi:10.1016/j.jtbi.2025.112159), model schematics rendered from `docs/figures/*.svg`. |
| Histology images | `histology/` + `histology/CREDITS.md` | All CC BY 4.0, CC BY-SA 2.0 or public domain; the credits file has a ready-to-paste attribution line for each. The three Yale Rosen images are CC BY-SA: show unmodified, keep the attribution. |
| Scripts | `make_frames.py`, `make_video.py`, `analysis_fig.py` | Re-render the animation from a CC3D run's `LatticeData/*.vtk` (base Python: numpy, Pillow, imageio-ffmpeg, matplotlib, scipy). |

## The model run behind the animation

- Project copy: `results/cc3d/outreach-anim-project/` = `model/cc3d/subepithelial_fibrosis_draft/` at
  commit `9a0566c` with the `ParameterScan` line removed from the `.cc3d` and `<RandomSeed>202</RandomSeed>`
  added to the Potts block (replicate seed 202 of the Gate B4 scan, which narrowed −4.2 %).
- Run: `python -m cc3d.run_script -i results/cc3d/outreach-anim-project/outreach_anim.cc3d -o results/cc3d/outreach-anim-20k -f 50`
  in `cc3d_490` (CC3D 4.9.0). 401 VTK snapshots, one per 50 MCS, in `results/cc3d/outreach-anim-20k/LatticeData/`.
- Frames: `python make_frames.py <LatticeData> <frames dir> --scale 6`; video: `python make_video.py <frames dir> <out> --fps 15`.

## What is not in git

`histology/*.png|jpg` (re-downloadable from the URLs in `histology/CREDITS.md`) and the large schematic
PNGs in `figures/` (re-rendered from `docs/figures/*.svg` and `docs/virtual_tissue_model_diagram.svg`) are
ignored via the folder's `.gitignore`; they are on this machine only. `animation_frame_stats.csv` is the
per-frame readout table (MCS, day, lumen px and %, cell counts, band means of G and C) from the showcase run.

## Photo credits

- Group photo (June 26, 2025) and classroom presentation photo (June 6, 2025): Marcella's own, from
  `H:\My Drive\Classroom\Intro to Math Modeling in Toxicology\`. Not copied into the repo.
