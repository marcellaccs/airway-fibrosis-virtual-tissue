
from cc3d import CompuCellSetup
        


from M1_M2Steppables import ConstraintInitializerSteppable

CompuCellSetup.register_steppable(steppable=ConstraintInitializerSteppable(frequency=1))

# from M1_M2Steppables import DeathSteppable

# CompuCellSetup.register_steppable(steppable=DeathSteppable(frequency=1))


# from M1_M2Steppables import GrowthSteppable

# CompuCellSetup.register_steppable(steppable=GrowthSteppable(frequency=1))



        
# from M1_M2Steppables import M1M2MitosisSteppable
# CompuCellSetup.register_steppable(steppable=M1M2MitosisSteppable(frequency=1))


        
from M1_M2Steppables import TransitionSteppable
CompuCellSetup.register_steppable(steppable=TransitionSteppable(frequency=1))


        


CompuCellSetup.run()
