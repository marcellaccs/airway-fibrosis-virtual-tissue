from cc3d.core.PySteppables import *
import numpy as np
import random as rd
import parameters as p

P1 = 0.3 #arbitrary probability M1 transitions to M1
P2 = 0.05 #arbitrary probability M2 transitions to M2



class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self,frequency)

    def start(self):
        self.plot_win = self.add_new_plot_window(title='Cytokine Concentration',
                                                     x_axis_title='MonteCarlo Step (MCS)',
                                                     y_axis_title='Concentration', x_scale_type='linear', y_scale_type='linear',
                                                     grid=False)
            
        self.plot_win.add_plot("P", style='Lines', color='red', size=5)
        self.plot_win.add_plot("A", style='Lines', color='blue', size=5)

        for cell in self.cell_list:

            cell.targetVolume = p.cell_targetVolume
            cell.lambdaVolume = 2.0
        
        
        
        
            
        
    def step(self,mcs):
        # iterating over cells of type 1
        # list of  cell types (capitalized)
        # arguments are (name of the data series, x, y)
        secretor = self.get_field_secretor("P")
        total_amount_P = secretor.totalFieldIntegral()
        secretor = self.get_field_secretor("A")
        total_amount_A = secretor.totalFieldIntegral()
        
        self.plot_win.add_data_point("P", mcs, total_amount_P)
        

        self.plot_win.add_data_point("A", mcs, total_amount_A)
        
        
        
        
        
        for cell in self.cell_list_by_type(self.M1):
            # Make sure Secretion plugin is loaded
            # make sure this field is defined in one of the PDE solvers
            # you may reuse secretor for many cells. Simply define it outside the loop
            secretor = self.get_field_secretor("P")
            secretor_LPS = self.get_field_secretor("LPS")
            amount_seen_LPS = secretor_LPS.amountSeenByCell(cell)
            amount_seen_A = secretor.amountSeenByCell(cell)
            #secretor.secreteInsideCellAtBoundary(cell, p.p_max*(amount_seen_LPS/100)**2/((amount_seen_LPS/100)**2+2**2))
            secretor.secreteInsideCellAtBoundary(cell, p.p_max*(amount_seen_LPS)*1/(1+amount_seen_A)**2)
            print("amount seen LPS=",amount_seen_LPS)
            #print("amount seen LPS by M1=",p.p_max*(amount_seen_LPS**4/(amount_seen_LPS**4+50**4)))
            # tot_amount = secretor.secreteInsideCellAtBoundaryTotalCount(cell, 300).tot_amount
            
        for cell in self.cell_list_by_type(self.M2):
            # Make sure Secretion plugin is loaded
            # make sure this field is defined in one of the PDE solvers
            # you may reuse secretor for many cells. Simply define it outside the loop
            secretor = self.get_field_secretor("A")
            amount_seen_A = secretor.amountSeenByCell(cell)
            secretor.secreteInsideCellAtBoundary(cell, 0.05*1/(1+amount_seen_A)**2 )
            
            # tot_amount = secretor.secreteInsideCellAtBoundaryTotalCount(cell, 300).tot_amount    
            
        
        
    

        # # alternatively if you want to make growth a function of chemical concentration uncomment lines below and comment lines above        

        # field = self.field.CHEMICAL_FIELD_NAME
        
        # for cell in self.cell_list:
            # concentrationAtCOM = field[int(cell.xCOM), int(cell.yCOM), int(cell.zCOM)]

            # # you can use here any fcn of concentrationAtCOM
            # cell.targetVolume += 0.01 * concentrationAtCOM       

        
# class DeathSteppable(SteppableBasePy):
    # def __init__(self, frequency=1):
        # SteppableBasePy.__init__(self, frequency)

    
    # def step(self, mcs):
        # if mcs == 500:
            # for cell in self.cell_list:
                # if rd.random() < 0.2:
                    # cell.targetVolume=0
                    # cell.lambdaVolume=100
                    # if cell.type == self.M1:
                        # self.shared_steppable_vars['NM1'] -= 1
                    # elif cell.type == self.M2:
                        # self.shared_steppable_vars['NM2'] -= 1
                    
        
# class M1M2MitosisSteppable(MitosisSteppableBase):
    # def __init__(self,frequency=1):
        # MitosisSteppableBase.__init__(self,frequency)
        # #self.cell_counts = {'M1' : 0, 'M2' : 0}
        
        
    # def start(self):
        # # self.shared_steppable_vars['NM1'] = 0
        # # self.shared_steppable_vars['NM2'] = 0
        
        # # self.plot_win = self.add_new_plot_window(title='Number of Cells',
                                                     # # x_axis_title='MonteCarlo Step (MCS)',
                                                     # # y_axis_title='Number', x_scale_type='linear', y_scale_type='linear',
                                                     # # grid=False)
            
        # # self.plot_win.add_plot("M1", style='Lines', color='red', size=5)
        # # self.plot_win.add_plot("M2", style='Lines', color='blue', size=1)
    
    

    # def step(self, mcs):

        # cells_to_divide=[]
        # for cell in self.cell_list:
            # if cell.volume>50:
                # cells_to_divide.append(cell)

        # for cell in cells_to_divide:

            # self.divide_cell_random_orientation(cell)
            # # Other valid options
            # # self.divide_cell_orientation_vector_based(cell,1,1,0)
            # # self.divide_cell_along_major_axis(cell)
            # # self.divide_cell_along_minor_axis(cell)

            # # arguments are (name of the data series, x, y)
        # self.plot_win.add_data_point("M1", mcs, self.shared_steppable_vars['NM1'])
        # self.plot_win.add_data_point("M2", mcs, self.shared_steppable_vars['NM2'])
            
            


    # def update_attributes(self):
        # # reducing parent target volume
        # self.parent_cell.targetVolume /= 2.0                  

        # self.clone_parent_2_child()            

        # # for more control of what gets copied from parent to child use cloneAttributes function
        # # self.clone_attributes(source_cell=self.parent_cell, target_cell=self.child_cell, no_clone_key_dict_list=[attrib1, attrib2]) 
        
        # if self.parent_cell.type==self.M1:
            # self.child_cell.type=self.M2
            # #self.cell_counts['M2'] +=1
            # self.shared_steppable_vars['NM2'] +=1
        # else:
            # self.child_cell.type=self.M1
            # #self.cell_counts['M1'] +=1
            # self.shared_steppable_vars['NM1'] +=1
            

        
class TransitionSteppable(SteppableBasePy):
    def __init__(self, frequency=1):
        '''
        constructor
        '''
        SteppableBasePy.__init__(self, frequency)
        # PLACE YOUR CODE BELOW THIS LINE


    def start(self):
        '''
        called once before first MCS
        '''
        # PLACE YOUR CODE BELOW THIS LINE
        self.shared_steppable_vars['NM1'] = len(self.cell_list_by_type(self.M1))
        self.shared_steppable_vars['NM2'] = len(self.cell_list_by_type(self.M2))
        
        self.plot_win = self.add_new_plot_window(title='Number of Cells',
                                                     x_axis_title='MonteCarlo Step (MCS)',
                                                     y_axis_title='Number', x_scale_type='linear', y_scale_type='linear',
                                                     grid=True,
                                                     config_options={'legend': True})
            
        self.plot_win.add_plot("M1", style='Lines', color='red', size=5)
        self.plot_win.add_plot("M2", style='Lines', color='blue', size=5)
        #print("TransitionSteppable: This function is called once before simulation")
        
        import os
        fileDir = os.path.dirname(os.path.abspath(__file__)) # this is the "Simulation" folder 
        fileDirUp = os.path.dirname(fileDir) # this is one directory up (project main folder) 
        fileName2 = os.path.join(fileDirUp,"logfile2.txt") # out filename with path

        self.file2 = open(fileName2,"a") # APPENDING 
        if self.file2 is None:
            print('couldn"t open file')
            exit()
                
     
        self.file2.write("Start of the log file in the project's directory\n")
        
        
    def step(self, mcs):
        '''
        called every MCS or every "frequency" MCS (depending how it was instantiated in the main Python file)
        '''
        # PLACE YOUR CODE BELOW THIS LINE
        # iterating over cells of type 1
        # list of  cell types (capitalized)
        for cell in self.cell_list_by_type(self.M2):
            # Make sure Secretion plugin is loaded
            # make sure this field is defined in one of the PDE solvers
            secretor = self.get_field_secretor("P")
            amount_seen_P = secretor.amountSeenByCell(cell)
            print("amount seen of P by M2=",amount_seen_P)
            if amount_seen_P > 40:
                cell.type=self.M1
                self.shared_steppable_vars['NM2'] -=1
                self.shared_steppable_vars['NM1'] +=1
        
        for cell in self.cell_list_by_type(self.M1):
            secretor = self.get_field_secretor("A")
            amount_seen_A = secretor.amountSeenByCell(cell)
            print("amount seen of A by M1=",amount_seen_A)
            
            if amount_seen_A > 45:
                
                #print("TransitionSteppable: This function is called once before simulation")
                cell.type=self.M2
                self.shared_steppable_vars['NM1'] -=1
                self.shared_steppable_vars['NM2'] +=1
                
        
        #outLine = 'some stuff'
        outLine = "LPS_conc" + "\t" + "N_M1" + "\t" + "N_M2" + "\n"
        outLine += str({{LPS_conc}}) + "\t" + str(self.shared_steppable_vars['NM1']) + "\t" + str(self.shared_steppable_vars['NM2'])
        print(outLine)
        self.file2.write(outLine)
                
        

        self.plot_win.add_data_point("M1", mcs, self.shared_steppable_vars['NM1'])
        self.plot_win.add_data_point("M2", mcs, self.shared_steppable_vars['NM2'])
def finish(self):
    # Writing scan parameters together with cell counts to an output file
    
    self.file2.close() 
    
    # Append new values to the same file
    #file_obj, file_path = self.open_file_in_parameter_scan_main_output_folder("Pscan_log.csv", mode='a')    
    
    # if file_obj is None:
        # return
 
    # print("File Path:", file_path)
    # print(outLine, file=file_obj)
    # file_obj.close()