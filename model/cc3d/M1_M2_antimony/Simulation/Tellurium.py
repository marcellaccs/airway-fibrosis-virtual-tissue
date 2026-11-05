
from cc3d import CompuCellSetup
        

from TelluriumSteppables import TelluriumSteppable

CompuCellSetup.register_steppable(steppable=TelluriumSteppable(frequency=1))


CompuCellSetup.run()
