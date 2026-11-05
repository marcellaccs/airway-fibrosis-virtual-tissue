from cc3d import CompuCellSetup       

from SBML_DeltaNotchSteppables import *

CompuCellSetup.register_steppable(steppable=DeltaNotchSteppable(frequency=1))

CompuCellSetup.run()
