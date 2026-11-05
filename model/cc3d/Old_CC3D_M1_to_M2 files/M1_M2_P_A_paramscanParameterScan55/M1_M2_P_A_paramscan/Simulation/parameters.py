
By='M Torres'
LastModified=''


#Var Name                    Units                       Comment                                       Reference
##Biological Parameters#######
model_width_cells=10           #units cell widths          dim of the simulation in cell widths          arbitrary
cell_width=10                #microns                    width of a macrophage in microns (10-30)      Krombach 1997         
p_max=  0.05                      #micrograms per mL         maximum secretion rate of P by M1           arbitrary


##Model Parameters#######
pixels_per_micron=1.0        #pixels/micron              conversion factor btwn biology & model        arbitrary

##Parameter Conversions#######
model_width_pixels = int(model_width_cells*cell_width*pixels_per_micron)
                             #pixels                     size of model window, x & y            
cell_width_pixels = int(cell_width*pixels_per_micron)
                             #pixels                     width of individual cell  
#initial_cell_field_radius =

# 2D model####
cell_targetVolume = (cell_width_pixels)**2