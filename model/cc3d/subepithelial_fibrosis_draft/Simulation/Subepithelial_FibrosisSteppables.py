"""
Subepithelial Fibrosis - Steppables Module
Verified against CC3D 4.9.0

Basic units (provisional first-pass calibration -- see parameters.py CONVERSION section
and docs/model_assumptions_for_slides.md A7 for full sourcing and limitations):
  1 px  = p.UM_PER_PX um   (1.25 um/px, Devalia1990/Mariassy1984/Plopper2020)
  1 MCS = p.S_PER_MCS s     (62.4 s/MCS, isolated-fibroblast measurement anchored to
                             Tisler2020's IPF/IPF migration speed -- see parameters.py
                             for the conservative alternative and its limitations)
  Fibroblast cell cycle: p.FIBROBLAST_CYCLE_MCS (~1730 MCS, >=1000 MCS/cycle per
                             Module 8.2's guidance)
All model constants live in parameters.py (Biological/Model/Conversion split, Module 8.2
convention), imported below as `p`. Not duplicated here.

Gate B (2026-10-27, docs/roadmap_revision_2026-10-27.md sec 5): epithelial repair path
(FibrosisModelSteppable.apply_epithelial_repair, rate from the ODE's e4), initial
fibroblast count re-anchored to Zajicek 1992 (parameters.py), PSCAN replicates with a
dummy iter_count and a per-replicate pinned seed (seed_python_rng), and one combined
replicates_summary.csv per scan (DiagnosticsSteppable.write_replicate_summary).

Gate B' Phase 1 (2026-10-31, docs/gate_Bprime_plan_2026-10-30.md sec 3-4): spatial
pro-inflammatory field P behind p.P_FIELD_ENABLED. Sources written from Python: healthy /
damaged epithelium at p.P_H * WS / p.P_H * (e6/e5) * WS per cell per MCS into the wall-side
Medium pixels (FibrosisModelSteppable.secrete_epithelial_P), plus the uniform S_M1 macrophage
pedestal over the subepithelial band from the live ODE (ODESignalSteppable.step). Readouts:
local_P per cell, mean_P_band / lumen_P_mean / P_analogue_H5 in the summary CSV. No consumer
yet (Phase 2), so a P-on run must match its P-off twin on every B4 column.

Gate B' Phase 3 (2026-11-02, plan sec 3-4): MMP field behind p.MMP_FIELD_ENABLED (which
requires P). Epithelial source p.MMP_0 * (1 + p.K_MMP * local_P) per cell per MCS, every MCS,
healthy and damaged alike, into the same wall-side pixels as P
(FibrosisModelSteppable.secrete_epithelial_MMP); TIMP: each myofibroblast subtracts p.TIMP_RATE
at its COM pixel, clamped at 0 (apply_timp_subtraction); optional C MMP-decay term
K_C_MMP * MMP * C per band pixel (apply_c_mmp_decay, p.C_MMP_DECAY_ENABLED). Readouts: local_MMP
per cell; mean_MMP_band, lumen_MMP_mean, mean_MMP_at_myof_com, mean_MMP_under_damaged /
_healthy in the summary CSV. With the C term off MMP has no consumer until Phase 4's ECM
removal, so that run must match its off twin on every B4 column.

ASCII only, in every .py and .xml of this project (2026-10-27): CC3D 4.9.0's parameter-scan
templating (cc3d.core.param_scan.template_utils) reads each file as UTF-8 through Jinja2 and
rewrites it with a bare open(..., 'w'), i.e. in the Windows locale codepage, so any non-ASCII
byte (the accented Spanish comments this file used to carry) comes back undecodable and the
scan copy fails with a SyntaxError before MCS 0. Transliterated rather than worked around with
PYTHONUTF8, so a scan cannot depend on the environment.
"""
# ================================================================
# IMPORTACIONES
# ================================================================
from cc3d.core.PySteppables import *
import csv
from pathlib import Path
import random
import time
import parameters as p

# Full model, copied verbatim from supplementary.ipynb cell 21 (the canonical
# model per docs/ode_tissue_coupling_options.md sec 1 -- NOT the "balanced"
# version in model/ode/repair_term_check.py, which is a verification
# reimplementation). Inline string, not a separate file: matches both the
# CC3D workshop's taught convention (Module 6.1 "Introduction to Network
# Modeling with Antimony", slides 74-76 -- "This code block just creates a
# string variable called model") and this repo's own working precedent
# (model/cc3d/M1_M2_antimony/Simulation/TelluriumSteppables.py).
#
# Known deviations from the published notebook cell:
#   1. Eh'/Ed' use the published parameter numbering (e8/e9 on Ed', e9/e10 on
#      Eh'), not the "balanced" numbering in repair_term_check.py. The two
#      differ by <2% on Eh+Ed and ~0% on f_d (docs/ode_tissue_coupling_options.md
#      sec 1: "f_d is safe to use as published").
#   2. WS (wood-smoke exposure) is a smooth sigmoid-sum assignment rule, not
#      the original six discrete at-events. The discrete events made CVODE
#      (the default adaptive integrator) fail with CV_CONV_FAILURE at t=32h
#      (the second day's first meal event) -- adaptive implicit solvers
#      handle stiffness well but not genuine discontinuities. Full story,
#      including the exp() overflow trap hit while choosing WS_STEEPNESS, is
#      in docs/tellurium_connection_walkthrough.md.
TISSUE_SIGNAL_MODEL = '''
    // Compartments
    compartment C1;

    // Species
    species Eh in C1; Eh = 1.0;     // Healthy epithelial cells
    species Ed in C1; Ed = 0.0;     // Damaged epithelial cells
    species M1 in C1; M1 = 0.001;    // Recruited M1 macrophages
    species M2 in C1; M2 = 0.001;    // Recruited M2 macrophages
    species M0R in C1; M0R = 0.0;  // Resident M0 macrophages
    species M1R in C1; M1R = 0.0;   // Resident M1 macrophages
    species M2R in C1; M2R = 0.001;   // Resident M2 macrophages, low M2 dominant population
    species P in C1; P = 0.0;       // Pro-inflammatory cytokines
    species A in C1; A = 0.000;     // Anti-inflammatory cytokines

    // Parameters
    e1 = 0.0315;  // Epithelial cell proliferation rate
    e2 = 0.0001;   // Epithelial cell death rate
    e3 = 0.005;   // Healthy epithelial cell damage rate
    e4 = 0.002;   // Damaged epithelial cell repair rate
    e5 = 0.1;     // Healthy epithelial pro-inflammatory cytokine production rate
    e6 = 0.2;     // Damaged epithelial pro-inflammatory cytokine production rate
    He1 = 0.2;    // Hill constant for P production by Eh
    He2 = 0.2;    // Hill constant for P production by Ed
    ne1 = 4;      // Hill coefficient for P production by Eh
    ne2 = 4;      // Hill coefficient for P production by Ed

    m1 = 50;      // M0 to M1 differentiation rate
    m2 = 0.1;     // M0 to M2 differentiation rate
    m4 = 0.02;    // Macrophage decay (death/efflux) rate
    m5 = 0.05;    // M1 to M2 transition rate
    m6 = 0.2;     // M1 pro-inflammatory cytokine production rate
    m7 = 0.04;    // Pro-inflammatory cytokine degradation rate
    m8 = 0.1;     // M2 anti-inflammatory cytokine production rate
    m9 = 0.04;    // M1 anti-inflammatory cytokine production rate
    m10 = 0.04;   // Anti-inflammatory cytokine degradation rate
    Hm1 = 0.25;   // Hill constant for P activation
    Hm2 = 0.05;   // Hill constant for A activation
    Hm3 = 0.9;    // Hill constant for A inhibition
    Hm4 = 1.2;    // Hill constant for A self-inhibition
    nm1 = 2.5;    // Hill coefficient for P activation
    nm2 = 4;      // Hill coefficient for A activation
    nm3 = 2;      // Hill coefficient for A inhibition
    nm4 = 2;      // Hill coefficient for A self-inhibition

    k_c = 0.0125; // Concentration of background anti-inflammatory cytokine

    K = 1;        // Carrying capacity
    WS_STEEPNESS = 20;  // sigmoid steepness (1/h) -- see note by the WS rule below
    m11 = 0.2;    // Direct WS activation rate for M1
    m3 = 0.07;    // Resident macrophage proliferation rate
    smr = 0.1;    // Circulating macrophage source rate
    mumr = 0.05;  // Circulating macrophage decay rate
    e10 = 0.0;   // Baseline A production by healthy epithelial cells
    e8 = 1.0;     // M2 enhancement of repair
    e9 = 1.0;    // A enhancement of repair

    // Helper functions for activation/influx
    RM1 := m1*(P^nm1/(Hm1^nm1 + P^nm1)) + m11*WS    // M1 activation function
    RM2 := m2*(A^nm2/(Hm2^nm2 + A^nm2)) + k_c       // M2 activation function

    // Differential equations
    Eh' = e1*(Eh + Ed)*(1 - (Eh + Ed)/K) - e2*Eh - e3*WS*Eh + e4*(1 + e9*(M2 + M2R) + e10*A)*Ed
    Ed' = -e2*Ed + e3*WS*Eh - e4*(1 + e8*(M2 + M2R) + e9*A)*Ed

    // Recruited macrophages
    M1' = WS*(smr*RM1)/(mumr + RM1 + RM2) - m5*(A^nm2/(Hm2^nm2 + A^nm2))*M1 - m4*M1
    M2' = WS*(smr*RM2)/(mumr + RM1 + RM2) + m5*(A^nm2/(Hm2^nm2 + A^nm2))*M1 - m4*M2

    // Resident macrophages
    M0R' = -m1*(P^nm1/(Hm1^nm1 + P^nm1))*M0R  - m2*(A^nm2/(Hm2^nm2 + A^nm2))*M0R + m3*WS*(M1R + M2R)*(1 - (M0R + M1R + M2R)/K) - m4*M0R
    M1R' = m1*(P^nm1/(Hm1^nm1 + P^nm1))*M0R - m5*(A^nm2/(Hm2^nm2 + A^nm2))*M1R - m4*M1R
    M2R' = m2*(A^nm2/(Hm2^nm2 + A^nm2))*M0R + m5*(A^nm2/(Hm2^nm2 + A^nm2))*M1R - m4*M2R

    // Cytokine equations including both resident and recruited macrophages
    P' = e5*WS*(Eh^ne1/(He1^ne1 + Eh^ne1)) + e6*WS*(Ed^ne2/(He2^ne2 + Ed^ne2)) + m6*WS*(Hm3^nm3/(A^nm3 + Hm3^nm3))*(M1 + M1R) - m7*P
    A' = m8*(Hm3^nm3/(A^nm3 + Hm3^nm3))*(M2 + M2R) + m9*(Hm4^nm4/(A^nm4 + Hm4^nm4))*(M1 + M1R) - m10*A + k_c

    // Wood smoke recurring dosing, 3 meals a day, as a smooth (Heaviside-approximating)
    // pulse train rather than discrete at-events. Each meal is one rising sigmoid minus
    // one falling sigmoid, both in time%24 so the pattern repeats every 24h; the %24
    // wrap itself lands at t%24=0, inside the 19-8h "off" plateau, so it does not cross
    // a pulse. Replaces the six E1-E6 at-events, which caused CVODE (adaptive) to fail
    // to converge across the hard discontinuities (CV_CONV_FAILURE at t=32h, the second
    // day's first event) -- see docs/tellurium_connection_walkthrough.md. WS_STEEPNESS
    // trades fidelity to the discrete pulse shape (higher = closer to a true 1h square
    // wave, but stiffer) against solver stability (lower = smoother, easier to integrate,
    // but the pulse widens/softens and the delivered dose per meal shifts) -- and there is
    // a hard numerical ceiling on top of that tradeoff: time%24 ranges over 24, so
    // WS_STEEPNESS*24 must stay well under ~709 (exp() overflows to inf past that, in
    // double precision). WS_STEEPNESS=50 overflowed (50*24=1200) and produced
    // CV_TOO_MUCH_ACC even at t=4, hours before any transition -- each sigmoid term still
    // evaluated to a clean 0 or 1 despite the intermediate inf, but something in CVODE's
    // internal Jacobian/step-size estimation choked on the repeated overflow regardless.
    // 20 (20*24=480, safely under the overflow threshold) gives a ~0.29h (~18 min)
    // transition against a 1h pulse -- softer than intended but numerically clean.
    WS := 1/(1+exp(-WS_STEEPNESS*(time%24-8))) - 1/(1+exp(-WS_STEEPNESS*(time%24-9))) + 1/(1+exp(-WS_STEEPNESS*(time%24-13))) - 1/(1+exp(-WS_STEEPNESS*(time%24-14))) + 1/(1+exp(-WS_STEEPNESS*(time%24-18))) - 1/(1+exp(-WS_STEEPNESS*(time%24-19)))
'''


def c_norm(C):
    """Normalized ECM burden, C_norm = C/(C+p.K_C) in [0, 1) (Priority 2: normalize C
    at point of use). C stays the raw unbounded accumulator everywhere else -- call
    this only where C is about to be multiplied into a lambdaVolume scaling or
    blended into a 0-1 signal."""
    return C / (C + p.K_C)


def epithelial_wall_source_pixels(steppable, cell):
    """Pixels an epithelial cell's P (Phase 1) and MMP (Phase 3) output is written into: its
    Medium neighbours on the subepithelial side (y <= p.SUBEPITHELIAL_Y_MAX), the same geometry
    secrete_epithelial_ecm uses, so the fields land in the wall and never in the lumen.
    Deduplicated (several boundary pixels share a neighbour). Fallback when a cell has no
    such Medium neighbour (mesenchyme pressed against its whole basal side): the cell's own
    basal row of boundary pixels -- a cytokine does not vanish because a fibroblast is
    touching, and from inside the cell it still diffuses into the wall. Module-level so the
    DiagnosticsSteppable can evaluate the field at the same pixels (mean_MMP_under_*); any
    SteppableBasePy works as `steppable`. Returns (sorted pixel list, fell_back)."""
    candidates = set()
    own_pixels = []
    for ptd in steppable.get_cell_boundary_pixel_list(cell):
        x, y = ptd.pixel.x, ptd.pixel.y
        own_pixels.append((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (0 <= nx < steppable.dim.x and 0 <= ny < steppable.dim.y):
                continue
            if ny > p.SUBEPITHELIAL_Y_MAX:
                continue
            if steppable.cell_field[nx, ny, 0] is not None:
                continue
            candidates.add((nx, ny))
    if candidates:
        return sorted(candidates), False
    if not own_pixels:
        return [], True
    y_basal = min(y for _, y in own_pixels)
    return sorted(px for px in own_pixels if px[1] == y_basal), True


def init_fibroblast_cell(cell):
    """Shared fibroblast initial state -- used both for the t=0 seed pool
    (TissueInitializationSteppable) and for R_fib recruits
    (FibrosisModelSteppable.recruit_fibroblasts), so the two paths can't
    drift apart into differently-initialized fibroblasts."""
    cell.targetVolume = p.TARGET_VOLUME_FIB
    cell.lambdaVolume = p.LAMBDA_VOLUME_FIB
    cell.dict["activated"] = False
    cell.dict["activation_progress"] = 0.0
    cell.dict["activation_signal"] = 0.0
    cell.dict["local_G"] = 0.0
    cell.dict["local_C"] = 0.0
    cell.dict["local_P"] = 0.0
    cell.dict["local_MMP"] = 0.0
    # Mitosis (cc3d_v1_todo.md PRIORITY 0 item 0, decided 2026-09-06: built for
    # biological completeness, gated on location per Molina et al. 2025's localized-
    # clonal-expansion finding, NOT tuned as a displacement mechanism -- see
    # FibroblastMitosisSteppable). mitosis_clock only accumulates while local G is
    # above p.FIBROBLAST_MITOSIS_G_THRESHOLD; "dividing" flags a cell mid-growth-phase
    # (targetVolume already doubled, waiting for cell.volume to catch up).
    cell.dict["mitosis_clock"] = 0
    cell.dict["dividing"] = False


# ================================================================
# STEPPABLE: INICIALIZACION DEL TEJIDO
# ================================================================
class TissueInitializationSteppable(SteppableBasePy):

    def __init__(self, frequency=1):
        super().__init__(frequency)

    def seed_python_rng(self):
        """Make a pinned <RandomSeed> reproduce the whole run, and say which case this is.

        <RandomSeed> in the XML only seeds CC3D's C++ generator; the fibroblast
        placement, damage seeding and recruitment below draw from Python's `random`,
        which was never seeded, so a pinned XML seed did not reproduce a run
        (lab-notebook/2026/2026-09-18.md). getRandomSeed() returns the pinned value, or 0
        when the XML has no <RandomSeed> (verified 2026-09-20). Pinned: seed Python's
        `random` with it. Unpinned: seed Python's `random` from OS entropy instead, NOT
        with 0, or every general run would get identical fibroblast placement. The banner
        makes a forgotten pin visible in the first lines of the log.

        PSCAN replicates (Gate B3, 2026-10-27): with no XML pin and p.ITER_COUNT set (the
        project is a parameter-scan copy rendered with iter_count), the seed is
        p.REPLICATE_SEED_BASE + iter_count, applied to CC3D's generator through
        Simulator.setRandomSeed before any pixel copy has happened (start() runs before
        MCS 0) and to Python's `random`. Pass/fail (iv) in lab-notebook/2026/2026-10-27.md
        is the test that this actually pins the C++ generator, not just Python's."""
        seed = self.simulator.getRandomSeed()
        if seed:
            random.seed(seed)
            mode = "xml"
            print(f"RNG seed = {seed}: *** PINNED in XML <RandomSeed> (CC3D and Python "
                  f"random) -- remove it for general runs ***")
        elif p.ITER_COUNT is not None:
            seed = p.REPLICATE_SEED_BASE + p.ITER_COUNT
            self.simulator.setRandomSeed(seed)
            random.seed(seed)
            mode = "pscan"
            print(f"RNG seed = {seed}: *** PINNED from PSCAN iter_count={p.ITER_COUNT} "
                  f"(= {p.REPLICATE_SEED_BASE} + iter_count; set on CC3D's generator via "
                  f"Simulator.setRandomSeed, getRandomSeed() now reports "
                  f"{self.simulator.getRandomSeed()}, and on Python random) ***")
        else:
            seed = random.SystemRandom().randrange(1, 2 ** 31)
            random.seed(seed)
            mode = "unpinned"
            print(f"RNG seed: none pinned, this is a random run (Python random seeded from "
                  f"OS entropy = {seed}; CC3D's own seed is not recoverable). To make a "
                  f"run reproducible, add <RandomSeed>N</RandomSeed> to the XML.")
        self.shared_steppable_vars["rng_seed"] = seed
        self.shared_steppable_vars["rng_mode"] = mode
        self.shared_steppable_vars["iter_count"] = p.ITER_COUNT

    def start(self):
        self.seed_python_rng()
        print("=" * 50)
        print(" Initializing airway tissue")
        print("=" * 50)

        # self.create_airway()  # commented out 2026-08-09: A8 decision (lab-notebook
        # 2026-08-08) rejects a frozen airway cell -- lumen must be Medium so the
        # epithelial sheet can be displaced into it. See docs/cc3d_v1_todo.md Priority 1.
        self.create_epithelium()
        self.create_fibroblasts()
        self.create_outer_boundary()
        self.initialize_cell_attributes()
        self.wire_surface_constraint()
        self.link_epithelial_neighbors()
        self.print_mcs0_diagnostics()

        print("Initialization finished.")
        print("=" * 50)
# ------------------------------------------------------------
#p.EPITHELIAL_Y_MIN
    # Stale as written even if ever resurrected: y range below assumed the pre-2026-08-11
    # layout (lumen at low y). Post-reorder the lumen band is 0:p.EPITHELIAL_Y_MIN would need
    # to become p.LUMEN_MIN_Y:p.DOMAIN_Y. Left disabled per the A8 decision either way.
    # def create_airway(self):
    #     """Construye una banda continua de epitelio sano."""
    #     x = 0
    #     y = 0
    #     cell = self.new_cell(self.AIRWAYPLACEHOLDER)
    #
    #     x_end = min(x + p.EPITHELIAL_CELL_WIDTH - 1, p.DOMAIN_X - 1)
    #
    #     self.cell_field[
    #         0:p.DOMAIN_X
    #         ,0:p.EPITHELIAL_Y_MIN,
    #         0
    #     ] = cell
    #
    #         #x += p.EPITHELIAL_CELL_WIDTH

    # ------------------------------------------------------------
    # ------------------------------------------------------------

    def create_epithelium(self):
        """Construye una banda continua de epitelio sano."""
        x = 0
        while x < p.DOMAIN_X:
            cell = self.new_cell(self.EPITHELIALHEALTHY)

            x_end = min(x + p.EPITHELIAL_CELL_WIDTH - 1, p.DOMAIN_X - 1)

            self.cell_field[
                x:x_end + 1,
                p.EPITHELIAL_Y_MIN:p.EPITHELIAL_Y_MAX + 1,
                0
            ] = cell

            x += p.EPITHELIAL_CELL_WIDTH

    # ------------------------------------------------------------

    def create_fibroblasts(self):
        """Distribuye fibroblastos aleatoriamente en el subepitelio."""
        created = 0
        attempts = 0

        while created < p.FIBROBLAST_INITIAL_NUMBER:
            attempts += 1
            if attempts > 10000:
                break

            x = random.randint(2, p.DOMAIN_X - 3)
            y = random.randint(p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX)

            if self.cell_field[x, y, 0] is not None:
                continue

            cell = self.new_cell(self.FIBROBLAST)
            self.cell_field[x, y, 0] = cell
            created += 1

        print(f"Fibroblasts created: {created}")

    # ------------------------------------------------------------

    def create_outer_boundary(self):
        """Frozen wall at the outer edge (A8): non-deformable, biases wall growth
        inward. Needed before Group 3 recruitment and before ECM-driven thickening
        can be directed inward."""
        cell = self.new_cell(self.OUTERBOUNDARY)
        self.cell_field[
            0:p.DOMAIN_X,
            p.OUTER_BOUNDARY_Y_MIN:p.OUTER_BOUNDARY_Y_MAX + 1,
            0
        ] = cell

    # ------------------------------------------------------------

    def wire_surface_constraint(self):
        """Wire up SurfaceLocalFlex for epithelium (Group 1 task 5). Measure
        cell.surface after seeding rather than hardcoding a perimeter -- tracked
        surface depends on NeighborOrder=2, so it exceeds the naive 1st-order value.
        Do not change targetSurface/lambdaSurface on damage."""
        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            cell.targetSurface = cell.surface
            cell.lambdaSurface = p.LAMBDA_SURFACE_EPITHELIAL

    # ------------------------------------------------------------

    def link_epithelial_neighbors(self):
        """FocalPointPlasticity cohesion between neighboring epithelial cells
        (2026-08-13) -- see Subepithelial_Fibrosis.xml's FocalPointPlasticity
        plugin comment for the full rationale. Only epithelium is at this point
        in start() (damage seeding hasn't run yet), but written generically over
        both epithelial types in case this is ever called again later. Guards
        against creating the same link twice from both directions (cell A
        visiting neighbor B, then B visiting neighbor A)."""
        epithelial_types = (self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED)
        linked = 0
        for cell in self.cell_list_by_type(*epithelial_types):
            for neighbor, _ in self.get_cell_neighbor_data_list(cell):
                if neighbor is None or neighbor.type not in epithelial_types:
                    continue
                if self.get_focal_point_plasticity_is_linked(cell, neighbor):
                    continue
                self.new_fpp_link(
                    cell, neighbor,
                    p.EPITHELIAL_FPP_LAMBDA,
                    p.EPITHELIAL_FPP_TARGET_DISTANCE,
                    p.EPITHELIAL_FPP_MAX_DISTANCE
                )
                linked += 1
        print(f"Epithelial FPP links created: {linked}")

    # ------------------------------------------------------------

    def print_mcs0_diagnostics(self):
        """Confirm the volume and surface constraints are actually set (Group 1
        verification)."""
        cell = next(iter(self.cell_list_by_type(self.EPITHELIALHEALTHY)), None)
        if cell is None:
            print("WARNING: no EpithelialHealthy cell found for MCS 0 diagnostics")
            return
        print(
            f"MCS=0 epithelial sample: volume={cell.volume} "
            f"targetVolume={cell.targetVolume} surface={cell.surface} "
            f"targetSurface={cell.targetSurface}"
        )

    # ------------------------------------------------------------

    def initialize_cell_attributes(self):
        """Inicializa propiedades mecanicas y variables internas."""
        for cell in self.cell_list:
            # Epitelio sano
            if cell.type == self.EPITHELIALHEALTHY:
                cell.targetVolume = p.TARGET_VOLUME_EPITHELIAL
                cell.lambdaVolume = p.LAMBDA_VOLUME_EPITHELIAL
                self._init_cell_dict(cell, phenotype="healthy")
            # elif cell.type == self.AIRWAYPLACEHOLDER:
            #     cell.targetVolume = cell.volume
            #     cell.lambdaVolume = p.LAMBDA_VOLUME_AIR
            # Fibroblasto
            elif cell.type == self.FIBROBLAST:
                init_fibroblast_cell(cell)

            # Miofibroblasto
            elif cell.type == self.MYOFIBROBLAST:
                cell.targetVolume = p.TARGET_VOLUME_MYOF
                cell.lambdaVolume = p.LAMBDA_VOLUME_MYOF
                self._init_cell_dict(
                    cell,
                    activated=True,
                    activation_progress=1.0,
                    local_G=0.0,
                    local_C=0.0
                )

    # ------------------------------------------------------------
    def _init_cell_dict(self, cell, **kwargs):
        """Inicializa el diccionario de la celula con valores por defecto."""
        for key, value in kwargs.items():
            cell.dict[key] = value

# ================================================================
# STEPPABLE: ODE SIGNAL (S_M2 pedestal)
# ================================================================
class ODESignalSteppable(SteppableBasePy):
    """The ODE-to-tissue connection (Option C, docs/ode_tissue_coupling_options.md
    sec 3), Route 2 (sec 5): the full model (TISSUE_SIGNAL_MODEL, above)
    integrates live inside CC3D via libRoadRunner (add_free_floating_antimony
    + timestep_sbml, default CVODE integrator), and M2_tot = M2 + M2R is read
    each MCS to scale a uniform additive pedestal S_M2 added to every pixel of
    field G. The pedestal contributes no gradient and no chemotactic force
    (A14) -- it only brings the field's baseline closer to the differentiation
    threshold. Runs before FibrosisModelSteppable so read_local_fields() sees
    the field already updated within the same MCS.

    CVODE used to fail with CV_CONV_FAILURE on the model's original discrete WS
    events (t=32h, see docs/tellurium_connection_walkthrough.md); resolved by
    replacing the events with a continuous smoothed-Heaviside rule (sigmoids)
    in TISSUE_SIGNAL_MODEL -- CVODE integrates stiff-but-continuous dynamics
    well, not genuine discontinuities. Fixed-step RK4 is no longer needed."""

    def __init__(self, frequency=1):
        super().__init__(frequency)
        self.G = None
        self.P = None

    def start(self):
        self.G = self.field.G
        if self.G is None:
            print("WARNING: Field 'G' not found for ODESignalSteppable!")
        self.P = getattr(self.field, "P", None)
        if self.P is None and p.P_FIELD_ENABLED:
            print("WARNING: Field 'P' not found for ODESignalSteppable (P_FIELD_ENABLED is True)!")

        self.add_free_floating_antimony(
            model_string=TISSUE_SIGNAL_MODEL,
            model_name='tissue_signal',
            step_size=p.ODE_STEP_SIZE
        )

        # Gate B1 cross-check: the repair rate is read live from the SBML's e4 (not
        # duplicated in parameters.py); p.ODE_E4_PER_H_REFERENCE only exists to catch the
        # Antimony string and the documentation drifting apart.
        e4_live = self.sbml.tissue_signal['e4']
        if abs(e4_live - p.ODE_E4_PER_H_REFERENCE) > 1e-12:
            print(f"WARNING: SBML e4={e4_live} differs from p.ODE_E4_PER_H_REFERENCE="
                  f"{p.ODE_E4_PER_H_REFERENCE}; the live value is used, update the reference")
        print(f"Epithelial repair (Gate B1): e4={e4_live} /h on the tissue clock "
              f"({p.HOURS_PER_MCS:.5f} h/MCS) = {e4_live * p.HOURS_PER_MCS:.3e} per MCS bare; "
              f"Eq. 16 M2/A enhancement "
              f"{'CARRIED' if p.EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT else 'NOT carried'}")
        self.check_p_field_constants()

    def check_p_field_constants(self):
        """Gate B' Phase 1: the P-field constants parameters.py derives (P_DECAY_PER_MCS from
        the ODE's m7, P_DIFFUSION_PX2_PER_MCS from lambda) against (a) the live SBML and (b) the
        literals the XML carries, since the XML cannot read parameters.py. Warnings only, like
        the e4 check above: the run uses the XML's field constants and the SBML's rate
        constants whatever this prints, so a mismatch has to be fixed in the files, not here.
        Also prints the P_H derivation so the design numbers are in every log."""
        ts = self.sbml.tissue_signal
        m7_live = ts['m7']
        if abs(m7_live - p.ODE_M7_PER_H_REFERENCE) > 1e-12:
            print(f"WARNING: SBML m7={m7_live} differs from p.ODE_M7_PER_H_REFERENCE="
                  f"{p.ODE_M7_PER_H_REFERENCE}; P_DECAY_PER_MCS / the XML decay rest on the reference")
        ratio_live = ts['e6'] / ts['e5']
        if abs(ratio_live - p.P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE) > 1e-9:
            print(f"WARNING: SBML e6/e5={ratio_live} differs from "
                  f"p.P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE={p.P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE}; "
                  f"the live ratio is used for secretion, the reference only in P_H")
        m6e5_live = ts['m6'] / ts['e5']
        if abs(m6e5_live - p.ODE_M6_OVER_E5_REFERENCE) > 1e-9:
            print(f"WARNING: SBML m6/e5={m6e5_live} differs from p.ODE_M6_OVER_E5_REFERENCE="
                  f"{p.ODE_M6_OVER_E5_REFERENCE}; the live ratio is used for S_M1, the reference only in P_H")
        # The live e6/e5 is what secrete_epithelial_P multiplies the damaged cells by (A19a).
        self.shared_steppable_vars['P_damaged_ratio'] = ratio_live
        # Phase 3 (2026-11-02): the same two-way check for the MMP field's literals.
        expected_xml = {
            "P": (p.P_DIFFUSION_XML, p.P_DECAY_XML, p.P_DIFFUSION_PX2_PER_MCS, p.P_DECAY_PER_MCS),
            "MMP": (p.MMP_DIFFUSION_XML, p.MMP_DECAY_XML, p.MMP_DIFFUSION_PX2_PER_MCS, p.MMP_DECAY_PER_MCS),
        }
        for fname, (lit_d, lit_k, der_d, der_k) in expected_xml.items():
            for name, derived, literal in (("GlobalDiffusionConstant", der_d, lit_d),
                                           ("GlobalDecayConstant", der_k, lit_k)):
                if abs(literal - derived) > 0.01 * derived:
                    print(f"WARNING: parameters.py {fname}_*_XML {name}={literal} is >1% off the "
                          f"derived {derived:.4g}; update the XML literal and {fname}_*_XML together")
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(Path(__file__).with_name("Subepithelial_Fibrosis.xml"))
            found = set()
            for df in tree.getroot().iter("DiffusionField"):
                dd = df.find("DiffusionData")
                fname = dd.findtext("FieldName", "").strip() if dd is not None else ""
                if fname not in expected_xml:
                    continue
                found.add(fname)
                lit_d, lit_k = expected_xml[fname][:2]
                xml_d = float(dd.findtext("GlobalDiffusionConstant", "nan"))
                xml_k = float(dd.findtext("GlobalDecayConstant", "nan"))
                if abs(xml_d - lit_d) > 1e-9 or abs(xml_k - lit_k) > 1e-12:
                    print(f"WARNING: XML field {fname} has D={xml_d} k={xml_k} but parameters.py "
                          f"says {fname}_DIFFUSION_XML={lit_d} {fname}_DECAY_XML={lit_k}")
            for fname in expected_xml:
                if fname not in found:
                    print(f"WARNING: no DiffusionField named {fname} found in Subepithelial_Fibrosis.xml")
        except Exception as exc:  # the check must never stop a run
            print(f"WARNING: could not parse the XML for the P/MMP-field cross-check: {exc!r}")
        print(f"P field (Gate B' Phase 1): {'ON' if p.P_FIELD_ENABLED else 'OFF (declared, no sources)'}; "
              f"lambda={p.P_DIFFUSION_LENGTH_PX:.0f} px, D={p.P_DIFFUSION_PX2_PER_MCS:.3f} px^2/MCS, "
              f"k={p.P_DECAY_PER_MCS:.3e} /MCS (t1/2 {0.6931 / p.P_DECAY_PER_MCS:.0f} MCS); "
              f"P_H={p.P_H:.4f} per healthy cell per MCS of WS, damaged x{ratio_live:.1f}; "
              f"S_M1 coefficient P_H*(m6/e5)*n_epi/N_band="
              f"{p.P_H * m6e5_live * p.N_EPITHELIAL_CELLS / p.N_SUBEPITHELIAL_BAND_PIXELS:.4e} "
              f"per band pixel per unit WS*Hill(A)*M1_tot; design band mean at the attractor = "
              f"{p.P_BAND_MEAN_TARGET} (uniform-field approximation)")
        c_term = ("ON" if (p.MMP_FIELD_ENABLED and p.C_MMP_DECAY_ENABLED) else "OFF")
        print(f"MMP field (Gate B' Phase 3): {'ON' if p.MMP_FIELD_ENABLED else 'OFF (declared, no sources)'}; "
              f"lambda={p.MMP_DIFFUSION_LENGTH_PX:.0f} px, D={p.MMP_DIFFUSION_PX2_PER_MCS:.3f} px^2/MCS, "
              f"k={p.MMP_DECAY_PER_MCS:.3e} /MCS (t1/2 {0.6931 / p.MMP_DECAY_PER_MCS:.0f} MCS); "
              f"MMP_0={p.MMP_0:.4f} per epithelial cell per MCS x (1 + {p.K_MMP} * P_local), derived "
              f"for band mean {p.MMP_BAND_MEAN_TARGET} at P_local={p.P_LOCAL_EPITHELIAL_REFERENCE} "
              f"(uniform-field approximation; the field is peaked under the sheet at this lambda); "
              f"TIMP_RATE={p.TIMP_RATE:.4f} per myofibroblast per MCS at its COM; "
              f"C MMP-decay term {c_term} (K_C_MMP={p.K_C_MMP}, every "
              f"{p.C_MMP_DECAY_PERIOD_MCS} MCS)")

    def step(self, mcs):
        m2_tot = self.sbml.tissue_signal['M2'] + self.sbml.tissue_signal['M2R']
        s_m2 = p.S_M2_COEFFICIENT * m2_tot

        # f_d = Ed/(Eh+Ed) from the live ODE (cc3d_v1_todo.md Priority 2), exposed
        # via shared_steppable_vars for FibrosisModelSteppable.apply_damage_seeding
        # to read this same MCS -- same "register before, order matters" pattern
        # already used for S_M2 above.
        eh = self.sbml.tissue_signal['Eh']
        ed = self.sbml.tissue_signal['Ed']
        f_d = ed / (eh + ed) if (eh + ed) > 0 else 0.0
        self.shared_steppable_vars['f_d'] = f_d

        # Gate B1 (2026-10-27): per-MCS repair probability for EpitheliumDamaged, from the
        # ODE's own e4 read live, on the tissue clock, times Eq. 16's M2/A enhancement
        # evaluated on the live ODE state when p.EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT
        # (same inheritance as S_M2 and f_d: the ODE's own expression on its own state).
        # See parameters.py for the decision record. Consumed this same MCS by
        # FibrosisModelSteppable.apply_epithelial_repair.
        ts = self.sbml.tissue_signal
        if p.EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT:
            enhancement = 1.0 + ts['e8'] * (ts['M2'] + ts['M2R']) + ts['e9'] * ts['A']
        else:
            enhancement = 1.0
        p_repair = ts['e4'] * enhancement * p.HOURS_PER_MCS
        self.shared_steppable_vars['epithelial_repair_p'] = p_repair

        # Gate B' Phase 1 (2026-10-31): the exposure gate and the macrophage term of the ODE's
        # P equation, exposed for this MCS. WS gates the epithelial P source
        # (FibrosisModelSteppable.secrete_epithelial_P); WS * Hill(A) * (M1 + M1R) is the
        # ODE's own macrophage source term (m6 * WS * Hm3^nm3/(A^nm3 + Hm3^nm3) * (M1 + M1R)),
        # applied below as the uniform S_M1 pedestal on P (A13), on the S_M2 pattern. Read
        # every MCS regardless of the switch (reads only; the P_analogue_H5 readout needs WS
        # even in an off run); written to the field only when P_FIELD_ENABLED.
        ws = ts['WS']
        m1_tot = ts['M1'] + ts['M1R']
        hm3, nm3 = ts['Hm3'], ts['nm3']
        hill_a = hm3 ** nm3 / (ts['A'] ** nm3 + hm3 ** nm3)
        self.shared_steppable_vars['WS'] = ws
        self.shared_steppable_vars['M1_tot'] = m1_tot
        self.shared_steppable_vars['P_hill_A'] = hill_a
        s_m1 = 0.0
        if p.P_FIELD_ENABLED and self.P is not None and ws >= p.P_WS_FLOOR:
            # Per band pixel: P_H * (m6/e5) * Hill(A) * WS * M1_tot * n_epi / N_band -- the
            # ODE's macrophage:healthy-epithelium source ratio carried over exactly (see
            # parameters.py, P field model constants). Subepithelial band only. Skipped
            # between pulses (WS below p.P_WS_FLOOR), when nothing would be written anyway.
            s_m1 = (p.P_H * (ts['m6'] / ts['e5']) * hill_a * ws * m1_tot
                    * p.N_EPITHELIAL_CELLS / p.N_SUBEPITHELIAL_BAND_PIXELS)
            for x in range(self.dim.x):
                for y in range(p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX + 1):
                    self.P[x, y, 0] += s_m1
        self.shared_steppable_vars['S_M1'] = s_m1

        if mcs % 500 == 0:
            print(
                f"MCS={mcs:6d} ODE: WS={self.sbml.tissue_signal['WS']:.4f} "
                f"M2_tot={m2_tot:.4f} (reference attractor {p.M2_TOT_REFERENCE:.4f}) "
                f"S_M2={s_m2:.5f} f_d={f_d:.4f} A={ts['A']:.4f} "
                f"repair_p={p_repair:.3e}/MCS (enhancement x{enhancement:.3f}) "
                f"repairs so far={self.shared_steppable_vars.get('repair_events', 0)}"
            )
            if p.P_FIELD_ENABLED:
                print(f"MCS={mcs:6d} ODE->P: WS={ws:.4f} M1_tot={m1_tot:.5f} Hill(A)={hill_a:.4f} "
                      f"S_M1={s_m1:.4e} per band pixel this MCS")

        if self.G is not None:
            # Manual pixel loop, not field[:, :, :] += s_m2: matches the pattern
            # DiagnosticsSteppable.print_field_stats already verified safe in
            # this CC3D 4.9.0 build (np.array(field[...]) crashes the backend),
            # and the vectorized in-place setter crashes identically (checked).
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    self.G[x, y, 0] += s_m2

        # Advance the ODE last, after this MCS's value has been read and applied.
        self.timestep_sbml()

# ================================================================
# STEPPABLE: MODELO DE FIBROSIS
# ================================================================

class FibrosisModelSteppable(SteppableBasePy):
    def __init__(self, frequency=1):
        super().__init__(frequency)
        # Referencias a campos
        self.G = None
        self.C = None
        self.P = None
        self.MMP = None

        # Estadisticas globales
        self.mean_G = 0.0
        self.mean_C = 0.0
        self.mean_P = 0.0
        self.mean_MMP = 0.0
        # Gate B' Phase 3: MMP mass actually removed by TIMP (the clamp at 0 means a
        # myofibroblast sitting where MMP ~ 0 removes less than TIMP_RATE) and by the C term.
        self.timp_removed_total = 0.0
        self.c_mmp_removed_total = 0.0
        # Wall-clock spent in each of the three Phase 3 loops (perf_counter, accumulated only
        # on the switched-on path), printed at finish(): machine noise between whole runs
        # (+-50 s on a 300 s run, 2026-11-02) is larger than the loops' own cost, so the
        # per-MCS budget question (plan sec 7) is answered in-process.
        self.t_mmp_source = 0.0
        self.t_timp = 0.0
        self.t_c_mmp = 0.0
        # Gate B' Phase 1: H5 P-analogue accumulator (see accumulate_p_analogue) and a count
        # of epithelial cells whose P had to fall back to their own basal pixels.
        self.p_analogue_sum = 0.0
        self.p_analogue_n = 0
        self.p_secretion_fallbacks = 0
        # Gate B' Phase 2: completed damaged-cell lifetimes (stamped in apply_damage_seeding,
        # closed in apply_epithelial_repair) and the |f_tissue - f_d| tracking gap, criterion 2.
        self.damaged_lifetime_sum = 0
        self.damaged_lifetime_n = 0
        # Expected repairs = sum over damaged cells and MCS of the (gated) per-cell probability,
        # and damaged cell-MCS exposure; their ratio is the expected damaged lifetime. Realized
        # repairs are ~1 per 10k MCS, so a same-seed direction check on realized lifetimes is
        # noise; this deterministic pair shows consumer 1's effect in one run (criterion 3).
        self.expected_repairs = 0.0
        self.damaged_cell_mcs = 0
        # Consumer 2's deterministic companion: fibroblast cell-MCS in which the mitosis gate
        # was open ONLY because of P (G_local below the threshold, G_local + K_PROLIF * P_local
        # at or above it), over all fibroblast cell-MCS. In the current regime G exceeds the
        # 0.225 gate almost everywhere after the first ~1000 MCS, so realized division counts
        # barely move; this says how often P actually tipped the gate.
        self.fib_cell_mcs = 0
        self.p_tipped_gate_mcs = 0
        self.fd_gap_sum = 0.0
        self.fd_gap_n = 0

        # Contadores
        self.n_Eh = 0
        self.n_Ed = 0
        self.n_Fib = 0
        self.n_MyoF = 0
        # Gate B1: cumulative EpitheliumDamaged -> EpithelialHealthy repair events.
        self.n_repair_events = 0

    # ------------------------------------------------------------
    def start(self):
        print("-" * 50)
        print("Fibrosis model initialized")
        print("-" * 50)
        self.shared_steppable_vars["repair_events"] = 0

        # Obtener referencias a los campos definidos en el XML
        self.G = self.field.G
        self.C = self.field.C
        self.P = getattr(self.field, "P", None)
        self.MMP = getattr(self.field, "MMP", None)

        if self.G is None:
            print("WARNING: Field 'G' not found!")
        if self.C is None:
            print("WARNING: Field 'C' not found!")
        if self.P is None and p.P_FIELD_ENABLED:
            print("WARNING: Field 'P' not found but P_FIELD_ENABLED is True!")
        if self.MMP is None and p.MMP_FIELD_ENABLED:
            print("WARNING: Field 'MMP' not found but MMP_FIELD_ENABLED is True!")

    # ------------------------------------------------------------
    def step(self, mcs):
        """Bucle principal del modelo."""
        # Reiniciar contadores
        self.n_Eh = 0
        self.n_Ed = 0
        self.n_Fib = 0
        self.n_MyoF = 0

        # Leer campos locales para cada celula
        self.read_local_fields()

        # Actualizar cada poblacion celular
        self.update_epithelium(mcs)
        self.update_fibroblasts(mcs)
        self.update_myofibroblasts(mcs)

        # Epithelial ECM secretion, subepithelial boundary only (A8/A9).
        self.secrete_epithelial_ecm()

        # Gate B' Phase 1: epithelial P source into the same wall-side pixels, gated by the
        # live ODE WS (writes nothing when the switch is off or WS is zero), and the H5
        # P-analogue readout (a float accumulation; runs in off runs too).
        self.secrete_epithelial_P()
        self.accumulate_p_analogue()

        # Gate B' Phase 3: epithelial MMP source on local_P (read this MCS above), the TIMP
        # sink at myofibroblast COMs, and the optional C MMP-decay term. All three write
        # nothing when MMP_FIELD_ENABLED is off.
        self.secrete_epithelial_MMP()
        self.apply_timp_subtraction()
        self.apply_c_mmp_decay(mcs)

        # R_fib recruitment across the outer boundary (A15) -- after this
        # MCS's population updates, so a recruit's local_G/local_C (0.0 from
        # init_fibroblast_cell) get a real reading on next MCS's
        # read_local_fields() rather than being processed same-step on a
        # placeholder.
        self.recruit_fibroblasts(mcs)

        # Actualizar estadisticas globales
        self.update_global_statistics(mcs)

    # ============================================================
    # CAMPOS LOCALES
    # ============================================================
    def read_local_fields(self):
        """Guarda la concentracion local de G y C para cada celula."""
        if self.G is None or self.C is None:
            return

        for cell in self.cell_list:
            x = int(round(cell.xCOM))
            y = int(round(cell.yCOM))

            x = max(0, min(x, self.dim.x - 1))
            y = max(0, min(y, self.dim.y - 1))

            cell.dict["local_G"] = self.G[x, y, 0]
            cell.dict["local_C"] = self.C[x, y, 0]
            # Gate B' Phase 1: local P at the COM, consumed by Phase 2's repair gating and
            # mitosis gate. 0.0 when the switch is off so no consumer can read a live value.
            cell.dict["local_P"] = (self.P[x, y, 0]
                                    if (p.P_FIELD_ENABLED and self.P is not None) else 0.0)
            # Gate B' Phase 3: local MMP at the COM, consumed by Phase 4's ECM removal.
            cell.dict["local_MMP"] = (self.MMP[x, y, 0]
                                      if (p.MMP_FIELD_ENABLED and self.MMP is not None) else 0.0)

    # ============================================================
    # EPITELIO
    # ============================================================
    def update_epithelium(self, mcs):
        """Cuenta la poblacion epitelial, aplica la reparacion (Gate B1) y luego el damage
        seeding (f_d-gated). Repair first, then seeding: see apply_epithelial_repair."""
        self.n_Eh = len(self.cell_list_by_type(self.EPITHELIALHEALTHY))
        self.n_Ed = len(self.cell_list_by_type(self.EPITHELIUMDAMAGED))
        self.apply_epithelial_repair(mcs)
        self.apply_damage_seeding(mcs)
        # Criterion 2 readout (plan sec 2): the tissue damaged fraction after this MCS's repair
        # and seeding against the ODE's f_d for the same MCS; run mean of the absolute gap goes
        # to the CSV. A float accumulation, no field write, no random draw.
        n_total = self.n_Eh + self.n_Ed
        if n_total > 0:
            f_d = self.shared_steppable_vars.get("f_d", 0.0)
            self.fd_gap_sum += abs(self.n_Ed / n_total - f_d)
            self.fd_gap_n += 1
            self.shared_steppable_vars["fd_gap_mean"] = self.fd_gap_sum / self.fd_gap_n

    # ------------------------------------------------------------
    def apply_epithelial_repair(self, mcs):
        """Gate B1 (2026-10-27): EpitheliumDamaged -> EpithelialHealthy repair, the path
        the ODE has (e4, Eq. 16's M2/A-enhanced form) and the tissue layer lacked
        (docs/aoc_platform_impact_2026-10-11.md sec 2A; lab-notebook/2026/2026-10-23.md;
        docs/roadmap_revision_2026-10-27.md sec 5). One Bernoulli trial per damaged cell per
        MCS at the probability ODESignalSteppable computed this same MCS from the live ODE
        (e4 on the tissue clock, times the enhancement when
        p.EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT; ~8.3e-5 at the attractor, 3.5e-5 bare).

        Runs BEFORE apply_damage_seeding in the same MCS: repair removes a damaged cell,
        the seeding rule then tops the damaged fraction back up toward f_d (its refill
        probability (f_d - f_current)/(1 - f_current) per healthy cell makes a one-cell
        deficit good again within a few MCS). Net effect: the damaged FRACTION still tracks
        the ODE's f_d exactly as before, which is what the ODE prescribes (f_d is its own
        creation/repair balance); what changes is that damage MEMBERSHIP now turns over at
        the repair rate instead of being frozen at first seeding. That gives the spatial
        pattern of damage a lifetime (~12,000 MCS mean at the attractor-enhanced rate, vs
        a 20,000-MCS run) rather than making it a permanent stamp -- the property Gate D's
        focal arm will depend on. Expected events per 20k run at f_d ~ 0.113 on 25 cells:
        ~4-5 enhanced, ~2 bare.

        Type switch audit (cc3d-expert "Type transitions"): the XML's Contact rows, FPP
        parameters, ConnectivityGlobal penalty and FluctuationAmplitude are identical for
        EpitheliumDamaged and EpithelialHealthy, and neither chemotaxes, so the only
        XML-side consequence is the G secretion row (0.1 -> 0.01) -- intended, that is the
        point. Python-side, lambdaVolume is restored from the 0.90x the damage switch
        applied; targetSurface is untouched (wire_surface_constraint: do not change it on
        damage, so not on repair either); the cell keeps its FPP links and its dict."""
        p_repair = self.shared_steppable_vars.get("epithelial_repair_p", 0.0)
        if p_repair <= 0.0:
            return

        for cell in list(self.cell_list_by_type(self.EPITHELIUMDAMAGED)):
            # Gate B' Phase 2, consumer 1: local P slows this cell's repair,
            # p_repair / (1 + K_P * P_local). Off: the B4 probability, and the same single
            # random draw per damaged cell either way, so the RNG sequence is untouched.
            p_cell = p_repair
            if p.P_GATES_REPAIR:
                p_cell = p_repair / (1.0 + p.K_P * cell.dict.get("local_P", 0.0))
            self.expected_repairs += p_cell
            self.damaged_cell_mcs += 1
            if random.random() < p_cell:
                lifetime = mcs - cell.dict.get("damaged_since", mcs)
                gate_note = (f", gated to {p_cell:.3e} at P_local={cell.dict.get('local_P', 0.0):.3f}"
                             if p.P_GATES_REPAIR else "")
                self.damaged_lifetime_sum += lifetime
                self.damaged_lifetime_n += 1
                cell.type = self.EPITHELIALHEALTHY
                cell.dict["phenotype"] = "healthy"
                cell.lambdaVolume = p.LAMBDA_VOLUME_EPITHELIAL
                self.n_Ed -= 1
                self.n_Eh += 1
                self.n_repair_events += 1
                print(f"MCS={mcs:6d} epithelial repair: cell id={cell.id} damaged -> healthy "
                      f"(repair #{self.n_repair_events}, p_repair={p_repair:.3e}{gate_note}, "
                      f"damaged for {lifetime} MCS, Ed now {self.n_Ed}/{self.n_Eh + self.n_Ed})")
        self.shared_steppable_vars["repair_events"] = self.n_repair_events
        self.shared_steppable_vars["damaged_lifetime_sum"] = self.damaged_lifetime_sum
        self.shared_steppable_vars["damaged_lifetime_n"] = self.damaged_lifetime_n
        self.shared_steppable_vars["expected_repairs"] = self.expected_repairs
        self.shared_steppable_vars["damaged_cell_mcs"] = self.damaged_cell_mcs

    # ------------------------------------------------------------
    def apply_damage_seeding(self, mcs):
        """Diffuse damage seeding, gated on the live ODE's f_d = Ed/(Eh+Ed)
        (cc3d_v1_todo.md Priority 2; ode_tissue_coupling_options.md sec 2
        Option A). Replaces the old continuous damage/repair accumulator,
        which floored on hardcoded TGFB_LEVEL/PRO_INFLAMMATORY_LEVEL
        constants and converted the whole epithelial population in near
        lockstep regardless of the ODE state (see lab discussion 2026-08-09).

        P(healthy -> damaged) = max(0, (f_d - f_current) / (1 - f_current))
        applied identically to every healthy cell each step -- independent
        per-cell Bernoulli trials at a shared probability is the diffuse
        (uniform-random-target) placement arm; focal placement (seeded foci,
        neighbor-biased spread) is not implemented yet.

        This rule only pushes the damaged fraction UP toward f_d; it never
        un-damages a cell itself. Until 2026-10-27 that made damage one-directional
        (a v1 simplification, not an ODE inheritance -- A19 correction, 2026-10-23).
        Gate B1 added the reverse path, apply_epithelial_repair, which runs just
        before this rule each MCS at the ODE's e4-derived rate; this rule then refills
        the deficit, so the fraction still tracks f_d while membership turns over."""
        f_d = self.shared_steppable_vars.get("f_d", 0.0)
        n_total = self.n_Eh + self.n_Ed
        if n_total == 0:
            return

        f_current = self.n_Ed / n_total
        if f_current >= 1.0:
            return

        p_convert = max(0.0, (f_d - f_current) / (1.0 - f_current))
        if p_convert <= 0.0:
            return

        for cell in list(self.cell_list_by_type(self.EPITHELIALHEALTHY)):
            if random.random() < p_convert:
                cell.type = self.EPITHELIUMDAMAGED
                cell.dict["phenotype"] = "damaged"
                # Gate B' Phase 2: stamp for the damaged-lifetime readout (a dict write only).
                cell.dict["damaged_since"] = mcs
                # Evitar que pierda completamente su volumen o cohesion elastica (mantener estructura)
                cell.lambdaVolume = 0.90 * p.LAMBDA_VOLUME_EPITHELIAL
                self.n_Eh -= 1
                self.n_Ed += 1

    # ------------------------------------------------------------
    def secrete_epithelial_ecm(self):
        """Epithelium secretes into field C at its boundary pixels, but only
        writes into a neighboring Medium pixel on the subepithelial side
        (y <= p.SUBEPITHELIAL_Y_MAX, i.e. below the epithelial band post-2026-08-11
        reorder) -- never the cell's own pixel, and never a Medium neighbor on
        the luminal side (y >= p.LUMEN_MIN_Y, above the band). Keeps ECM
        occupying lattice space distinct from the secreting cell, and keeps
        the lumen collagen-free per A8/A9."""
        if self.C is None:
            return

        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            for ptd in self.get_cell_boundary_pixel_list(cell):
                x, y = ptd.pixel.x, ptd.pixel.y
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.dim.x and 0 <= ny < self.dim.y):
                        continue
                    if ny > p.SUBEPITHELIAL_Y_MAX:
                        continue
                    if self.cell_field[nx, ny, 0] is not None:
                        continue
                    self.C[nx, ny, 0] += p.EPITHELIAL_ECM_SECRETION_RATE

    # ------------------------------------------------------------
    def epithelial_p_source_pixels(self, cell):
        """Pixels an epithelial cell's P output is written into; the geometry lives in the
        module-level epithelial_wall_source_pixels (shared with the MMP source and the
        diagnostics since Phase 3). Returns (sorted pixel list, fell_back)."""
        return epithelial_wall_source_pixels(self, cell)

    def secrete_epithelial_P(self):
        """Gate B' Phase 1 (docs/gate_Bprime_plan_2026-10-30.md sec 3, A19a): each epithelial
        cell writes P_H * WS (healthy) or P_H * (e6/e5) * WS (damaged; the ratio is read live
        from the SBML, 2:1) into the field P per MCS, the amount split evenly over its
        wall-side Medium neighbours (epithelial_p_source_pixels). WS is the ODE's exposure
        pulse read this same MCS by ODESignalSteppable, so the source pulses with the cooking
        schedule as it does in the ODE; P's ~1000-MCS half-life averages the pulses (the
        two-clock caveat, plan sec 7, stands). Python-side rather than <SecretionData> because
        the XML cannot gate on a live SBML variable. Behind the switch: no field write, no
        random draw, so criterion 1 is untouched."""
        if not p.P_FIELD_ENABLED or self.P is None:
            return
        ws = self.shared_steppable_vars.get("WS", 0.0)
        if ws < p.P_WS_FLOOR:
            return
        ratio = self.shared_steppable_vars.get("P_damaged_ratio", p.P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE)
        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            amount = p.P_H * ws * (ratio if cell.type == self.EPITHELIUMDAMAGED else 1.0)
            pixels, fell_back = self.epithelial_p_source_pixels(cell)
            if fell_back:
                self.p_secretion_fallbacks += 1
            if not pixels:
                continue
            per_pixel = amount / len(pixels)
            for x, y in pixels:
                self.P[x, y, 0] += per_pixel

    def accumulate_p_analogue(self):
        """H5 P-analogue (docs/aoc_platform_impact_2026-10-11.md sec 5 H5; A17 2026-10-27/30):
        the IL-6-class readout computed from the EPITHELIAL STATE alone, kept alongside the
        field so it exists in P-off runs and in Gate D's condition (0). Per MCS it is the
        exposure-gated epithelial P production per cell relative to one healthy cell at full
        exposure, WS * (n_h + ratio * n_d) / n_epi, i.e. the P source without P_H, diffusion
        or decay; the CSV reports its run mean (P_analogue_H5). At the attractor this is
        ~<WS> (1 + f_d) ~ 0.14. First definition, 2026-10-31; Gate C may replace it with the
        chip-clock time series (H6), the run mean is what fits one CSV row."""
        ws = self.shared_steppable_vars.get("WS", 0.0)
        ratio = self.shared_steppable_vars.get("P_damaged_ratio", p.P_DAMAGED_TO_HEALTHY_RATIO_REFERENCE)
        n_total = self.n_Eh + self.n_Ed
        if n_total > 0:
            self.p_analogue_sum += ws * (self.n_Eh + ratio * self.n_Ed) / n_total
        self.p_analogue_n += 1
        self.shared_steppable_vars["P_analogue_H5"] = (
            self.p_analogue_sum / self.p_analogue_n if self.p_analogue_n else 0.0)
        self.shared_steppable_vars["P_secretion_fallbacks"] = self.p_secretion_fallbacks

    # ------------------------------------------------------------
    def secrete_epithelial_MMP(self):
        """Gate B' Phase 3 (plan sec 3, consumer 3 of P; A14): every epithelial cell, healthy
        and damaged alike, writes p.MMP_0 * (1 + p.K_MMP * local_P) into the field MMP per
        MCS, every MCS (not WS-gated: the exposure enters through local_P, which the P field
        carries from the WS-gated P sources), split evenly over the same wall-side Medium
        pixels as P (epithelial_wall_source_pixels, same fallback). local_P is this MCS's
        read_local_fields value at the cell's COM, the sheet-level P consumer 1 also reads.
        Python-side because <SecretionData> cannot read another field. Behind the switch: no
        field write, no random draw."""
        if not p.MMP_FIELD_ENABLED or self.MMP is None:
            return
        t0 = time.perf_counter()
        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            amount = p.MMP_0 * (1.0 + p.K_MMP * cell.dict.get("local_P", 0.0))
            pixels, _ = epithelial_wall_source_pixels(self, cell)
            if not pixels:
                continue
            per_pixel = amount / len(pixels)
            for x, y in pixels:
                self.MMP[x, y, 0] += per_pixel
        self.t_mmp_source += time.perf_counter() - t0

    def apply_timp_subtraction(self):
        """Gate B' Phase 3 (plan sec 3): each myofibroblast subtracts p.TIMP_RATE from the MMP
        field at its COM pixel per MCS, clamped at 0 (TIMP-1 is raised alongside the
        gelatinases under wood smoke, Zou2014, and myofibroblasts are the model's TIMP
        source). The mass actually removed is accumulated for the log, since the clamp
        removes less than TIMP_RATE wherever MMP is already near 0."""
        if not p.MMP_FIELD_ENABLED or self.MMP is None:
            return
        t0 = time.perf_counter()
        for cell in self.cell_list_by_type(self.MYOFIBROBLAST):
            x = max(0, min(int(round(cell.xCOM)), self.dim.x - 1))
            y = max(0, min(int(round(cell.yCOM)), self.dim.y - 1))
            value = self.MMP[x, y, 0]
            new_value = value - p.TIMP_RATE
            if new_value < 0.0:
                new_value = 0.0
            self.MMP[x, y, 0] = new_value
            self.timp_removed_total += value - new_value
        self.shared_steppable_vars["timp_removed_total"] = self.timp_removed_total
        self.t_timp += time.perf_counter() - t0

    def apply_c_mmp_decay(self, mcs):
        """Gate B' Phase 3 (plan sec 3, optional): C loses p.K_C_MMP * MMP_local * C per
        subepithelial-band pixel per MCS on top of the XML's 0.0005 base decay (the MMP arm
        of collagen turnover; C is stiffness-only until Phase 4, so this is the only MMP
        consumer in Phase 3). A 13,600-pixel loop like the S_M1 pedestal; runs every
        p.C_MMP_DECAY_PERIOD_MCS MCS with the per-call rate scaled by the period (Module 8.2:
        frequency and rate are coupled). Pixels with MMP == 0 (most of the band at
        lambda = 8 px) are skipped without a C write. No random draw."""
        if not (p.MMP_FIELD_ENABLED and p.C_MMP_DECAY_ENABLED) or self.MMP is None or self.C is None:
            return
        period = p.C_MMP_DECAY_PERIOD_MCS
        if mcs % period != 0:
            return
        t0 = time.perf_counter()
        factor = p.K_C_MMP * period
        removed = 0.0
        for x in range(self.dim.x):
            for y in range(p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX + 1):
                m = self.MMP[x, y, 0]
                if m <= 0.0:
                    continue
                c = self.C[x, y, 0]
                if c <= 0.0:
                    continue
                loss = factor * m * c
                if loss > c:
                    loss = c
                self.C[x, y, 0] = c - loss
                removed += loss
        self.c_mmp_removed_total += removed
        self.shared_steppable_vars["c_mmp_removed_total"] = self.c_mmp_removed_total
        self.t_c_mmp += time.perf_counter() - t0

    def finish(self):
        """Gate B' Phase 3 end-of-run diagnostics, MMP runs only (nothing printed otherwise,
        so an off run's log is untouched): the wall-clock of the three Phase 3 loops, and
        two per-cell tables behind the plan's direction checks. (a) Per epithelial cell: type,
        local_P and the MMP at its wall-side source pixels -- the "highest under damaged
        cells" check compares a 3-cell sample against 22, and the 2:1 P contrast is a
        band-scale difference at lambda_P = 40 px, so the per-cell spread is what makes the
        mean comparison readable. (b) Per myofibroblast: MMP at its COM pixel against the
        mean of its four lattice neighbours -- the TIMP sink's local dip, which the
        band-mean comparison in the CSV cannot see because myofibroblasts sit near the sheet
        where MMP is far above the band mean."""
        if not p.MMP_FIELD_ENABLED or self.MMP is None:
            return
        print(f"MMP timing: source loop {self.t_mmp_source:.1f} s, TIMP {self.t_timp:.1f} s, "
              f"C MMP-decay term {self.t_c_mmp:.1f} s (period {p.C_MMP_DECAY_PERIOD_MCS} MCS, "
              f"{'ON' if p.C_MMP_DECAY_ENABLED else 'OFF'}); "
              f"TIMP removed {self.timp_removed_total:.4g}, C removed by MMP {self.c_mmp_removed_total:.4g}")
        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            pixels, fell_back = epithelial_wall_source_pixels(self, cell)
            under = (sum(self.MMP[x, y, 0] for x, y in pixels) / len(pixels)) if pixels else 0.0
            print(f"MMP per-cell: {'damaged' if cell.type == self.EPITHELIUMDAMAGED else 'healthy'} "
                  f"id={cell.id} xCOM={cell.xCOM:.1f} local_P={cell.dict.get('local_P', 0.0):.4f} "
                  f"src_px={len(pixels)}{' (fallback)' if fell_back else ''} MMP_under={under:.4f}")
        for cell in self.cell_list_by_type(self.MYOFIBROBLAST):
            x = max(0, min(int(round(cell.xCOM)), self.dim.x - 1))
            y = max(0, min(int(round(cell.yCOM)), self.dim.y - 1))
            nbrs = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    if 0 <= x + dx < self.dim.x and 0 <= y + dy < self.dim.y]
            nbr_mean = sum(self.MMP[nx, ny, 0] for nx, ny in nbrs) / len(nbrs)
            at_com = self.MMP[x, y, 0]
            print(f"MMP per-myof: id={cell.id} COM=({x},{y}) MMP_at_COM={at_com:.4f} "
                  f"neighbour_mean={nbr_mean:.4f} dip={nbr_mean - at_com:.4f}")

    # ============================================================
    # FIBROBLASTOS
    # ============================================================
    def update_fibroblasts(self, mcs):
        """Actualiza todos los fibroblastos.

        Materialized into a list before iterating: activate_fibroblast can
        mutate cell.type via convert_to_myofibroblast mid-loop, and mutating
        while iterating cell_list_by_type can skip or double-process cells."""
        for cell in list(self.cell_list_by_type(self.FIBROBLAST)):
            self.n_Fib += 1
            # Forzar restriccion geometrica dura: si el centroide sube al espacio epitelial/lumen, empujarlo hacia abajo
            # (post-2026-08-11 reorder: the epithelial/lumen space is now *above* the
            # subepithelial band, so the wrong-direction check is yCOM > p.SUBEPITHELIAL_Y_MAX)
            if cell.yCOM > p.SUBEPITHELIAL_Y_MAX:
                #cell.yCOM = p.SUBEPITHELIAL_Y_MAX # O aplicar fuerza de restitucion
                pass
            self.update_fibroblast_state(cell, mcs)
    # ------------------------------------------------------------

    def recruit_fibroblasts(self, mcs):
        """R_fib recruitment across the outer boundary (A15). One Bernoulli
        trial per MCS (probability p.R_FIB) rather than a fixed schedule, so
        the expected rate is p.R_FIB per MCS without needing a fractional-cell
        accumulator. Placement is GF-biased (ode_tissue_coupling_options.md
        sec 3, Option F.2): candidate empty (Medium) pixels within a band
        adjacent to the frozen outer boundary are weighted by local G, not
        chosen uniformly -- so recruitment clusters where the signal already
        is, without adding a new field."""
        if random.random() >= p.R_FIB:
            return

        # Band adjacent to the frozen outer boundary: post-2026-08-11 reorder the
        # boundary sits at low y, so the band runs up from p.SUBEPITHELIAL_Y_MIN
        # (previously it ran down from p.SUBEPITHELIAL_Y_MAX).
        y_min = p.SUBEPITHELIAL_Y_MIN
        y_max = p.SUBEPITHELIAL_Y_MIN + p.RECRUITMENT_BAND_WIDTH - 1

        candidates = []
        weights = []
        for x in range(self.dim.x):
            for y in range(y_min, y_max + 1):
                if self.cell_field[x, y, 0] is not None:
                    continue
                g_val = self.G[x, y, 0] if self.G is not None else 0.0
                candidates.append((x, y))
                weights.append(g_val + p.RECRUITMENT_G_EPSILON)

        if not candidates:
            return

        x, y = random.choices(candidates, weights=weights, k=1)[0]
        cell = self.new_cell(self.FIBROBLAST)
        self.cell_field[x, y, 0] = cell
        init_fibroblast_cell(cell)

        print(f"MCS={mcs:6d} R_fib recruited a new fibroblast at ({x},{y})")

    # ------------------------------------------------------------

    def update_fibroblast_state(self, cell, mcs):
        """Actualiza el estado de un fibroblasto."""
        G = cell.dict.get("local_G", 0.0)
        C = cell.dict.get("local_C", 0.0)

        # Reducir movilidad con ECM (mobility itself comes from the XML
        # chemotaxis lambdas; lambdaVolume stiffens the cell against ECM).
        # C normalized at point of use (Priority 2) -- C itself is unbounded.
        cell.lambdaVolume = p.LAMBDA_VOLUME_FIB * (1.0 + c_norm(C))

        # Mitosis and differentiation are kept mutually exclusive per cell (cc3d_v1_todo.md
        # PRIORITY 0 item 0): a cell already growing toward division doesn't also accrue
        # differentiation progress, and vice versa -- see update_fibroblast_mitosis's
        # docstring. Not a biological claim, just keeps the two processes from fighting
        # over the same cell's targetVolume in the same MCS.
        if cell.dict.get("dividing"):
            return
        self.update_fibroblast_mitosis(cell)
        if cell.dict.get("dividing"):
            return

        # Activacion
        self.activate_fibroblast(cell, G, C, mcs)

    # ------------------------------------------------------------

    def update_fibroblast_mitosis(self, cell):
        """GF-gated fibroblast mitosis (cc3d_v1_todo.md PRIORITY 0 item 0, decided
        2026-09-06): built for biological completeness -- proliferation is a real
        fibroblast characteristic, not just migration -- and deliberately NOT tuned as
        a displacement mechanism; PRIORITY 0's diagnosis (2026-09-03) found the
        displacement plateau is a population/occupancy gap, but the decision was to
        pursue a v2 volume-occupying ECM cell type for that, not lean on mitosis to
        force it. This rule stays at a reasonable/low, literature-anchored level.

        Gates WHERE/WHETHER a fibroblast accumulates cell-cycle progress on local G,
        not the cycle's rate: Molina et al. (2025) found elevated fibroblast
        proliferation in vivo is spatially localized clonal expansion in remodeling
        regions, not a faster global cycle, consistent with Mio1992/Holz2004 finding
        no disease-driven speedup of the cycle itself (p.FIBROBLAST_CYCLE_TIME_H,
        held at the literature 25-34h range). mitosis_clock accumulates only while
        local G >= p.FIBROBLAST_MITOSIS_G_THRESHOLD (paused, not reset, when G drops
        below it -- a brief excursion out of a permissive region shouldn't erase
        accumulated progress). Once the clock reaches p.FIBROBLAST_CYCLE_MCS, this
        starts the growth phase (targetVolume -> 2x); FibroblastMitosisSteppable
        watches for cell.volume to catch up and performs the actual division."""
        G = cell.dict.get("local_G", 0.0)
        # Gate B' Phase 2, consumer 2: the gate signal is G_local + K_PROLIF * P_local when
        # P_DRIVES_PROLIFERATION (IL-6/STAT3 route); off, it is G alone as in Gate B4. A
        # comparison only -- no random draw, no field write.
        signal = G
        if p.P_DRIVES_PROLIFERATION:
            signal = G + p.K_PROLIF * cell.dict.get("local_P", 0.0)
        self.fib_cell_mcs += 1
        if signal >= p.FIBROBLAST_MITOSIS_G_THRESHOLD:
            cell.dict["mitosis_clock"] = cell.dict.get("mitosis_clock", 0) + 1
            if G < p.FIBROBLAST_MITOSIS_G_THRESHOLD:
                self.p_tipped_gate_mcs += 1
        self.shared_steppable_vars["fib_cell_mcs"] = self.fib_cell_mcs
        self.shared_steppable_vars["p_tipped_gate_mcs"] = self.p_tipped_gate_mcs

        if cell.dict.get("mitosis_clock", 0) >= p.FIBROBLAST_CYCLE_MCS:
            cell.targetVolume = 2.0 * p.TARGET_VOLUME_FIB
            cell.dict["dividing"] = True
            cell.dict["mitosis_clock"] = 0

    # ------------------------------------------------------------

    def activate_fibroblast(self, cell, G, C, mcs):
        """
        Activa fibroblasto -> miofibroblasto, gated on local G only.
        """
        if "activation_progress" not in cell.dict:
            cell.dict["activation_progress"] = 0.0

        # Gated on local G alone (cc3d_v1_todo.md Priority 2): TGFB_LEVEL/M2_LEVEL
        # were hardcoded placeholders giving every fibroblast nearly the same
        # activation_signal regardless of position (G is close to spatially
        # uniform except near a secreting source, from the ODE's S_M2 pedestal),
        # which converted the whole starting pool within ~300 MCS regardless of
        # location -- and Myofibroblast has Lambda=0, so that also silently
        # killed observable fibroblast chemotaxis. C is left out too (not just
        # the placeholders): it's an unbounded, unnormalized accumulator
        # (cc3d_v1_todo.md's separate "normalize C at point of use" item), not
        # yet safe to mix into a 0-1 gate. Below p.FIB_TO_MYOF_G_THRESHOLD, no
        # progress accrues at all -- only cells that migrate close enough to a
        # high-G source (damaged epithelium, existing myofibroblasts) differentiate.
        activation_signal = G if G >= p.FIB_TO_MYOF_G_THRESHOLD else 0.0
        cell.dict["activation_signal"] = activation_signal

        # Progreso
        activation_rate = 0.02 * activation_signal
        cell.dict["activation_progress"] = min(
            1.0,
            cell.dict["activation_progress"] + activation_rate
        )

        # Cambios graduales
        progress = cell.dict["activation_progress"]
        cell.lambdaVolume = p.LAMBDA_VOLUME_FIB * (1.0 + progress)

        # Conversion completa
        if progress >= 1.0:
            self.convert_to_myofibroblast(cell)

    # ------------------------------------------------------------

    def convert_to_myofibroblast(self, cell):
        """Conversion irreversible a miofibroblasto."""
        cell.type = self.MYOFIBROBLAST
        cell.targetVolume = p.TARGET_VOLUME_MYOF
        cell.lambdaVolume = p.LAMBDA_VOLUME_MYOF
        cell.dict["activated"] = True
        cell.dict["phenotype"] = "myofibroblast"
        cell.dict["activation_progress"] = 1.0

    # ============================================================
    # MYOFIBROBLASTS
    # ============================================================

    def update_myofibroblasts(self, mcs):
        """Actualiza todos los miofibroblastos."""
        for cell in self.cell_list_by_type(self.MYOFIBROBLAST):
            self.n_MyoF += 1
            self.update_myofibroblast_state(cell, mcs)

    # ------------------------------------------------------------

    def update_myofibroblast_state(self, cell, mcs):
        """Actualiza el estado de un miofibroblasto."""
        C = cell.dict.get("local_C", 0.0)
        c_normalized = c_norm(C)
        # Rigidez (mobility itself comes from the XML chemotaxis lambdas).
        # C normalized at point of use (Priority 2) -- C itself is unbounded.
        cell.lambdaVolume = p.LAMBDA_VOLUME_MYOF * (1.0 + 2.0 * c_normalized)
        # PRIORITY 0 displacement plan step 3: local ECM burden also grows the
        # cell's targetVolume, not just its resistance to compression -- this is
        # what lets accumulated C actually push on the subepithelial compartment's
        # footprint instead of only stiffening cells already there.
        cell.targetVolume = p.TARGET_VOLUME_MYOF * (1.0 + p.MYOF_TARGET_VOLUME_GROWTH_FACTOR * c_normalized)


    # ============================================================
    # GLOBAL STATISTICS
    # ============================================================
    def compute_mean_field(self, field_name, y_min, y_max):
        """Calcula la media de un campo en una region."""
        field = getattr(self.field, field_name, None)
        if field is None:
            return 0.0

        total = 0.0
        n = 0
        for x in range(self.dim.x):
            for y in range(y_min, y_max + 1):
                total += field[x, y, 0]
                n += 1

        return total / n if n > 0 else 0.0

    # ------------------------------------------------------------
    def compute_mean_ecm(self):
        return self.compute_mean_field("C", p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX)

    def compute_mean_growth_factor(self):
        return self.compute_mean_field("G", p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX)

    def compute_mean_p(self):
        return self.compute_mean_field("P", p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX)

    def compute_mean_mmp(self):
        return self.compute_mean_field("MMP", p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX)

    # ------------------------------------------------------------
    def update_global_statistics(self, mcs):
        """Actualiza variables globales y muestra estadisticas."""
        self.mean_G = self.compute_mean_growth_factor()
        self.mean_C = self.compute_mean_ecm()
        # P band mean only on the print cadence: it feeds nothing but the log line (the CSV
        # computes its own at the final MCS), and the 13,600-pixel read every MCS was the
        # larger half of the P-on cost in the Phase 1 smoke run.
        if p.P_FIELD_ENABLED and self.P is not None and mcs % 100 == 0:
            self.mean_P = self.compute_mean_p()
        if p.MMP_FIELD_ENABLED and self.MMP is not None and mcs % 100 == 0:
            self.mean_MMP = self.compute_mean_mmp()

        if mcs % 100 == 0:
            print(
                f"MCS={mcs:6d} | "
                f"Eh={self.n_Eh:3d} | Ed={self.n_Ed:3d} | "
                f"Fib={self.n_Fib:3d} | MyoF={self.n_MyoF:3d} | "
                f"G={self.mean_G:.3f} | C={self.mean_C:.3f}"
            )
            if p.P_FIELD_ENABLED:
                print(f"MCS={mcs:6d} | P band mean={self.mean_P:.4f} (design ~{p.P_BAND_MEAN_TARGET} "
                      f"at the attractor) | P_analogue_H5 run mean="
                      f"{self.shared_steppable_vars.get('P_analogue_H5', 0.0):.4f} | "
                      f"P-source fallbacks so far={self.p_secretion_fallbacks}")
            if p.MMP_FIELD_ENABLED and self.MMP is not None:
                myof_vals = []
                for cell in self.cell_list_by_type(self.MYOFIBROBLAST):
                    x = max(0, min(int(round(cell.xCOM)), self.dim.x - 1))
                    y = max(0, min(int(round(cell.yCOM)), self.dim.y - 1))
                    myof_vals.append(self.MMP[x, y, 0])
                at_myof = sum(myof_vals) / len(myof_vals) if myof_vals else float("nan")
                print(f"MCS={mcs:6d} | MMP band mean={self.mean_MMP:.4f} (design ~{p.MMP_BAND_MEAN_TARGET} "
                      f"at the attractor) | at myofibroblast COMs={at_myof:.4f} (n={len(myof_vals)}) | "
                      f"TIMP removed so far={self.timp_removed_total:.4g} | "
                      f"C removed by MMP so far={self.c_mmp_removed_total:.4g}")

# ================================================================
# STEPPABLE: FIBROBLAST MITOSIS
# ================================================================


class FibroblastMitosisSteppable(MitosisSteppableBase):
    """GF-gated fibroblast mitosis (cc3d_v1_todo.md PRIORITY 0 item 0, decided
    2026-09-06): built because proliferation is a real fibroblast characteristic, not
    a displacement mechanism -- kept at a reasonable/low, literature-anchored rate
    (p.FIBROBLAST_CYCLE_MCS, ~1730 MCS from the cited 25-34h doubling-time range via
    p.S_PER_MCS) and gated on local G (FibrosisModelSteppable.update_fibroblast_mitosis)
    so *whether/where* a fibroblast divides tracks Molina et al. (2025)'s localized-
    clonal-expansion finding, not a rate turned up to force sheet displacement. See
    PRIORITY 0 item 0: the decision was that a v2 volume-occupying ECM cell type, not
    cell-crowding via mitosis, is the intended mechanism for that question.

    Standard CC3D volume-doubling mitosis (see .claude/skills/cc3d-expert): rather than
    this steppable itself deciding who divides, FibrosisModelSteppable sets a
    dict["dividing"] fibroblast's targetVolume to 2x once its GF-gated cell-cycle clock
    completes. This steppable only watches for cell.volume to catch up to most of that
    (p.MITOSIS_GROWTH_TRIGGER_FRACTION, not exactly 2x -- lambdaVolume-driven relaxation
    toward a target never converges exactly) and performs the actual split, then resets
    both daughters to normal fibroblast state. Only Fibroblast divides, not
    Myofibroblast -- Molina2025's clonal expansion is of fibroblast progeny, and
    myofibroblasts are this model's differentiated, ECM-secreting end state."""

    def __init__(self, frequency=1):
        MitosisSteppableBase.__init__(self, frequency)
        self.division_count = 0

    def step(self, mcs):
        cells_to_divide = [
            cell for cell in self.cell_list_by_type(self.FIBROBLAST)
            if cell.dict.get("dividing")
            and cell.volume >= p.MITOSIS_GROWTH_TRIGGER_FRACTION * 2.0 * p.TARGET_VOLUME_FIB
        ]
        for cell in cells_to_divide:
            self.division_count += 1
            print(
                f"MCS={mcs:6d} fibroblast mitosis: cell id={cell.id} divided "
                f"(volume={cell.volume}, division #{self.division_count})"
            )
            self.divide_cell_random_orientation(cell)
        self.shared_steppable_vars["fibroblast_divisions"] = self.division_count

        if mcs % 1000 == 0 and mcs > 0:
            print(f"MCS={mcs:6d} fibroblast mitosis: {self.division_count} division(s) so far")

    def finish(self):
        print(f"FINAL: fibroblast mitosis total divisions = {self.division_count}")

    def update_attributes(self):
        # Parent grew to 2x targetVolume to trigger this split; halving it here
        # (rather than hardcoding p.TARGET_VOLUME_FIB) matches it back to whatever the
        # growth phase actually set, and clone_parent_2_child copies that already-
        # halved value to the child along with type and cell.dict.
        self.parent_cell.targetVolume /= 2.0
        self.clone_parent_2_child()
        for cell in (self.parent_cell, self.child_cell):
            cell.lambdaVolume = p.LAMBDA_VOLUME_FIB
            cell.dict["dividing"] = False
            cell.dict["mitosis_clock"] = 0
            cell.dict["activation_progress"] = 0.0
            cell.dict["activation_signal"] = 0.0


# ================================================================
# STEPPABLE: GROUP 1 VERIFICATION
# ================================================================
class DiagnosticsSteppable(SteppableBasePy):
    """Verification only, per the Group 1 acceptance criteria: field magnitude
    sanity, epithelial count conservation, and sheet-integrity checks (no
    fragmentation, no gaps) at MCS 0, 1000 and the final MCS of the run.

    The final checkpoint is driven from finish(), not a hardcoded MCS number:
    <Steps>N</Steps> simulates MCS 0 through N-1, so a literal checkpoint at
    N (e.g. 20000) never fires and silently skips the last-MCS check."""

    CHECKPOINTS = (0, 1000)

    # PRIORITY 0 plan step 3a (cc3d_v1_todo.md, 2026-08-14): finer-grained than
    # CHECKPOINTS, spanning the MCS ~300-400 window where lumen narrowing was
    # observed to plateau, so print_myofibroblast_c_norm_stats can show whether
    # c_norm(C) = C/(C+p.K_C) is already saturated by then (p.K_C=20 vs. field C's
    # observed max ~150-160) rather than just inferring it from the aggregate
    # field-mean stats print_field_stats already logs.
    C_NORM_CHECKPOINTS = (0, 100, 200, 300, 400, 500, 750, 1000, 2000, 5000, 10000)

    # Flood-fill seed for compute_lumen_area: top-center of the domain, inside the
    # lumen band (y >= p.LUMEN_MIN_Y) at t=0 regardless of geometry tweaks, as long as
    # the epithelium never reaches the very top row.
    LUMEN_SEED = None  # set in start(), needs p.DOMAIN_X/p.DOMAIN_Y

    def __init__(self, frequency=1):
        super().__init__(frequency)
        self.n_epithelial_initial = None
        self.last_mcs = None
        self.lumen_area_initial = None

    def start(self):
        self.n_epithelial_initial = (
            len(self.cell_list_by_type(self.EPITHELIALHEALTHY))
            + len(self.cell_list_by_type(self.EPITHELIUMDAMAGED))
        )
        self.LUMEN_SEED = (p.DOMAIN_X // 2, p.DOMAIN_Y - 1)
        self.lumen_area_initial = self.compute_lumen_area()
        print(f"MCS=     0 lumen area baseline: {self.lumen_area_initial} px")
        if 0 in self.CHECKPOINTS:
            self.check_sheet_integrity(0)

    def step(self, mcs):
        self.last_mcs = mcs
        n = (
            len(self.cell_list_by_type(self.EPITHELIALHEALTHY))
            + len(self.cell_list_by_type(self.EPITHELIUMDAMAGED))
        )
        assert n == self.n_epithelial_initial, (
            f"epithelial count drifted at MCS={mcs}: {n} vs {self.n_epithelial_initial}"
        )

        if mcs % 100 == 0:
            self.print_field_stats(mcs)
            self.print_displacement_stats(mcs)

        if mcs in self.CHECKPOINTS:
            self.check_sheet_integrity(mcs)

        if mcs in self.C_NORM_CHECKPOINTS:
            self.print_myofibroblast_c_norm_stats(mcs)
            self.print_interface_occupancy_stats(mcs)
            self.print_volume_frustration_stats(mcs)

    def finish(self):
        if self.last_mcs is not None:
            integrity = self.check_sheet_integrity(self.last_mcs)
            # Same off-by-one reason as check_sheet_integrity above: the true final
            # MCS isn't necessarily a multiple of 100, so step()'s mod-100 cadence
            # can miss it -- always get one last displacement/lumen-area reading here.
            self.print_displacement_stats(self.last_mcs)
            self.print_myofibroblast_c_norm_stats(self.last_mcs)
            self.print_interface_occupancy_stats(self.last_mcs)
            self.print_volume_frustration_stats(self.last_mcs)
            self.write_replicate_summary(self.last_mcs, integrity)

    # ------------------------------------------------------------

    SUMMARY_FILENAME = "replicates_summary.csv"

    def write_replicate_summary(self, mcs, integrity):
        """Gate B3 (2026-10-27): one row per run into ONE combined CSV, the Module 8.2
        log-writing-steppable pattern that turns a PSCAN of a dummy iter_count into a
        replicate table instead of N scattered logs. Inside a parameter scan, run_script's
        --output-dir is <scan root>/scan_iteration_N/output and --parameter-scan-iteration
        is set, so the file goes two levels up, at the scan root, and is appended under
        CC3D's own FileLock (several workers may finish at once). In an ordinary run it is
        written into that run's --output-dir instead. Columns are the quantities Gate B4
        reports (lab-notebook/2026/2026-10-27.md, criteria): final lumen area and its
        percent change vs the MCS-0 baseline, the cell counts, the subepithelial field
        means, repair events, divisions, and the clean-run checks."""
        from cc3d.CompuCellSetup import persistent_globals as pg
        from cc3d.core.filelock import FileLock

        out_dir = pg.output_directory
        if not out_dir:
            print("replicate summary: no output directory known, nothing written")
            return
        out_dir = Path(out_dir)
        scan_iteration = pg.parameter_scan_iteration
        in_scan = scan_iteration not in (None, "")
        summary_path = (out_dir.parent.parent if in_scan else out_dir) / self.SUMMARY_FILENAME

        lumen_pixels = self.flood_fill_lumen_pixels()
        lumen_area = len(lumen_pixels)
        pct = (100.0 * (lumen_area - self.lumen_area_initial) / self.lumen_area_initial
               if self.lumen_area_initial else 0.0)
        field_c = getattr(self.field, "C", None)
        lumen_c_max = max((field_c[x, y, 0] for x, y in lumen_pixels), default=0.0) if field_c is not None else 0.0

        def band_mean(name):
            field = getattr(self.field, name, None)
            if field is None:
                return 0.0
            total, n = 0.0, 0
            for x in range(self.dim.x):
                for y in range(p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX + 1):
                    total += field[x, y, 0]
                    n += 1
            return total / n if n else 0.0

        sv = self.shared_steppable_vars
        row = {
            "scan_iteration": scan_iteration if in_scan else "",
            "iter_count": sv.get("iter_count") if sv.get("iter_count") is not None else "",
            "rng_mode": sv.get("rng_mode", ""),
            "rng_seed": sv.get("rng_seed", ""),
            "final_mcs": mcs,
            "lumen_area_initial_px": self.lumen_area_initial,
            "lumen_area_px": lumen_area,
            "lumen_pct_change": f"{pct:.2f}",
            "n_Eh": len(self.cell_list_by_type(self.EPITHELIALHEALTHY)),
            "n_Ed": len(self.cell_list_by_type(self.EPITHELIUMDAMAGED)),
            "n_Fib": len(self.cell_list_by_type(self.FIBROBLAST)),
            "n_MyoF": len(self.cell_list_by_type(self.MYOFIBROBLAST)),
            "mean_G_subepithelial": f"{band_mean('G'):.4f}",
            "mean_C_subepithelial": f"{band_mean('C'):.4f}",
            "repair_events": sv.get("repair_events", 0),
            "fibroblast_divisions": sv.get("fibroblast_divisions", 0),
            "fragmented": integrity["fragmented"],
            "isolated": integrity["isolated"],
            "mesenchymal_overlap": integrity["overlap"],
            "lumen_C_max": f"{lumen_c_max:.4g}",
            "fibroblast_initial_number": p.FIBROBLAST_INITIAL_NUMBER,
            "repair_enhancement_carried": int(p.EPITHELIAL_REPAIR_CARRY_ODE_ENHANCEMENT),
        }
        # Gate B' Phase 1 (2026-10-31): P readouts, after the B4 columns and before the switch
        # columns. All three are defined in an off run too (0, 0, and the epithelial-state
        # analogue), so the column set does not depend on the switch.
        field_p = getattr(self.field, "P", None)
        lumen_p_mean = ((sum(field_p[x, y, 0] for x, y in lumen_pixels) / len(lumen_pixels))
                        if (field_p is not None and lumen_pixels) else 0.0)
        row["mean_P_band"] = f"{band_mean('P'):.4f}"
        row["lumen_P_mean"] = f"{lumen_p_mean:.4f}"
        row["P_analogue_H5"] = f"{sv.get('P_analogue_H5', 0.0):.4f}"
        # Gate B' Phase 2 (2026-11-02): damaged-cell lifetime (criterion 3, consumer 1's
        # direction check) as the mean of COMPLETED lifetimes (repaired cells; 0 when none,
        # the count is repair_events), plus the mean age of the cells still damaged at the
        # final MCS (censored; the informative number in a short run), and criterion 2's
        # run-mean |f_tissue - f_d|.
        n_life = sv.get("damaged_lifetime_n", 0)
        row["mean_damaged_lifetime_mcs"] = (f"{sv.get('damaged_lifetime_sum', 0) / n_life:.1f}"
                                            if n_life else "0")
        ages = [mcs - cell.dict.get("damaged_since", mcs)
                for cell in self.cell_list_by_type(self.EPITHELIUMDAMAGED)]
        row["mean_damaged_age_final_mcs"] = f"{sum(ages) / len(ages):.1f}" if ages else "0"
        row["mean_abs_fd_gap"] = f"{sv.get('fd_gap_mean', 0.0):.4f}"
        # Deterministic companion to the realized lifetime (see FibrosisModelSteppable): the
        # expected number of repairs over the run and the expected damaged lifetime
        # (damaged cell-MCS / expected repairs), which consumer 1 lengthens whether or not a
        # rare realized repair happened to move.
        exp_rep = sv.get("expected_repairs", 0.0)
        row["expected_repairs"] = f"{exp_rep:.4f}"
        row["expected_damaged_lifetime_mcs"] = (f"{sv.get('damaged_cell_mcs', 0) / exp_rep:.0f}"
                                                if exp_rep > 0 else "0")
        fib_mcs = sv.get("fib_cell_mcs", 0)
        row["p_tipped_gate_frac"] = (f"{sv.get('p_tipped_gate_mcs', 0) / fib_mcs:.4f}"
                                     if fib_mcs else "0")
        # Gate B' Phase 3 (2026-11-02): MMP readouts, the plan's Phase 3 done-when checks.
        # Band mean (what MMP_0 targets), the
        # flood-filled lumen mean, the field at myofibroblast COMs (the TIMP sink: lower than
        # the undepleted value at the same spot; compare against the band mean), and the field
        # at each epithelial cell's wall-side source pixels averaged by type ("highest under
        # damaged cells": damaged cells sit where P is highest, so their MMP output is too).
        # All five are 0 in an off run (the field is declared but never written).
        field_mmp = getattr(self.field, "MMP", None)
        if field_mmp is not None:
            lumen_mmp_mean = ((sum(field_mmp[x, y, 0] for x, y in lumen_pixels) / len(lumen_pixels))
                              if lumen_pixels else 0.0)
            myof_vals = []
            for cell in self.cell_list_by_type(self.MYOFIBROBLAST):
                x = max(0, min(int(round(cell.xCOM)), self.dim.x - 1))
                y = max(0, min(int(round(cell.yCOM)), self.dim.y - 1))
                myof_vals.append(field_mmp[x, y, 0])
            under = {self.EPITHELIALHEALTHY: [], self.EPITHELIUMDAMAGED: []}
            for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
                pixels, _ = epithelial_wall_source_pixels(self, cell)
                if pixels:
                    under[cell.type].append(sum(field_mmp[x, y, 0] for x, y in pixels) / len(pixels))
            mean_or_zero = lambda vals: (sum(vals) / len(vals)) if vals else 0.0
            row["mean_MMP_band"] = f"{band_mean('MMP'):.4f}"
            row["lumen_MMP_mean"] = f"{lumen_mmp_mean:.4f}"
            row["mean_MMP_at_myof_com"] = f"{mean_or_zero(myof_vals):.4f}"
            row["mean_MMP_under_damaged"] = f"{mean_or_zero(under[self.EPITHELIUMDAMAGED]):.4f}"
            row["mean_MMP_under_healthy"] = f"{mean_or_zero(under[self.EPITHELIALHEALTHY]):.4f}"
        else:
            for name in ("mean_MMP_band", "lumen_MMP_mean", "mean_MMP_at_myof_com",
                         "mean_MMP_under_damaged", "mean_MMP_under_healthy"):
                row[name] = "0"
        # Gate B' (2026-10-30): one column per switch, so every row states which of the
        # B' loops it ran with. Appended AFTER the Gate B4 columns, so the exact-regression
        # check (compare_replicates.py) can match the B4 CSV on its own columns and treat
        # these as extra. Column names are the switch names, lower-cased.
        for name in p.BPRIME_SWITCHES:
            row[name.lower()] = int(getattr(p, name))

        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(str(summary_path) + ".lock", timeout=60):
            write_header = not summary_path.exists()
            with open(summary_path, "a", newline="") as fout:
                writer = csv.DictWriter(fout, fieldnames=list(row.keys()))
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
        print(f"replicate summary row appended to {summary_path}")

    # ------------------------------------------------------------

    def print_field_stats(self, mcs):
        # Manual pixel loop, not np.array(field[:, :, 0]): the vectorized slice in
        # steppable-patterns.md crashes the C++ backend on this field object in this
        # CC3D 4.9.0 build (isolated by bisection). This matches the loop pattern
        # FibrosisModelSteppable.compute_mean_field already uses successfully.
        names = ["G", "C"]
        if p.P_FIELD_ENABLED:
            names.append("P")
        if p.MMP_FIELD_ENABLED:
            names.append("MMP")
        for name in names:
            field = getattr(self.field, name, None)
            if field is None:
                continue
            field_min = float("inf")
            field_max = float("-inf")
            total = 0.0
            n = 0
            for x in range(self.dim.x):
                for y in range(self.dim.y):
                    value = field[x, y, 0]
                    field_min = min(field_min, value)
                    field_max = max(field_max, value)
                    total += value
                    n += 1
            mean = total / n if n > 0 else 0.0
            print(
                f"MCS={mcs:6d} field {name}: min={field_min:.4g} "
                f"max={field_max:.4g} mean={mean:.4g}"
            )
            # Field C's lumen-specific max is reported in print_displacement_stats,
            # scoped to the flood-filled lumen region rather than a fixed y-band --
            # see flood_fill_lumen_pixels' docstring for why a y-cutoff is wrong here.

    # ------------------------------------------------------------

    def compute_epithelial_sheet_position(self):
        """Mean/min/max yCOM across the epithelial sheet (PRIORITY 0's displacement
        plan, step 1): the direct measure of whether/how much the sheet has moved
        from its p.EPITHELIAL_Y_MIN..MAX initialization band. min/max alongside mean
        catch uneven/buckled displacement, not just uniform drift -- relevant to
        plan step 6's "sheet doesn't buckle non-uniformly" acceptance check."""
        ys = [
            cell.yCOM
            for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED)
        ]
        if not ys:
            return None
        return sum(ys) / len(ys), min(ys), max(ys)

    # ------------------------------------------------------------

    def compute_epithelial_column_bounds(self):
        """Per-x-column (min_y, max_y) of pixels the epithelial sheet actually
        occupies right now. Used by check_sheet_integrity to test genuine overlap
        with the sheet's *current* footprint, not its p.EPITHELIAL_Y_MIN..MAX
        initialization band -- the same fixed-band-vs-live-position distinction
        flood_fill_lumen_pixels above already draws for the lumen. A fixed band
        can't tell a mesenchymal cell sitting in space the sheet has vacated
        (the column's live epithelial range has moved past it) from one actually
        wedged into the sheet where it now sits; confirmed 2026-09-22 as a real
        blind spot, not just a theoretical one -- the fixed-band check went from
        ~0 pre-rescale to 1-8 post-rescale with sheet integrity otherwise clean
        the whole time (cc3d_v1_todo.md, lab-notebook 2026-09-18/22)."""
        bounds = {}
        for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED):
            for ptd in self.get_cell_pixel_list(cell):
                x, y = ptd.pixel.x, ptd.pixel.y
                lo, hi = bounds.get(x, (y, y))
                bounds[x] = (min(lo, y), max(hi, y))
        return bounds

    # ------------------------------------------------------------

    def flood_fill_lumen_pixels(self):
        """Connected-region flood fill of Medium pixels reachable from a fixed
        seed point at the top-center of the domain (PRIORITY 0's displacement
        plan, step 2). Deliberately not a fixed y-cutoff region: a y-cutoff
        can't tell a Medium pocket pinched off from the main airway (should not
        count as open lumen) from a genuinely open passage, and can't handle the
        sheet buckling unevenly or displacing past the cutoff line (confirmed
        2026-08-13: the sheet's max yCOM reached ~83 against a p.LUMEN_MIN_Y of 80,
        so a y>=80 test partly scores legitimate epithelium-adjacent territory as
        "lumen"). This is the same quantity the Higham et al. validation target
        (validation_targets.md 3.5) is defined against -- connected open luminal
        area, not a raw region count -- and it's also the correct scope for any
        other "is this collagen actually in the open airway" check (see
        print_displacement_stats' lumen-collagen-max use below), for the same
        reason. 4-connected, same convention as _count_pixel_components below.
        If the seed pixel itself is occluded, the airway is fully closed at this
        checkpoint -- return the empty set rather than searching for a different
        seed, since that's the correct physical answer, not a measurement
        failure."""
        seed = self.LUMEN_SEED
        if self.cell_field[seed[0], seed[1], 0] is not None:
            return set()

        visited = {seed}
        stack = [seed]
        while stack:
            x, y = stack.pop()
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                nx, ny = nb
                if not (0 <= nx < self.dim.x and 0 <= ny < self.dim.y):
                    continue
                if nb in visited:
                    continue
                if self.cell_field[nx, ny, 0] is not None:
                    continue
                visited.add(nb)
                stack.append(nb)
        return visited

    def compute_lumen_area(self):
        return len(self.flood_fill_lumen_pixels())

    # ------------------------------------------------------------

    def print_displacement_stats(self, mcs):
        """PRIORITY 0's displacement plan, steps 1-2: actual sheet position and
        open lumen area, not just the field/sheet-integrity sanity checks above.
        Printed on the same cadence as print_field_stats so both read off the
        same checkpoints."""
        position = self.compute_epithelial_sheet_position()
        if position is not None:
            mean_y, min_y, max_y = position
            print(
                f"MCS={mcs:6d} epithelial sheet yCOM: mean={mean_y:.2f} "
                f"min={min_y:.2f} max={max_y:.2f} "
                f"(initialized {p.EPITHELIAL_Y_MIN}-{p.EPITHELIAL_Y_MAX})"
            )

        lumen_pixels = self.flood_fill_lumen_pixels()
        lumen_area = len(lumen_pixels)
        if self.lumen_area_initial:
            pct_change = 100.0 * (lumen_area - self.lumen_area_initial) / self.lumen_area_initial
        else:
            pct_change = 0.0
        print(
            f"MCS={mcs:6d} lumen area: {lumen_area} px "
            f"({pct_change:+.1f}% vs MCS=0 baseline of {self.lumen_area_initial} px)"
        )

        # Scoped to the flood-filled lumen pixels themselves, not a fixed y-band --
        # a fixed y>=p.LUMEN_MIN_Y cutoff double-counts as "leaked into the lumen"
        # any collagen sitting under an epithelial cell that has genuinely
        # displaced past that line without ever breaching (confirmed 2026-08-13,
        # see flood_fill_lumen_pixels' docstring). 0.0 when the lumen is fully
        # closed (empty pixel set), matching compute_lumen_area's convention.
        field_c = getattr(self.field, "C", None)
        if field_c is not None:
            lumen_collagen_max = 0.0
            for x, y in lumen_pixels:
                lumen_collagen_max = max(lumen_collagen_max, field_c[x, y, 0])
            print(f"MCS={mcs:6d} field C lumen max (flood-filled lumen): {lumen_collagen_max:.4g}")

    # ------------------------------------------------------------

    def print_myofibroblast_c_norm_stats(self, mcs):
        """PRIORITY 0 plan step 3a (cc3d_v1_todo.md): per-myofibroblast local_C
        and c_norm(C) distribution, not just the aggregate field mean/max
        print_field_stats already logs. Distinguishes the two live hypotheses
        for why lumen narrowing plateaus by MCS ~300-400: (a) c_norm is already
        saturating near 1 by then (p.K_C=20 too small against local C), so
        targetVolume = p.TARGET_VOLUME_MYOF * (1 + p.MYOF_TARGET_VOLUME_GROWTH_FACTOR
        * c_norm) stops growing even though field C keeps accumulating, vs.
        (b) c_norm is still climbing but the sheet has reached a new mechanical
        equilibrium (e.g. against the 2026-08-13 FPP cohesion links) that
        targetVolume growth alone can't push past. Reads cell.dict["local_C"],
        populated this same MCS by FibrosisModelSteppable.read_local_fields()
        (registered before this steppable, so the value is current)."""
        c_values = [
            cell.dict.get("local_C", 0.0)
            for cell in self.cell_list_by_type(self.MYOFIBROBLAST)
        ]
        if not c_values:
            print(f"MCS={mcs:6d} myofibroblast c_norm: no myofibroblasts yet")
            return

        c_norms = [c_norm(c) for c in c_values]
        n = len(c_values)
        n_saturated = sum(1 for cn in c_norms if cn >= 0.9)
        print(
            f"MCS={mcs:6d} myofibroblast local_C: n={n} "
            f"min={min(c_values):.4g} mean={sum(c_values)/n:.4g} max={max(c_values):.4g} | "
            f"c_norm: min={min(c_norms):.4g} mean={sum(c_norms)/n:.4g} max={max(c_norms):.4g} "
            f"| n(c_norm>=0.9)={n_saturated}/{n}"
        )

    # ------------------------------------------------------------

    # Width of the band directly below the epithelium (2026-09-03, PRIORITY 0
    # plan step 3a follow-up): both the c_norm-saturation and FPP-link
    # mechanical-equilibrium hypotheses were tested and ruled out/minor (see
    # cc3d_v1_todo.md) -- neither explains why lumen narrowing plateaus by MCS
    # ~500 while field C and the myofibroblast population keep growing.
    # Leading hypothesis: a CPM cell only transmits pushing pressure to
    # neighbors it's actually adjacent to, so the *aggregate* subepithelial
    # occupancy (~23% at MCS 2999 in the diagnostic run) is the wrong number --
    # what matters is occupancy in the narrow band actually touching the
    # epithelial sheet. 10 rows, same order as p.EPITHELIAL_CELL_HEIGHT (6) and
    # p.RECRUITMENT_BAND_WIDTH (5): wide enough to average over a few cell
    # diameters of interface, narrow enough to stay a genuine "at the
    # boundary" measure rather than drifting back toward the bulk number.
    INTERFACE_BAND_WIDTH = 10

    def print_interface_occupancy_stats(self, mcs):
        """Cell-pixel occupancy fraction in the narrow band directly below the
        epithelium (y = p.SUBEPITHELIAL_Y_MAX - INTERFACE_BAND_WIDTH + 1 ..
        p.SUBEPITHELIAL_Y_MAX) vs. the whole subepithelial compartment, plus the
        single row of pixels actually touching the epithelium (y =
        p.SUBEPITHELIAL_Y_MAX only). Added 2026-09-03 after a
        p.FIBROBLAST_INITIAL_NUMBER=300 scratch test (3.75x baseline) pushed the
        10-row band to ~70% occupied without moving the volume-frustration
        signature (print_volume_frustration_stats) off its unstressed baseline
        -- the 10-row average may be diluting out whatever is happening right
        at the boundary. If the boundary row itself is still short of
        confluence even when the wider band reads ~70%, that's the real
        "not enough cells where it counts" answer, distinct from "not enough
        cells overall" (mean field C / population counts) or a gain/mechanical
        limit (both ruled out above)."""
        y_max = p.SUBEPITHELIAL_Y_MAX
        y_min_interface = max(p.SUBEPITHELIAL_Y_MIN, y_max - self.INTERFACE_BAND_WIDTH + 1)

        def occupancy(y_lo, y_hi):
            occupied = 0
            total = 0
            for x in range(self.dim.x):
                for y in range(y_lo, y_hi + 1):
                    total += 1
                    if self.cell_field[x, y, 0] is not None:
                        occupied += 1
            return occupied, total

        interface_occupied, interface_total = occupancy(y_min_interface, y_max)
        bulk_occupied, bulk_total = occupancy(p.SUBEPITHELIAL_Y_MIN, y_max)
        boundary_occupied, boundary_total = occupancy(y_max, y_max)

        interface_frac = interface_occupied / interface_total if interface_total else 0.0
        bulk_frac = bulk_occupied / bulk_total if bulk_total else 0.0
        boundary_frac = boundary_occupied / boundary_total if boundary_total else 0.0
        print(
            f"MCS={mcs:6d} interface occupancy (y={y_min_interface}-{y_max}): "
            f"{interface_occupied}/{interface_total} px ({100.0*interface_frac:.1f}%) | "
            f"bulk subepithelial occupancy (y={p.SUBEPITHELIAL_Y_MIN}-{y_max}): "
            f"{bulk_occupied}/{bulk_total} px ({100.0*bulk_frac:.1f}%) | "
            f"boundary row occupancy (y={y_max} only): "
            f"{boundary_occupied}/{boundary_total} px ({100.0*boundary_frac:.1f}%)"
        )

    # ------------------------------------------------------------

    def print_volume_frustration_stats(self, mcs):
        """PRIORITY 0 plan step 3a, third round (2026-09-03): saturation, the FPP
        links, and interface-band under-occupancy have all been tested and
        ruled out/minor as the plateau's cause (cc3d_v1_todo.md) -- the
        interface band fills to ~35-38% occupied by MCS ~2000 while lumen
        narrowing stays flat from MCS ~300-500 onward. This checks the
        remaining live question: is that growing local crowding actually
        generating pressure that loses the energy competition against the
        epithelium (myofibroblasts volume-frustrated, cell.volume trailing
        cell.targetVolume -- real force, just not enough of it), or is it being
        absorbed by lateral rearrangement without ever seriously contesting the
        boundary (myofibroblasts sit close to their targetVolume regardless --
        no real pressure on the sheet despite the crowding)? Cross-referenced
        against the epithelium's own volume/targetVolume ratio: compression
        there (volume trailing target) would confirm force is reaching the
        sheet even if it isn't enough to move it; an untouched ratio (~1.0)
        would mean the sheet isn't even being contested yet."""
        y_min_interface = max(p.SUBEPITHELIAL_Y_MIN, p.SUBEPITHELIAL_Y_MAX - self.INTERFACE_BAND_WIDTH + 1)

        myof_ratios = [
            cell.volume / cell.targetVolume
            for cell in self.cell_list_by_type(self.MYOFIBROBLAST)
            if cell.targetVolume > 0 and cell.yCOM >= y_min_interface
        ]
        epi_ratios = [
            cell.volume / cell.targetVolume
            for cell in self.cell_list_by_type(self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED)
            if cell.targetVolume > 0
        ]

        if myof_ratios:
            n = len(myof_ratios)
            print(
                f"MCS={mcs:6d} interface myofibroblast volume/targetVolume: n={n} "
                f"min={min(myof_ratios):.3f} mean={sum(myof_ratios)/n:.3f} max={max(myof_ratios):.3f}"
            )
        else:
            print(f"MCS={mcs:6d} interface myofibroblast volume/targetVolume: no myofibroblasts in band")

        if epi_ratios:
            n = len(epi_ratios)
            print(
                f"MCS={mcs:6d} epithelial volume/targetVolume: n={n} "
                f"min={min(epi_ratios):.3f} mean={sum(epi_ratios)/n:.3f} max={max(epi_ratios):.3f}"
            )

    # ------------------------------------------------------------

    def check_sheet_integrity(self, mcs):
        """No epithelial cell fragments into disconnected pixel groups, and every
        epithelial cell still borders at least one other epithelial cell."""
        epithelial_types = (self.EPITHELIALHEALTHY, self.EPITHELIUMDAMAGED)
        fragmented = []
        isolated = []

        for cell in self.cell_list_by_type(*epithelial_types):
            if self._count_pixel_components(cell) > 1:
                fragmented.append(cell.id)

            has_epithelial_neighbor = False
            for neighbor, _ in self.get_cell_neighbor_data_list(cell):
                if neighbor is not None and neighbor.type in epithelial_types:
                    has_epithelial_neighbor = True
                    break
            if not has_epithelial_neighbor:
                isolated.append(cell.id)

        print(
            f"MCS={mcs:6d} sheet integrity: fragmented={len(fragmented)} "
            f"isolated={len(isolated)}"
        )
        if fragmented:
            print(f"  fragmented cell ids: {fragmented}")
        if isolated:
            print(f"  isolated cell ids: {isolated}")

        # Pixel-level overlap with the sheet's current footprint (see
        # compute_epithelial_column_bounds' docstring), not yCOM against the fixed
        # p.EPITHELIAL_Y_MIN..MAX initialization band: a genuinely displaced sheet
        # leaves the old band's space behind, and a mesenchymal cell sitting there
        # is not an intrusion. A cell counts here only if one of its own pixels
        # falls within the sheet's actual y-span in that same column right now.
        column_bounds = self.compute_epithelial_column_bounds()
        invaded_ids = []
        for cell in self.cell_list_by_type(self.FIBROBLAST, self.MYOFIBROBLAST):
            for ptd in self.get_cell_pixel_list(cell):
                x, y = ptd.pixel.x, ptd.pixel.y
                bound = column_bounds.get(x)
                if bound is not None and bound[0] <= y <= bound[1]:
                    invaded_ids.append(cell.id)
                    break
        print(
            f"MCS={mcs:6d} mesenchymal cells overlapping the epithelial sheet's "
            f"current footprint: {len(invaded_ids)}"
        )
        if invaded_ids:
            print(f"  overlapping cell ids: {invaded_ids}")
        return {"fragmented": len(fragmented), "isolated": len(isolated),
                "overlap": len(invaded_ids)}

    # ------------------------------------------------------------

    def _count_pixel_components(self, cell):
        """4-connected flood fill over a cell's own pixel set."""
        pixels = {(ptd.pixel.x, ptd.pixel.y) for ptd in self.get_cell_pixel_list(cell)}
        if not pixels:
            return 0

        remaining = set(pixels)
        components = 0
        while remaining:
            components += 1
            stack = [next(iter(remaining))]
            while stack:
                p = stack.pop()
                if p not in remaining:
                    continue
                remaining.discard(p)
                x, y = p
                for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if nb in remaining:
                        stack.append(nb)
        return components