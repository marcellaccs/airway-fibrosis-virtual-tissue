from cc3d import CompuCellSetup

from .Subepithelial_FibrosisSteppables import (
    TissueInitializationSteppable,
    ODESignalSteppable,
    FibrosisModelSteppable,
    FibroblastMitosisSteppable,
    DiagnosticsSteppable
)

# ---------------------------------------------------------
# Inicializacion del tejido
# ---------------------------------------------------------
CompuCellSetup.register_steppable(
    steppable=TissueInitializationSteppable(frequency=1)
)

# ---------------------------------------------------------
# ODE signal (S_M2 pedestal on G) -- before FibrosisModelSteppable so
# read_local_fields() sees the field already updated within the same MCS
# ---------------------------------------------------------
CompuCellSetup.register_steppable(
    steppable=ODESignalSteppable(frequency=1)
)

# ---------------------------------------------------------
# Dinamica principal del modelo
# ---------------------------------------------------------
CompuCellSetup.register_steppable(
    steppable=FibrosisModelSteppable(frequency=1)
)

# ---------------------------------------------------------
# GF-gated fibroblast mitosis -- after FibrosisModelSteppable so a fibroblast's
# targetVolume growth (set this same MCS if its cell-cycle clock just completed)
# is what gets checked against the division-trigger threshold.
# ---------------------------------------------------------
CompuCellSetup.register_steppable(
    steppable=FibroblastMitosisSteppable(frequency=1)
)

# ---------------------------------------------------------
# Verification (Group 1)
# ---------------------------------------------------------
CompuCellSetup.register_steppable(
    steppable=DiagnosticsSteppable(frequency=1)
)

# ---------------------------------------------------------
# Ejecutar simulacion
# ---------------------------------------------------------
CompuCellSetup.run()