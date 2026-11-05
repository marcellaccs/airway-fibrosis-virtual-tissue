from cc3d.core.PySteppables import *

## Type Tellurium Model Here
m1m2 = '''
    // Equations
    //J1: -> M1; k*M1;
    //J2: M1 -> ; mu*M1;
    //J3: -> M2; k*M2;
    //J4: M2 -> ; mu*M2;
    
    // Transition between phenotypes
    J1: M1 -> M2; k1*M1*A^2/(a^2+A^2) - k2*M2*P^2/(b^2+P^2);
    
    // Secretion of pro-inflammatory cytokines induced by LPS, inhibited by anti-inflammatory
    J2: -> P; k3*M1*L*d^2/(A^2+d^2);
    
    // Secretion of anti-inflammatory cytokines, self-inhibition
    J3: -> A; k4*M2*d^2/(A^2+d^2);

    // Parameters
    //k = 0.1; 
    //mu = 0.05;
    k1 = 0.2;
    k2 = 0.2;
    k3 = 0.02;
    k4 = 0.02;
    a = 2;
    b = 2;
    c = 2;
    d = 2;
    L = 0 ;

    // Initial Conditions
    M1 = 6;
    M2 = 6;
    P = 0.1; // Add an initial value for P
    A = 0.1; // Add an initial value for A
    
    // Events
    // E1: at (M1 < 0): M1 = 0;
    // E2: at (M2 < 0): M2 = 0;
'''

Variables = {'M1':'red','M2':'blue'}

class TelluriumSteppable(SteppableBasePy):
    def __init__(self,frequency=1):
        SteppableBasePy.__init__(self,frequency)

    def start(self):
        self.add_free_floating_antimony(model_string=m1m2, model_name='m1m2', step_size=0.1, integrator = 'gillespie')
        #self.sbml.model['k1']=2.0
        self.plot_win = self.add_new_plot_window(title='Macrophage Population Level Phenotype',
                                                 x_axis_title='Time',
                                                 y_axis_title='Macrophage Concentration', 
                                                 x_scale_type='linear', 
                                                 y_scale_type='linear',
                                                 grid=True,
                                                 config_options={'legend': True})
        for var in Variables:
            self.plot_win.add_plot(var, style='Lines', color=Variables[var], size=5)
        
        
    def step(self,mcs):
        for var in Variables:
            self.plot_win.add_data_point(var, mcs, self.sbml.m1m2[var])
        
        self.timestep_sbml()


    def finish(self):
        """
        Finish Function is called after the last MCS
        """


        