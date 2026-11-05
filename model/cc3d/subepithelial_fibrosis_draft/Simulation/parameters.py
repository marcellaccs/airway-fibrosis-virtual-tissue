"""
Subepithelial Fibrosis model -- parameters.

Biological / Model / Conversion split per CC3D Workshop Module 8.2 ("Best Practices for
Parameters and Layouts", Sluka -- cc3d expertise/Module Slides/Module 8.2 ...). Import as
`import parameters as p` from Subepithelial_FibrosisSteppables.py rather than duplicating
values across files.

  BIOLOGICAL  -- real-world quantities as reported in the literature, in real units
                 (um, hours, ...), each with a citation. Not directly consumed by CC3D.
  MODEL       -- the actual lattice-space constants CC3D consumes (px, MCS, dimensionless
                 energies/lambdas), each with a note on where the value comes from
                 (a Biological quantity via Conversion, a prior working value, or
                 "arbitrary/uncalibrated" when no literature anchor exists -- A19's own
                 convention for this repo when a ratio genuinely has none).
  CONVERSION  -- the lattice<->real-unit factors themselves, computed from the Biological
                 and Model values above rather than hardcoded, so the two can't drift out
                 of sync silently.

Basic units (see docs/model_assumptions_for_slides.md A7, docs/validation_targets.md sec 7,
lab-notebook/2026/2026-09-04.md for the full sourcing):
  1 px  = UM_PER_PX um   (currently 1.25 um/px)
  1 MCS = S_PER_MCS s     (currently 62.4 s/MCS, ~1000-2000 MCS per fibroblast cell cycle)
These are provisional, first-pass calibrations -- see the CONVERSION section below for what
each rests on and its limitations. The ODE (tissue-signal) layer's own MCS-to-hours mapping
(ODE_STEP_SIZE) is independent of these and does not need to agree with them -- see its note.

Scope note: TISSUE_SIGNAL_MODEL (the Antimony/SBML string integrated by ODESignalSteppable)
is intentionally NOT moved here. It is a self-contained sub-model with its own densely
commented internal rate constants (e1, e2, m1, ... -- one comment per line already, copied
verbatim from the published notebook per docs/ode_tissue_coupling_options.md), not simple
CPM/tissue-layer scalars, and moving a 100-line model definition away from the steppable that
uses it would cost more readability than the Module 8.2 convention buys back. It stays in
Subepithelial_FibrosisSteppables.py.
"""

# ================================================================
# BIOLOGICAL -- literature-cited real-world quantities
# ================================================================

# Airway epithelial cell width. Three sources converge on ~9-11 um for small-airway
# (simple cuboidal, Plopper2020) epithelium: Devalia1990 10.2+-1.0 um (human bronchial,
# cultured, planimetry); Mariassy1984 9.3 um (Clara/secretory cell, sheep tracheobronchial,
# TEM), within a 9.3-21.2 um within-epithelium range. 10 um taken as the working value.
# docs/model_assumptions_for_slides.md A7 (2026-09-04 update); docs/validation_targets.md
# sec 7.
EPITHELIAL_CELL_WIDTH_UM = 10.0

# Fibroblast migration speed, primary human lung fibroblasts on image-based collagen
# scaffolds (Tisler et al., 2020, Fig. 3B *(verify)* -- read off a figure, not tabulated;
# see docs/citation_todo.md). Two conditions reported; BASELINE is the one actually used
# in S_PER_MCS below (CONSERVATIVE is kept for the record and for reviewers, not consumed).
#
# Anchor choice, decided 2026-09-06: IPF-cell-on-IPF-matrix (BASELINE). This model's
# fibroblasts are undergoing active wood-smoke/PM2.5-driven fibrotic conversion, not sitting
# at an uninjured baseline, which leans (weakly -- see LIMITATION) toward the IPF condition
# being the more representative population.
#
# LIMITATION for reviewers: Tisler2020 is an IPF cohort; this model's exposure is
# wood-smoke/biomass/PM2.5, a different etiology. No biomass/wood-smoke-specific fibroblast
# migration figure was found in the 2026-09-04 literature pass (docs/citation_todo.md logs
# this as an open gap). The CONSERVATIVE (normal/normal) alternative gives S_PER_MCS=109.5,
# which clears the cell-cycle ceiling below by only ~9%; BASELINE gives more margin (62.4)
# and is used here, but the choice is a modeling judgment call, not a settled literature
# value, and should be stated as such in any manuscript or slide that cites it.
FIBROBLAST_MIGRATION_SPEED_UM_PER_H = 10.7          # BASELINE: IPF cell on IPF matrix
FIBROBLAST_MIGRATION_SPEED_UM_PER_H_CONSERVATIVE = 6.1  # normal cell on normal matrix

# Fibroblast doubling time. In-culture doubling time is NOT reduced by fibrotic disease
# (Mio1992: 32.0+-6.0h IPF/UIP vs 33.2+-10.4h control lines, no difference) and is
# LENGTHENED in emphysema (Holz2004: 33.6+-2.8h emphysema vs 24.8+-1.4h control) -- the
# exposure phenotype closest to this model. What IS elevated in vivo is spatially localized
# clonal expansion (Molina et al., 2025), not a faster cycle -- see FIBROBLAST_MITOSIS_G_THRESHOLD
# below, which is the "where/whether" gate this finding argues for. 30h is a round value
# within the cited 25-34h range spanning both control and disease figures.
FIBROBLAST_CYCLE_TIME_H = 30.0

# -- Pro-inflammatory field P: literature pins (Gate B' Phase 1, 2026-10-31) -------------
#
# P is the tissue-layer stand-in for the ODE's scalar P, the IL-6-class pro-inflammatory
# milieu (TISSUE_SIGNAL_MODEL in the steppables; docs/roadmap_revision_2026-10-29.md sec 2.1).
# Pins from the 2026-10-30 Consensus pass: docs/calibration_table.md "B' literature pins",
# docs/evidence_dossier_assumptions.md [55]-[77], lab-notebook/2026/2026-10-30.md (evening).
# None of the sources is wood-smoke specific; all are marked as proxies there.
#
# Diffusion length. The cited quantity is the RANGE of a cytokine in tissue, not D itself:
# free D (~84-128 um^2/s for a 21-26 kDa protein, Young1980, Ross2018) would give lambda > 600 px
# at this decay, a uniform field; what brings the range to cell scale is binding to the matrix
# (Thorne2008, Zhu2024), so the model's D is the binding-dressed value and lambda is what the
# literature pins. For the IL-6/IL-8 class: 80-120 um in vivo (OylerYaniv2017), "a few cell
# diameters" where consumers are dense (Thurley2015), IL-8 immobilised on lung GAGs
# (Frevert2003), ~250 um single-cell ceiling (Francis1997). Range 25-120 um, ceiling 250 um
# (lab-notebook/2026/2026-11-01_lit_diffusion_ranges.md, dossier [55]-[98]).
#
# Build value (decided 2026-11-02, Marcella): the CENTRE of P's own range, 50 um, chosen as a
# reasonable starting point and the middle of the Gate D scan, with NO reference to G's
# diffusion constant -- the two fields are pinned independently (a shared-D rule was considered
# on 11-01 and dropped: same molecular size gives the same free D, but tissue-effective D is
# set by binding, which differs between TGF-beta1 and IL-6/IL-8). History: built 10-31 at
# 100 um (D 4.44), run 11-01 at G's D 0.10 (15 um); both are scan points now.
P_DIFFUSION_LENGTH_UM = 50.0
P_DIFFUSION_LENGTH_UM_SCAN = (25.0, 50.0, 100.0, 120.0)   # Gate D sensitivity axis for P
P_DIFFUSION_LENGTH_UM_CEILING = 250.0                      # Francis1997 single-cell upper bound
# Decay. No airway-tissue IL-6 half-life was found. Plasma t1/2 3 min fast / 55 min slow
# (Castell1988, rat), receptor-mediated internalisation t1/2 15 min (Nesbitt1992). The build
# uses the ODE's own m7 = 0.04 /h (t1/2 ~17 h) on the tissue clock, the ODE-consistent
# fallback the calibration table names; 0.0131 /MCS (the 55 min phase) is the stated
# sensitivity arm and is NOT the build value (D would be 84 px^2/MCS, ~340 solver substeps).
# Read live from the SBML at start() like e4; this constant only catches drift.
ODE_M7_PER_H_REFERENCE = 0.04

# -- MMP field: literature pins (Gate B' Phase 3, 2026-11-02) -----------------------------
#
# MMP is the tissue-layer gelatinase (MMP-2/MMP-9 class) that Zou2014 found raised and
# epithelium-localized under wood smoke, with TIMP-1 raised alongside. Pins from the
# 2026-10-30 Consensus pass (docs/calibration_table.md "B' literature pins"; dossier [55]-[77]).
#
# Diffusion length. As for P, the cited quantity is the RANGE, not D: MMP-9 is a 92 kDa protein
# whose free D (~50 um^2/s, Stokes-Einstein from IgG, an estimate) would give lambda ~ 170 px,
# but MMP-2/-9 diffuse BOUND to collagen fibril surfaces and MMP-9 dimers are immobile
# (Collier2011); macromolecule D is 5-10x lower in collagen-rich tissue (Pluen2001). The field
# is therefore pericellular: lambda_MMP ~ 10 um = 8 px, one epithelial cell width, so MMP acts
# within a cell diameter of the epithelial source (and, in Phase 4, of the ECM cells it
# removes). Stated as free (direction from Collier2011, no measured range); a Gate D axis if
# Phase 4 shows removal is sensitive to it.
MMP_DIFFUSION_LENGTH_UM = 10.0
# Decay. Active MMP-9 auto-cleaves within minutes (Bonadio2023) and TIMP-1 inhibition is fast
# (Vempati2007), but pro-MMP-9 is a stable zymogen (RamosDeSimone1999) and no tissue half-life
# was found in the abstracts, so the field keeps G's 0.01 /MCS (t1/2 72 min, the latent-pool
# end) with TIMP explicit in TIMP_RATE rather than folded into the decay. Model section below.

# ================================================================
# MODEL -- lattice-space constants CC3D actually consumes
# ================================================================

# -- Geometry ------------------------------------------------------

DOMAIN_X = 200
DOMAIN_Y = 100

# Epithelial cell size (px). Defined ahead of the y-bands because the epithelial band's
# height is derived from EPITHELIAL_CELL_HEIGHT below, not hardcoded.
#
# Matches EPITHELIAL_CELL_WIDTH_UM=10um via UM_PER_PX below (10/8=1.25 um/px). Chosen for a
# small-airway cuboidal cell (Plopper2020); see docs/model_assumptions_for_slides.md A7.
EPITHELIAL_CELL_WIDTH = 8
# 8px tall = 10um at 1.25um/px, matching the measured 9.6um Clara-cell height
# (Mariassy1984, 7.7px rounds to 8) and Plopper2020's simple-cuboidal description
# (height ~= width, which 6x8 was not). Decided 2026-09-07 (docs/citation_todo.md);
# applied 2026-09-17 with the Module 8.2 rescale below -- was 6 (48px total).
EPITHELIAL_CELL_HEIGHT = 8

# Layer order flipped 2026-08-11 (cc3d_v1_todo.md Priority 0): CC3D renders y increasing
# upward, so the old low-to-high-y order (Lumen, Epithelium, Subepithelial, OuterBoundary)
# put the frozen wall at the *top* of the Player view and the airway lumen at the *bottom*
# -- backwards from the anatomical picture everyone reads off the slides (lumen at top, wall
# at bottom). New low-to-high-y order: OuterBoundary, Subepithelial, Epithelium, Lumen/Medium
# -- "airway space above the epithelium above the subepithelial space above the frozen outer
# boundary" reads correctly top-to-bottom in the Player.
#
# The lumen band is also halved (40 rows -> 20): at the old size the epithelium had 40 rows
# of headroom to retreat into before any narrowing became a large fraction of the lumen,
# which buried whatever inward displacement Priority 1 produces. The 20 rows freed up go to
# the subepithelial band (50 -> 70), not left unclaimed.
#
# Derived from cell size 2026-09-18 (was hardcoded 74-79, a fixed 6-row band): the epithelial
# band is exactly EPITHELIAL_CELL_HEIGHT rows so cells seed at WIDTH x HEIGHT = their
# targetVolume, and changing the cell height moves the bands instead of silently seeding
# cells under- or over-volume. The lumen (20 rows, y=80-99) is the fixed anchor so the
# lumen-area baseline (4000 px) and the narrowing percentages stay comparable across runs;
# the epithelium sits directly below it and the subepithelial band absorbs the difference
# (70 rows at height 6 -> 68 rows at height 8). Why it matters: with height 6->8 and the band
# left at 6 rows, the 2026-09-17 before/after run seeded cells 16px under target and the
# relaxation into open lumen produced an immediate ~12.5% "narrowing" unrelated to ECM.
LUMEN_ROWS = 20
OUTER_BOUNDARY_Y_MIN = 0
OUTER_BOUNDARY_Y_MAX = 3
LUMEN_MIN_Y = DOMAIN_Y - LUMEN_ROWS                                  # = 80
EPITHELIAL_Y_MAX = LUMEN_MIN_Y - 1                                   # = 79
EPITHELIAL_Y_MIN = EPITHELIAL_Y_MAX - EPITHELIAL_CELL_HEIGHT + 1     # = 72
SUBEPITHELIAL_Y_MIN = OUTER_BOUNDARY_Y_MAX + 1                       # = 4
SUBEPITHELIAL_Y_MAX = EPITHELIAL_Y_MIN - 1                           # = 71

# -- Cell initialization --------------------------------------------

# Re-anchored 80 -> 11 (2026-10-27, Gate B2 of docs/roadmap_revision_2026-10-27.md; todo item
# 5): the 80 was a deliberate 2026-08-11 displacement experiment, not a calibration, and the
# displacement gap is post-paper (ECM cell type, 5th in the v2 ranking). Anchor: Zajicek et al.
# (1992), normal adult hamster bronchus lamina propria, 14.8 +- 0.1 epithelial vs 6.6 +- 0.1
# fibroblasts per 100 um of bronchus, i.e. epithelial : fibroblast ~ 2.2 : 1 (abstract-level,
# SE; docs/validation_targets.md sec 7 anchor (4), docs/model_assumptions_for_slides.md A7).
# Two readings of the same source: MATCH THE RATIO -> 25 epithelial cells / 2.2 ~ 11, or MATCH
# THE LINEAR DENSITY -> 6.6 per 100 um x the 250 um domain ~ 16-17. The ratio is chosen:
# it is dimensionless, so A7's ~0.85-1.25 um/px spread and the 10 um vs ~6.8 um epithelial-
# width tension (validation_targets.md sec 7) cancel out of it, which is exactly why A7 names
# it the most useful anchor; the linear-density reading inherits both. It is also what A18
# allows the model to be compared on (ratios, not absolute densities). Expect LESS early
# narrowing than at 80 (initial subepithelial occupancy drops ~7x) -- the 20k baseline is
# re-measured in Gate B4 for that reason; R_FIB's "roughly doubles the initial pool"
# arithmetic below is correct again at this value.
#
# Provenance: 10 (pre-2026-08-09) -> 80 (2026-08-11: PRIORITY 0's displacement plan found the
# compartment at ~2% occupancy at 10, nowhere near crowding pressure, and bumped it to test a
# denser population; cc3d_v1_todo.md) -> 11 (2026-10-27, above).
FIBROBLAST_INITIAL_NUMBER = 11

# Number of epithelial cells seeded across the sheet (create_epithelium tiles the width).
# Named because the P source scale (P_H, Conversion) converts the ODE's whole-epithelium
# rate e5 into a per-cell rate, so "the whole epithelium" has to be a number.
N_EPITHELIAL_CELLS = DOMAIN_X // EPITHELIAL_CELL_WIDTH          # = 25
N_SUBEPITHELIAL_BAND_PIXELS = DOMAIN_X * (SUBEPITHELIAL_Y_MAX - SUBEPITHELIAL_Y_MIN + 1)  # = 13600
N_DOMAIN_PIXELS = DOMAIN_X * DOMAIN_Y                             # = 20000

# -- Recruitment: R_fib (A15) ---------------------------------------
#
# R_FIB is the per-MCS probability of recruiting one new fibroblast across the outer
# boundary (Bernoulli trial each step -- a good approximation of a Poisson process at this
# low a rate). Kept deliberately very low for this first pass: E[new fibroblasts over a
# 20000-MCS run] = R_FIB * 20000 = 20, i.e. it roughly doubles the initial pool of 10 rather
# than dominating it. A15 exists because subepithelial thickening correlates with fibroblast
# *number*, not only phenotype (Hoshino et al., 1998, rs=0.88) -- deliberately a first cut to
# demonstrate the mechanism is wired correctly before tuning the rate against that target.
R_FIB = 0.001

# Recruits are placed within a band adjacent to the frozen outer boundary (not anywhere in
# the subepithelial compartment), matching A15's "influx across the boundary" framing.
RECRUITMENT_BAND_WIDTH = 5

# GF-biased placement (ode_tissue_coupling_options.md sec 3, Option F.2): candidate sites
# are weighted by local G, not chosen uniformly at random. Epsilon keeps every candidate
# selectable (nonzero weight) before any GF signal exists yet, e.g. at the very start of a run.
RECRUITMENT_G_EPSILON = 1e-3

# -- Epithelial ECM secretion --------------------------------------
#
# Epithelium (healthy and damaged) secretes into field C at its boundary, subepithelial
# side only (y >= SUBEPITHELIAL_Y_MIN): written into the neighboring Medium pixel, not the
# epithelial cell's own pixel, so the deposited ECM occupies lattice space the cell doesn't.
EPITHELIAL_ECM_SECRETION_RATE = 0.01

# -- Normalize C at point of use (cc3d_v1_todo.md Priority 2 / kickoff doc Group 2 task 4) --
#
# C itself stays an unbounded accumulator (A14: burden, not density -- do not clamp the
# field). K_C is the half-saturation constant for C_norm = C/(C+K_C), applied where raw C
# gets mixed into a lambdaVolume scaling or a myofibroblast's targetVolume.
#
# Lowered 160 -> 20 (2026-08-11/12, PRIORITY 0 displacement plan): the old value's own
# comment predicted C_norm would "saturate quickly" on an assumption about Myofibroblast
# secretion that was never actually committed (real rate is 0.08, not 2.0). At the real
# rate, local C tops out around 150-160 by MCS 20000 (domain mean ~5.1-5.2, steady state by
# MCS 5000); C_norm(150)=0.48 at the highest-C myofibroblast in that run -- nowhere near
# saturating. 20 puts the half-saturation point inside the range C actually reaches instead
# of beyond it: C_norm(20)=0.5, C_norm(150)=0.88. Confirmed 2026-09-03 (per-myofibroblast
# c_norm diagnostic) that saturation is NOT what causes the displacement plateau -- see
# cc3d_v1_todo.md PRIORITY 0 plan step 3a.
K_C = 20.0

# -- Mechanical constraints ------------------------------------------

# TARGET_VOLUME_EPITHELIAL 48 -> 64 (2026-09-17, docs/citation_todo.md "Apply the 48 -> 64
# px change"): a real rescale, not the reinterpretation UM_PER_PX went through 2026-09-04 --
# pixel count per cell moves (EPITHELIAL_CELL_HEIGHT 6->8), so Module 8.2's rescale rule
# fires. LAMBDA_VOLUME_EPITHELIAL and LAMBDA_SURFACE_EPITHELIAL below, and the epithelial
# Contact energies in Subepithelial_Fibrosis.xml, are rescaled against this change together --
# see docs/citation_todo.md for the arithmetic. Derived from the cell size (not hardcoded) so
# it always equals the seeded footprint: the seeding band is EPITHELIAL_CELL_HEIGHT rows tall
# (see Geometry above), so cells start exactly at target volume.
TARGET_VOLUME_EPITHELIAL = EPITHELIAL_CELL_WIDTH * EPITHELIAL_CELL_HEIGHT    # = 64
TARGET_VOLUME_FIB = 30
TARGET_VOLUME_MYOF = 30

# Rescaled together with TARGET_VOLUME_EPITHELIAL above (Module 8.2, Sluka):
# LAMBDA_VOLUME_EPITHELIAL = 30 * (V_ref/V_actual) = 30 * (48/64) = 22.5.
LAMBDA_VOLUME_EPITHELIAL = 22.5
LAMBDA_VOLUME_FIB = 8
LAMBDA_VOLUME_MYOF = 12
LAMBDA_VOLUME_AIR = 10
# LAMBDA_SURFACE_EPITHELIAL = 1.0 * (D_ref/D_actual) = 1.0 * sqrt(48/64) = 0.87.
LAMBDA_SURFACE_EPITHELIAL = 0.87

# -- Epithelial cell-cell cohesion, FocalPointPlasticity (2026-08-13) ------------
#
# Passive structural links between neighboring epithelial cells, not an active pulling
# force -- see Subepithelial_Fibrosis.xml's FocalPointPlasticity plugin comment for the
# full rationale (the flickering sheet-breach found in the 2026-08-11/12 K_C=20 displacement
# run). Links are created once, in TissueInitializationSteppable.link_epithelial_neighbors.
#
# TARGET_DISTANCE = EPITHELIAL_CELL_WIDTH: neighboring cells in the same row sit with
# centroids offset by roughly one cell width (Module 7.3 convention). LAMBDA=50: first-pass,
# uncalibrated, same order of magnitude as LAMBDA_VOLUME_EPITHELIAL (30). MAX_DISTANCE=3x
# target: generous slack for normal sheet flex before a link breaks outright.
#
# Confirmed 2026-09-03 (FPP-lambda-off diagnostic) that these links are NOT the primary
# cause of the displacement plateau either -- see cc3d_v1_todo.md PRIORITY 0 plan step 3a.
EPITHELIAL_FPP_LAMBDA = 50.0
EPITHELIAL_FPP_TARGET_DISTANCE = float(EPITHELIAL_CELL_WIDTH)
EPITHELIAL_FPP_MAX_DISTANCE = 3.0 * EPITHELIAL_CELL_WIDTH

# -- C-to-targetVolume coupling (PRIORITY 0 displacement plan, step 3) -----------
#
# The load-bearing fix identified 2026-08-11: lambdaVolume scaling on C only stiffens
# myofibroblasts that already exist -- it can't grow the subepithelial compartment's
# footprint. This lets local C also grow a myofibroblast's targetVolume, so the cell
# actually claims more lattice space as burden accumulates locally, not just resists
# compression. 2.0 is a first-pass, uncalibrated choice (up to 3x TARGET_VOLUME_MYOF at
# c_norm -> 1). Confirmed 2026-09-03 that even with this coupling active, the subepithelial
# compartment never gets crowded enough to meaningfully compress the epithelium (volume-
# frustration diagnostic) -- the plateau is a population gap, not a gain problem. See
# cc3d_v1_todo.md PRIORITY 0 item 0 for the resulting decision on fibroblast mitosis vs.
# a v2 volume-occupying ECM cell type.
MYOF_TARGET_VOLUME_GROWTH_FACTOR = 2.0

# -- Biological thresholds -----------------------------------------

FIB_TO_MYOF_G_THRESHOLD = 0.45
# DAMAGE_THRESHOLD/REPAIR_THRESHOLD retired (cc3d_v1_todo.md Priority 2): epithelial damage
# is now gated on the live ODE's f_d, not a hysteresis band on a hardcoded-floor accumulator.

# -- Epithelial repair path (Gate B1, 2026-10-27) ------------------------------------
#
# E_d -> E_h repair for EpitheliumDamaged, the path the ODE has and the tissue layer lacked
# (docs/aoc_platform_impact_2026-10-11.md sec 2A; lab-notebook/2026/2026-10-23.md). The rate
# is the ODE's own e4 (0.002 h^-1, Torres et al. Table 2), READ LIVE from the SBML parameter
# in ODESignalSteppable rather than duplicated here, and converted on the TISSUE clock
# (HOURS_PER_MCS from S_PER_MCS, A7) -- not the ODE layer's ODE_STEP_SIZE. Reason: the ODE's
# attractor values are consumed as quasi-steady constants (A11), and "how long does a given
# damaged cell stay damaged on the lattice" is a tissue-time question, like every other rate
# in this file. Bare e4 at 62.4 s/MCS = 3.47e-5 per MCS per damaged cell (mean damaged
# lifetime ~28,800 MCS, ~21 days); ODE_E4_PER_H_REFERENCE below is a cross-check against the
# live value only (the steppable warns at start() if they differ), never consumed as the rate.
#
# Eq. 16 enhancement CARRIED (decided 2026-10-27, lab-notebook/2026/2026-10-27.md):
# effective rate = e4 * (1 + e8*(M2 + M2R) + e9*A), the Ed' line's numbering (the published
# Eh' line uses e9/e10; docs/ode_tissue_coupling_options.md sec 1 shows f_d is insensitive to
# the mismatch, and Ed' is the line that removes damaged cells). At the attractor (M2_tot
# 0.4464, A 0.950) the factor is ~2.40, i.e. ~8.3e-5 per MCS (~12,000 MCS, ~8.7 days). Why
# carried: the f_d that apply_damage_seeding tracks is itself the ODE's balance of e3*WS
# creation against ENHANCED repair, so a bare-e4 tissue rate would make per-cell damage
# persistence inconsistent with the damaged fraction the same ODE prescribes. The factor is
# spatially uniform (M2 and A are ODE scalars), so it adds no spatial structure -- same
# status as the S_M2 pedestal, and unrelated to the v2 multiplicative gain on cell-based
# secretion (A14), which is about spatial co-location. Set False to run bare e4.
EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT = True
ODE_E4_PER_H_REFERENCE = 0.002

# -- Fibroblast mitosis (cc3d_v1_todo.md "Next session priorities" item 2; decided
#    2026-09-06: build for biological completeness, NOT tuned as a displacement fix --
#    see PRIORITY 0 item 0. Population-level displacement, if it happens at all in v1,
#    is not this rule's job; v2's volume-occupying ECM cell type is prioritized for that.) -
#
# Gates WHERE/WHETHER a fibroblast accumulates cell-cycle progress, not the cycle's rate:
# Molina et al. (2025) found elevated fibroblast proliferation in vivo is spatially
# localized clonal expansion in remodeling regions, not a faster global cycle -- consistent
# with Mio1992/Holz2004 finding no disease-driven speedup of the cycle itself (see
# FIBROBLAST_CYCLE_TIME_H above). No paper supplies a calibrated local-G concentration for
# "remodeling region" in this model's terms, so this is a scanned/uncalibrated parameter,
# same convention A19 already uses for the healthy:damaged secretion ratio when no
# literature anchor exists. Half of FIB_TO_MYOF_G_THRESHOLD: biases mitosis toward the same
# active-signal regions as differentiation, without being identical to that threshold (a
# cell should be able to enter a permissive-for-mitosis region before it's differentiation-
# committed).
FIBROBLAST_MITOSIS_G_THRESHOLD = 0.5 * FIB_TO_MYOF_G_THRESHOLD

# Standard CC3D volume-doubling mitosis: grow targetVolume to 2x, divide once cell.volume
# reaches most of that (not exactly 2x -- lambdaVolume-driven relaxation toward a target
# never converges exactly, so waiting for the literal doubled volume can stall
# indefinitely). 0.9 is standard practice, not a biological parameter.
MITOSIS_GROWTH_TRIGGER_FRACTION = 0.9

# Isolated-fibroblast scratch-run measurement (lab-notebook/2026/2026-09-04.md, continued
# session): mean |delta COM| for a single Fibroblast, no other cells, under this model's own
# Contact/Chemotaxis/diffusion physics (FluctuationAmplitude=10, ChemotaxisByType Lambda=1000,
# field G GlobalDiffusionConstant=0.10/GlobalDecayConstant=0.01, Secretion Type="Fibroblast"=
# 0.005). 5000-MCS run, max excursion 12.65px from start (NoFlux boundary never confined it).
MEASURED_FIBROBLAST_SPEED_PX_PER_MCS = 0.1484

# -- ODE coupling reference values -----------------------------------
#
# M2_TOT_REFERENCE: Route 2 (docs/ode_tissue_coupling_options.md sec 5) no longer uses this
# to drive the model -- kept only as a reference to verify the live SBML integration
# converges to the same attractor value as the precomputed table
# (docs/ode_tissue_coupling_options.md sec 1).
M2_TOT_REFERENCE = 0.4464

# S_M2_COEFFICIENT is a first-pass value, not calibrated. With field G at mean~0.02 against
# FIB_TO_MYOF_G_THRESHOLD=0.45, this coefficient gives S_M2/GlobalDecayConstant(G)=S_M2/0.01
# ~= 0.13 of contribution at quasi-steady-state -- visible against the threshold, not dominant.
S_M2_COEFFICIENT = 0.003

# -- Gate B' switches (2026-10-30; docs/gate_Bprime_plan_2026-10-30.md sec 3) -----------------
#
# The four B' additions (roadmap_revision_2026-10-29.md sec 2) and the three P consumers are
# each behind one switch, ALL OFF until B' closes. Pre-registered criterion 1 (plan sec 2):
# with every switch False the six Gate B4 replicates (seeds 200-205, commit 434bc94,
# results/cc3d/v1-gateB-rebaseline20k/replicates_summary.csv) reproduce EXACTLY, checked by
# model/cc3d/tools/compare_replicates.py. The rule that makes that achievable: code behind
# an off switch makes no `random` draw and writes no field, so the RNG sequence and the
# fields are untouched. The XML may declare the P and MMP fields even when off (a field with
# no sources changes nothing in the Potts dynamics); criterion 1 is what verifies that claim.
#
# Gate D (Jan-Feb 2027) runs the focal-vs-diffuse test as an ablation over these:
# (0) all off, (1) +P repair gating, (2) +P proliferation, (3) +MMP, (4) +ECM cells, (5) all on.
# Every replicates_summary.csv row carries one column per switch so no run is ambiguous.
P_FIELD_ENABLED = False          # spatial pro-inflammatory field P: epithelial sources under
                                 # the live WS (2:1 damaged:healthy, A19a) + uniform S_M1 pedestal
P_GATES_REPAIR = False           # consumer 1: p_repair / (1 + K_P * P_local) per damaged cell
P_DRIVES_PROLIFERATION = False   # consumer 2: mitosis gate reads G_local + K_PROLIF * P_local
MMP_FIELD_ENABLED = False        # MMP field: epithelial source MMP_0 (1 + K_MMP P_local), TIMP
                                 # subtraction at myofibroblast COM, the C MMP-decay term
                                 # (C_MMP_DECAY_ENABLED), rate-based ECM-cell removal (Phase 4)
ECM_CELLS_ENABLED = False        # ECM as a volume-occupying cell type (TypeId 6), budget +
                                 # adjacent placement per myofibroblast, C kept for stiffness only

BPRIME_SWITCHES = (
    "P_FIELD_ENABLED",
    "P_GATES_REPAIR",
    "P_DRIVES_PROLIFERATION",
    "MMP_FIELD_ENABLED",
    "ECM_CELLS_ENABLED",
)


def validate_bprime_switches():
    """Consumers need their field. Raised at import so a misconfigured run never starts:
    a P consumer with P_FIELD_ENABLED False would silently read local_P = 0 and look like
    an off run while claiming to be an on run in the summary CSV."""
    if (P_GATES_REPAIR or P_DRIVES_PROLIFERATION) and not P_FIELD_ENABLED:
        raise ValueError(
            "parameters.py: P_GATES_REPAIR / P_DRIVES_PROLIFERATION require P_FIELD_ENABLED"
        )
    if MMP_FIELD_ENABLED and not P_FIELD_ENABLED:
        raise ValueError(
            "parameters.py: MMP_FIELD_ENABLED requires P_FIELD_ENABLED (the epithelial MMP "
            "source is mmp_0 (1 + k_mmp P_local); run MMP without P by setting k_mmp = 0 "
            "once that parameter exists, not by switching P off)"
        )


# -- P field: model constants (Gate B' Phase 1, 2026-10-31; plan sec 3, A13, A19a) -----------
#
# Sources, all written from Python (FibrosisModelSteppable.secrete_epithelial_P and
# ODESignalSteppable.step), never <SecretionData>: the epithelial source is gated by the live
# WS read from the SBML each MCS and the pedestal by live M1/A, which the XML cannot express.
#   healthy epithelial cell:  P_H * WS            per cell per MCS
#   damaged epithelial cell:  P_H * ratio * WS    per cell per MCS, ratio = e6/e5 = 2 (A19a)
#   S_M1 pedestal (A13):      P_H * (m6/e5) * Hm3^nm3/(A^nm3+Hm3^nm3) * WS * (M1+M1R)
#                             * N_EPITHELIAL_CELLS / N_SUBEPITHELIAL_BAND_PIXELS, per band pixel
# The per-cell amount is split evenly over the cell's Medium neighbours on the subepithelial
# side (same geometry as secrete_epithelial_ecm), so P is written into the wall, not the
# lumen. The pedestal is spread over the SUBEPITHELIAL band only (macrophages sit in the
# lamina propria; adding it to lumen pixels would contradict the plan's "zero in the lumen"
# check). Two factors the plan's k_M1 = p_h (m6/e5) Hill(A) left implicit are made explicit
# here, neither a new freedom: the WS gate (the ODE's P' macrophage term is
# m6*WS*Hill(A)*(M1+M1R), lab-notebook 2026-10-30) and the n_epi/N_band spread that turns a
# per-cell rate into a per-pixel one so the pedestal:epithelium ratio equals the ODE's.
# m6/e5, e6/e5 and the Hill constants are read LIVE from the SBML; the references below only
# catch the Antimony string and this file drifting apart (same pattern as e4).
P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE = 2.0    # e6/e5 = 0.2/0.1 (A19a); live value is used
ODE_M6_OVER_E5_REFERENCE = 2.0                # m6/e5 = 0.2/0.1; live value is used

# P_H is set so the P band mean at the ODE attractor is ~1 (dimensionless, like G; plan
# sec 5 "build placeholder", status assay: Jones assay 1 sets the real scale). Derived in the
# Conversion section from the attractor references below under a uniform-field
# approximation (lambda = 80 px against a 100-row domain, so the field is close to flat;
# the Phase 1 smoke run reports the actual band mean / P_H). References are the hourly
# samples CC3D sees (ODE_STEP_SIZE = 1 h), integrated to t = 3000 h on 2026-10-31:
P_BAND_MEAN_TARGET = 1.0
ODE_WS_MEAN_REFERENCE = 0.125           # three 1 h pulses per 24 h; hourly samples give 0.5, 0.5
ODE_F_D_REFERENCE = 0.1133              # Ed/(Eh+Ed) at the attractor (0.113 in the 10-27 notes)
ODE_WS_HILLA_M1_REFERENCE = 0.01101     # <WS * Hm3^nm3/(A^nm3+Hm3^nm3) * (M1+M1R)> over 24 h

# P diffusion constant: DERIVED in the Conversion section from P_DIFFUSION_LENGTH_UM and the
# decay (D = lambda^2 k), 1.11 px^2/MCS at 50 um. Independent of G's 0.10 by decision
# (2026-11-02); G's own range (10-70 um) is a separate Gate D axis and G cannot change during
# B' anyway, since criterion 1 freezes the base model. For comparison: lambda_P/lambda_G is
# 40/3.2 = 12.5 at these values.

# XML literals for the P field (Subepithelial_Fibrosis.xml cannot read this file). Must equal
# P_DIFFUSION_PX2_PER_MCS / P_DECAY_PER_MCS (Conversion) to within 1%;
# ODESignalSteppable.start() parses the XML and warns if they drift. CC3D 4.9.0's
# DiffusionSolverFE sub-steps automatically when D exceeds its stability limit (verified
# 2026-10-31 in a scratch project: D = 4.44 ran 20 calls/MCS at D/20, decay compounds to
# ~exp(-k) per MCS; <ExtraTimesPerMCS> is ignored), so a scan value needs no XML change
# beyond the constant itself (D = 1.11 runs ~5 sub-steps).
P_DIFFUSION_XML = 1.11
P_DECAY_XML = 0.000693

# WS below this is "no exposure" for the P sources. The ODE's WS is a sum of sigmoids
# (WS_STEEPNESS = 20 /h), so between pulses it is ~1e-9 to 1e-70, never exactly 0; without a
# floor the 13,600-pixel pedestal loop ran every MCS to add ~1e-38 per pixel (Phase 1 smoke
# run, 2026-10-31). Mass dropped by the floor is < 1e-6 of a pulse-MCS's source; the hourly
# samples inside a pulse are 0.5, 0.5, far above it.
P_WS_FLOOR = 1e-6

# -- P consumers 1 and 2 (Gate B' Phase 2, 2026-11-02; plan sec 3) -------------------------
#
# Both read cell.dict["local_P"], the field at the cell's COM (read_local_fields), and both
# are behind their switch: off, the code path is the one Gate B4 ran (same random draws, same
# comparisons), so criterion 1 holds. Normalization (lab-notebook 2026-11-01/02): P_H is set
# by the band mean, but the two consumers read P at different places -- consumer 1 inside the
# sheet (P ~1.7 at lambda = 50 um, 3k MCS, seed 200), consumer 2 where fibroblasts are (band
# ~0.8) -- so K_P is expressed against sheet-level P and K_PROLIF against band-level P.
#
# Consumer 1, repair gating: per damaged cell, p = p_repair / (1 + K_P * P_local), with
# p_repair the ODE-derived per-MCS probability ODESignalSteppable computes (e4 x Eq. 16
# enhancement on the tissue clock). A focus of damaged cells makes P, which keeps the focus
# damaged (positive, local). Seeding still tops the sheet up to f_d, so the global damaged
# fraction stays matched to the ODE; what becomes spatial is where damage sits and how long
# each cell stays damaged. K_P = 1.0 is the plan's placeholder ("halves repair at P = 1");
# at sheet-level P ~1.7 it is a ~2.7x slowdown. Scan {0, 0.5, 1, 2} (calibration table). The
# sign is contested in the literature -- IL-6 alone SPEEDS airway epithelial closure
# (Bequignon2020, Wang2012il6), smoke SLOWS repair (DiVincenzo2022) -- and holds only if P is
# read as the exposure milieu, not IL-6 alone (dossier, 2026-10-30 evening).
K_P = 1.0
# Consumer 2, mitosis gate: mitosis_clock accumulates while
# G_local + K_PROLIF * P_local >= FIBROBLAST_MITOSIS_G_THRESHOLD (IL-6/STAT3 route into the
# mesenchymal pool that bypasses G). Activation (activate_fibroblast) stays on G alone.
# Placeholder: P = 1 alone meets half the gate (plan sec 5), i.e. K_PROLIF = 0.5 x threshold =
# 0.1125; at band-level P ~0.8 that is ~40% of the gate. Literature: IL-1beta-driven ~2x
# mitogenic effect via autocrine IL-6 in lung fibroblasts (Olman2004); IL-6 INHIBITS normal
# lung fibroblast proliferation and is mitogenic only for IPF fibroblasts (Moodley2003) --
# scan including 0.
K_PROLIF = 0.5 * FIBROBLAST_MITOSIS_G_THRESHOLD

# -- MMP field: model constants (Gate B' Phase 3, 2026-11-02; plan sec 3, A14) ---------------
#
# Everything here is behind MMP_FIELD_ENABLED (which requires P_FIELD_ENABLED, above): off,
# no field write, no random draw. Sources and sinks are written from Python, never
# <SecretionData>, because the epithelial source reads the live local_P:
#   every epithelial cell (healthy and damaged alike, no 2:1 -- the exposure enters through
#   P_local, not WS):   MMP_0 * (1 + K_MMP * P_local)   per cell per MCS, split evenly over the
#   same wall-side Medium pixels as the P source (epithelial_wall_source_pixels), every MCS
#   (not WS-gated);
#   every myofibroblast (TIMP, Zou2014 raised TIMP-1 with the gelatinases): subtracts
#   TIMP_RATE from the field at its COM pixel per MCS, clamped at 0;
#   C MMP-decay term (optional, plan sec 3): on every subepithelial-band pixel C loses
#   K_C_MMP * MMP_local * C per MCS; the XML keeps C's 0.0005 base decay.
# Consumer 3 of P (the plan's name for the MMP source's P dependence) is the K_MMP term.
#
# K_MMP = 1: at the epithelial source the MMP output is (1 + P_local) x baseline, i.e. ~2.6x at
# the sheet-level P ~1.6 of the Phase 2 runs. Plan sec 5 placeholder, pinned later by the
# MMP-2/-9 fold-change under IL-6 / smoke extract (Zou2014 qualitative; Jones assay 3).
K_MMP = 1.0
# MMP_0 is set so the MMP band mean at the ODE attractor is ~1 (dimensionless, like G and P),
# derived in the Conversion section the way P_H is: uniform-field approximation,
#   band mean ~ S_total / (k_MMP * N_DOMAIN_PIXELS),  S_total = MMP_0 * n_epi * (1 + K_MMP * <P_local>).
# <P_local> at an epithelial cell's COM is P_LOCAL_EPITHELIAL_REFERENCE, the sheet-level P the
# Phase 2 consumers were normalized against (1.57 at a damaged cell, 3k MCS, seed 200,
# lambda_P = 50 um; the steady-state value is ~15% higher, so the attractor band mean lands
# ~8% under the target -- inside the approximation's own error). NOTE the approximation is
# much cruder here than for P: with lambda_MMP = 8 px against a 68-row band the field is
# strongly peaked under the sheet, so the band mean and the sheet-level value differ by an
# order of magnitude. The Phase 3 smoke run reports both. No removal threshold rests on this
# target: Phase 4's ECM removal was first planned as MMP_thr against the band mean and was
# decided 2026-11-04 to be rate-based instead (probability K_ECM_MMP * local_MMP per ECM cell
# per MCS, plan sec 6 item 8), because a threshold on a field this steep deletes all matrix
# within ~17 px of the sheet and none deeper.
MMP_BAND_MEAN_TARGET = 1.0
P_LOCAL_EPITHELIAL_REFERENCE = 1.6
# MMP decay: a lattice value, kept at G's 0.01 /MCS (t1/2 72 min; see the Biological section
# for why no literature half-life replaces it). The diffusion constant is DERIVED from
# MMP_DIFFUSION_LENGTH_UM and this decay in the Conversion section (D = lambda^2 k = 0.64).
MMP_DECAY_PER_MCS = 0.01
# XML literals for the MMP field, cross-checked against the derived values at start() like
# P's (ODESignalSteppable.check_p_field_constants). D = 0.64 runs ~3 solver sub-steps per MCS.
MMP_DIFFUSION_XML = 0.64
MMP_DECAY_XML = 0.01
# TIMP: each myofibroblast removes TIMP_RATE_FRACTION * MMP_0 per MCS at its COM pixel (plan
# sec 5 placeholder "0.1 * mmp_0"; pinned later by the TIMP-1 : MMP-9 ratio, Jones assay 3).
# TIMP_RATE itself is derived in the Conversion section.
TIMP_RATE_FRACTION = 0.1
# C MMP-decay term: k_C,mmp = 0.001 (plan sec 5, weak literature pin: collagen turnover under
# MMP induction). At the sheet-level MMP of ~10 this is 0.01 /MCS, 20x C's base decay; at the
# band mean of ~1 it equals 2x the base decay; deep in the band (MMP ~0) it is nothing.
# C_MMP_DECAY_ENABLED lets the MMP-only twin run with the term off (it is the only MMP
# consumer until Phase 4's ECM removal, so with it off a MMP-on run must match its off twin on
# every B4 column). Effective only when MMP_FIELD_ENABLED.
# C_MMP_DECAY_PERIOD_MCS: the term is a 13,600-pixel loop like the S_M1 pedestal, so it runs
# every PERIOD MCS with the per-call rate scaled by PERIOD (Module 8.2: steppable frequency and
# rate are coupled). Measured 2026-11-02 (in-process timer, seed 200, 3k MCS): 57 s per 3k at
# PERIOD = 1, i.e. ~6 min on a 20k run and more than the whole MMP source loop (45 s), hence
# PERIOD = 10 (the plan sec 7 fallback). The per-call factor K_C_MMP * MMP * PERIOD must stay
# well below 1: it is ~0.1 at the sheet-level MMP (~11) with PERIOD = 10. PERIOD = 1 is the
# exact per-MCS form if a run needs it.
K_C_MMP = 0.001
C_MMP_DECAY_ENABLED = True
C_MMP_DECAY_PERIOD_MCS = 10

validate_bprime_switches()

# -- Replicates: PSCAN iter_count (Gate B3, 2026-10-27; carried open since 2026-09-04) -----
#
# CC3D's parameter scan (cc3d.core.param_scan) copies the project per iteration and renders
# every .py/.xml in the COPY through Jinja2, so the template expression assigned to
# _ITER_COUNT_TEMPLATE becomes the iteration's value there; in the committed project (and any
# ordinary run) the literal template text survives, int() raises, and ITER_COUNT is None.
# iter_count is Module 8.2's dummy parameter: it changes nothing in the model. It exists to
# get N replicates out of one scan with one combined output file
# (DiagnosticsSteppable.write_replicate_summary -> <scan root>/replicates_summary.csv) and to
# derive one pinned seed per replicate (TissueInitializationSteppable.seed_python_rng):
# seed = REPLICATE_SEED_BASE + iter_count, set on CC3D's generator (Simulator.setRandomSeed)
# and on Python's `random`. An XML <RandomSeed> pin, if present, still wins.
# Spec: Simulation/ParameterScanSpecs.json. Run from the repo root (cc3d_490 env):
#   python -m cc3d.core.param_scan.parameter_scan_run \
#       -i model/cc3d/subepithelial_fibrosis_draft/subepithelial_fibrosis_draft.cc3d \
#       -o results/cc3d/<scan-name> --install-dir .
# Several workers may be started against the same -o; the scan's file lock hands each the
# next untaken iteration.
_ITER_COUNT_TEMPLATE = "{{ iter_count }}"
try:
    ITER_COUNT = int(_ITER_COUNT_TEMPLATE)
except ValueError:
    ITER_COUNT = None
# 200-series, kept distinct from the XML-pinned 101-106 of the 2026-09-26 baseline on purpose.
REPLICATE_SEED_BASE = 200

# ================================================================
# CONVERSION -- lattice <-> real-unit factors, computed (not hardcoded) from the
# Biological and Model values above so the two cannot drift out of sync silently.
# ================================================================

# um/px. See EPITHELIAL_CELL_WIDTH_UM above for the citations behind the 10um figure.
# Reinterpretation, not a rescale: EPITHELIAL_CELL_WIDTH (px) is unchanged, so no
# lambdaVolume/J rescaling follows (Module 8.2's rescaling rule fires on a pixel-count
# change, which this is not).
UM_PER_PX = EPITHELIAL_CELL_WIDTH_UM / EPITHELIAL_CELL_WIDTH  # = 1.25

# s/MCS. See FIBROBLAST_MIGRATION_SPEED_UM_PER_H above for the anchor choice and its
# LIMITATION note (Tisler2020 IPF, not this model's wood-smoke/biomass exposure).
S_PER_MCS = (MEASURED_FIBROBLAST_SPEED_PX_PER_MCS * UM_PER_PX) / (
    FIBROBLAST_MIGRATION_SPEED_UM_PER_H / 3600.0
)  # = 62.4

# Tissue-clock hours per MCS, for rates quoted per hour in the literature or the ODE
# (epithelial repair e4, Gate B1). The ODE layer's own clock is ODE_STEP_SIZE, below.
HOURS_PER_MCS = S_PER_MCS / 3600.0  # = 0.01733

# -- P field, lattice values (Gate B' Phase 1) --------------------------------------------
# Decay on the tissue clock from the ODE's m7 (reference; live value cross-checked at start()).
P_DECAY_PER_MCS = ODE_M7_PER_H_REFERENCE * HOURS_PER_MCS                 # = 6.93e-4 (t1/2 ~1000 MCS)
# Diffusion length in px, and D derived from lambda^2 = D/k (the cited quantity is lambda):
# 40 px and 1.11 px^2/MCS at the 50 um build value. Scan points at this decay: 25 um -> 0.28,
# 50 -> 1.11, 100 -> 4.44, 120 -> 6.39 px^2/MCS.
P_DIFFUSION_LENGTH_PX = P_DIFFUSION_LENGTH_UM / UM_PER_PX                    # = 40
P_DIFFUSION_PX2_PER_MCS = P_DIFFUSION_LENGTH_PX ** 2 * P_DECAY_PER_MCS       # = 1.11
P_DIFFUSION_PX2_PER_MCS_SCAN = tuple(
    (um / UM_PER_PX) ** 2 * P_DECAY_PER_MCS for um in P_DIFFUSION_LENGTH_UM_SCAN)
# P_H: per-cell P output of a healthy exposed epithelial cell per MCS (times WS). Uniform
# steady state: band mean ~ S_total / (k * N_DOMAIN_PIXELS), with
#   S_total = P_H * N_EPITHELIAL_CELLS * [ <WS> (1 + (ratio-1) f_d)  +  (m6/e5) <WS Hill(A) M1_tot> ]
# (healthy + damaged cells, then the pedestal). Solve for P_H at the target band mean. Total
# mass S_total/k does not depend on D; at lambda = 12 px the profile peaks under the sheet
# and less reaches the lumen, so the band mean sits somewhat ABOVE this estimate (the
# 2026-11-01 smoke run measures it).
_P_SOURCE_PER_CELL_UNIT = (
    ODE_WS_MEAN_REFERENCE * (1.0 + (P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE - 1.0) * ODE_F_D_REFERENCE)
    + ODE_M6_OVER_E5_REFERENCE * ODE_WS_HILLA_M1_REFERENCE
)                                                                        # = 0.1612
P_H = (P_BAND_MEAN_TARGET * P_DECAY_PER_MCS * N_DOMAIN_PIXELS
       / (N_EPITHELIAL_CELLS * _P_SOURCE_PER_CELL_UNIT))                 # = 3.44

# -- MMP field, lattice values (Gate B' Phase 3) ------------------------------------------
# Diffusion length in px and D from lambda^2 = D/k: 8 px and 0.64 px^2/MCS at 10 um, k = 0.01.
MMP_DIFFUSION_LENGTH_PX = MMP_DIFFUSION_LENGTH_UM / UM_PER_PX                  # = 8
MMP_DIFFUSION_PX2_PER_MCS = MMP_DIFFUSION_LENGTH_PX ** 2 * MMP_DECAY_PER_MCS   # = 0.64
# MMP_0: baseline MMP output of one epithelial cell per MCS (times 1 + K_MMP * P_local).
# Uniform steady state, as for P_H: band mean ~ S_total / (k * N_DOMAIN_PIXELS) with
# S_total = MMP_0 * n_epi * (1 + K_MMP * <P_local>), solved for MMP_0 at the target band mean.
# No WS factor: the source runs every MCS. Total mass S_total/k does not depend on D; with
# lambda = 8 px most of it sits within ~2 lambda of the sheet (see the Model-section note).
MMP_0 = (MMP_BAND_MEAN_TARGET * MMP_DECAY_PER_MCS * N_DOMAIN_PIXELS
         / (N_EPITHELIAL_CELLS * (1.0 + K_MMP * P_LOCAL_EPITHELIAL_REFERENCE)))   # = 3.08
# TIMP subtraction per myofibroblast per MCS at its COM pixel, clamped at 0 in the steppable.
TIMP_RATE = TIMP_RATE_FRACTION * MMP_0                                          # = 0.308

# Fibroblast cell-cycle length in MCS, from FIBROBLAST_CYCLE_TIME_H via S_PER_MCS.
# Cross-check against Module 8.2's >=1000 MCS/cell-cycle guidance: currently ~1730 MCS, OK.
# If S_PER_MCS's anchor choice above changes, this number moves with it automatically.
FIBROBLAST_CYCLE_MCS = round(FIBROBLAST_CYCLE_TIME_H * 3600.0 / S_PER_MCS)  # = 1730

# ODE_STEP_SIZE: hours of ODE time per MCS, for the ODE (tissue-signal/SBML) layer only.
# A7 does not commit the tissue-mechanics layer (S_PER_MCS above) and the ODE layer to the
# same MCS-to-real-time mapping -- they are read independently. 1.0 (1 MCS = 1h) is the
# simplest choice for this layer; with 20000 MCS that integrates out to t=20000h (~833
# days), well past the ~83 days at which f_d flattens out
# (docs/ode_tissue_coupling_options.md sec 1) -- ample margin, no finer calibration needed
# for this version. NOTE: this is a different number from S_PER_MCS/3600 (~0.017h) -- the
# two layers are deliberately not reconciled yet, see docs/cc3d_v1_todo.md.
ODE_STEP_SIZE = 1.0
