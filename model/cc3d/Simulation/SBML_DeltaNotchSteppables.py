from cc3d.cpp.PlayerPython import * 
from cc3d import CompuCellSetup
from cc3d.core.PySteppables import *
import numpy as np

class DeltaNotchSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self,frequency)
        self.track_cell_level_scalar_attribute(field_name='Notch', attribute_name='N')
        self.track_cell_level_scalar_attribute(field_name='Delta', attribute_name='D')

    def start(self):       
        model_string = """
        //Reactions
        J1: -> N; Davg^k/(a+Davg^k)-N;
        J2: ->D; v*(1/(1+b*N^h)-D);
        //Species Initializations
        Davg = 0.4;
        D = 0.5;
        N = 0.5;
        //Parameters
        k = 2;
        a = 0.01;
        v = 1;
        b = 100;
        h = 2;
        """   

        self.add_antimony_to_cell_types(model_string=model_string, model_name='DN', cell_types=[self.CELLA], step_size=0.2) 
                     
        for cell in self.cell_list:
            cell.targetVolume = 50
            cell.lambdaVolume = 2
            cell.sbml.DN['D'] = np.random.uniform(0.9,1.0)
            cell.sbml.DN['N'] = np.random.uniform(0.9,1.0)
            
    def step(self,mcs):
        self.timestep_sbml()
        for cell in self.cell_list:
            Davg=0; nn=0.0
            
            for (neighbor,common_surface_area) in self.get_cell_neighbor_data_list(cell):
                if neighbor:
                    Davg+=neighbor.sbml.DN['D']
                    nn+=1.0
            if nn:
                cell.sbml.DN['Davg']=Davg/nn
            cell.dict['D']=cell.sbml.DN['D']
            cell.dict['N']=cell.sbml.DN['N']
#       

            