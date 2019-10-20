"""
This script should to modified as needed to generate multiple mx3 files, which could be batch submitted to NSCC or ran on simple_job_server.
The script should be:
1. Self contained (should not need external files)
2. Copied and pasted for new jobs/task
3. Appropriated named, documented and version-controlled such that it is easy for anyone to modify and generate new simulation files.
"""

import textwrap
import os
import re
import random as rand
from copy import deepcopy
from dataclasses import dataclass

def DA_matrix():

	# ovf path
	mx3_output_path = r'C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\33series - extra simulations\mx3-files'

	sim_batch_name = '33dSKML_st009'
	effective_medium_scaling = 1/3

	@dataclass
	# parameter space to sweep
	class ParamsSweep:
		# before effective medium scaling
		Aex: [float] = None #  pJ/m
		Dind: [float] = None # mJ/M2

	# this generates a N-dimensional parameter space without the need for N-level nesting of for loops
	params_sweep =  ParamsSweep()
	params_sweep.Aex = [12.3, 12.5, 12.7, 12.9, 13.1, 13.3] #pJ/m
	params_sweep.Dind = [1.7, 1.9, 2.1, 2.3, 2.5] # mJ/M2
	ParamsSweepList = flatten(outer_product_object_list(params_sweep))

	# ensure path exist
	if not os.path.exists(mx3_output_path):
		os.makedirs(mx3_output_path)

	for params in ParamsSweepList:

		sim_name = sim_batch_name + '_Aex_%g_Dind_%.3g'%(params.Aex, params.Dind)
		mumax_file_str = os.path.join(mx3_output_path, sim_name+'.mx3')

		mumax_commands = textwrap.dedent('''\
		Mega :=1e6
		Pico :=1e-12
		Nano :=1e-9
		Mili :=1e-3

		// Micromagnetic variables
		Aex_var := %.5g*Pico  // Exchange in J/m^3
		Msat_var := 0.351360317*Mega  //Saturation magnetisation in A/m
		Ku1_var	:= 0.0968933*Mega  // Anistropy in J/m^3
		Dbulk_var  := 0.000000*Mili  //Bulk DMI in J/m^2
		Dind_var  := %.5g*Mili  //Interfacial DMI in J/m^2

		// Setting micromagnetic parameters for Region 0: Non-magnetic
		Aex.SetRegion(0, 0)
		Msat.SetRegion(0, 0)
		Ku1.SetRegion(0, 0)
		Dbulk.SetRegion(0, 0)
		Dind.SetRegion(0, 0)

		// Setting micromagnetic parameters for Region 1: FM 1
		Aex.SetRegion(1, Aex_var)
		Msat.SetRegion(1, Msat_var)
		Ku1.SetRegion(1, Ku1_var)
		Dbulk.SetRegion(1, Dbulk_var)
		Dind.SetRegion(1, Dind_var)

		// Setting micromagnetic parameters for Region 2: FM 2
		Aex.SetRegion(2, Aex_var)
		Msat.SetRegion(2, Msat_var)
		Ku1.SetRegion(2, Ku1_var)
		Dbulk.SetRegion(2, Dbulk_var)
		Dind.SetRegion(2, Dind_var)

		// Micromagnetic parameters for all regions
		alpha  =0.050000		 // Damping
		AnisU = vector(0, 0, 1) //Uniaxial anisotropy direction
		B_ext = vector(0, 0, 0.000000) //in Teslas

		// Physical size
		size_X	:=2048.000000 //sim_param.phy_size.x
		size_Y	:=2048.000000
		size_Z	:=42.000000

		// Total number of simulations cells
		Nx	:=512 //sim_param.grid_size.x
		Ny	:=512
		Nz	:=14

		// PBC, if any
		PBC_x :=0 //sim_param.pbc.x
		PBC_y :=0
		PBC_z :=0

		z_single_rep_thickness := 1 // thickness of single repetition in number of cells in z
		z_layer_rep_num := 14 //this many repetitions
		num_of_regions := 2 // number of FM regions (exclude NM region 0)

		//SetPBC(PBC_x, PBC_y, PBC_z)
		SetGridsize(Nx, Ny, Nz)
		SetCellsize(size_X*Nano/Nx, size_Y*Nano/Ny, size_Z*Nano/Nz)

		//geometry
		for layer_number:=0; layer_number<Nz; layer_number+= z_single_rep_thickness {
			// set adjacent layers to be of different regions
			// so that we could set interlayer exchange coupling
			// layer 1: FM1, layer 2: FM2
			defRegion(Mod(layer_number, num_of_regions)+1, layer(layer_number))
		}

		// interlayer exchange scaling
		ext_scaleExchange(1, 2, 0.000000)

		TableAdd(B_ext)
		TableAdd(E_Total)
		TableAdd(E_anis)
		TableAdd(E_demag)
		TableAdd(E_exch)
		TableAdd(E_Zeeman)
		tableAdd(ext_topologicalcharge)
		TableAdd(Temp)
		TableAdd(LastErr)
		OutputFormat = OVF1_TEXT

		// initialise with +z uniform mag since M(H) loop with start at saturation
		m.setRegion(0, Uniform(0, 0, 0))
		m.setRegion(1, Uniform(0, 0, 1))
		m.setRegion(2, Uniform(0, 0, 1))
		tablesave()

		// apply a short burst of thermal fluctuations to allow the system to cross small energy barriers
		SetSolver(2) // Heun
		ThermSeed(%d) // Set a random seed for thermal noise
		FixDt = 1.000000E-13

		middle_layer := 6
		// save the middle slice of the config
		AutoSave(CropLayer(m, middle_layer), 1e-9)
		tableautosave(1.000000E-11)

		// Recipe: High T for 5ns -> RT for 5ns -> relax
		Temp = 850.000000
		Run(5e-9)

		// save only the middle layer
		saveas(CropLayer(m, middle_layer),"%s")

		Temp = 300.000000
		Run(5e-9)

		// save only the middle layer
		saveas(CropLayer(m, middle_layer),"%s")

		// change back to normal settings
		SetSolver(5) // back to default solver
		FixDt = 0 // turn off fixed time step
		Temp = 0 // turn off temperature

		MinimizerStop = 1e-6
		relax()			// high-energy states best minimized by relax()
		//Minimize() 		// 'fine' approach with minimize
		saveas(m,"config.ovf")
		// save only the middle layer
		saveas(CropLayer(m, 6),"%s")
		tablesave()

		''' %(params.Aex*effective_medium_scaling,
			  params.Dind*effective_medium_scaling,
			  rand.randrange(0, 2 ** 32),
			  'after_highT_'+ sim_name+'.ovf',
			  'after_RT_'+ sim_name+'.ovf',
			  'relaxed_'+sim_name+'.ovf'))

		mumax_file = open(mumax_file_str, "w")
		mumax_file.write(mumax_commands)
		mumax_file.close()

# this function is the heart of one_sim
def outer_product_object_list(obj, start_ind = 0):
	# given an object which may contain some lists, return a list of objects that
	# holds individuals items of the list instead
	# if the object contains multiple lists, a list of objects equivalent to the outerproduct of
	# those lists are returned
	# this works with nest objects and but does not open/flatten nested list

	assert (hasattr(obj, '__dict__'))
	obj_dict = obj.__dict__
	dict_list = list(enumerate(obj_dict))

	# scan through each member of the object
	for ind in range(start_ind, len(dict_list)):

		key = dict_list[ind][1]
		val = obj_dict[key]

		# if found a nested object
		if hasattr(val, '__dict__'):
			# lets open up this object and explore

			sub_obj = outer_product_object_list(val)
			# if it turns out that this object contain lists
			if isinstance(sub_obj, list):
				# flatten any nested lists of sub objects
				sub_obj = flatten(sub_obj)
				result = [None] * len(sub_obj)

				for (ind_i, val_i) in enumerate(sub_obj):
					obj_tmp = deepcopy(obj)
					setattr(obj_tmp, key, val_i)
					result[ind_i] = outer_product_object_list(obj_tmp, ind+1) #plus one here is impt

				return result
			#
			# if the object does not contain any lists, don't bother with it
			else:
				pass

		# if found a list, stop and flatten list
		elif isinstance(val, list):

			result = [None]*len(val)

			for (ind_i, val_i) in enumerate(val):
				obj_tmp = deepcopy(obj)
				# replace list with a single value
				setattr(obj_tmp, key, val_i)
				result[ind_i] = outer_product_object_list(obj_tmp, ind+1) #plus one -> do not open up nested list

			return  result

	# if no objects or list are found, just return this object
	return obj

def flatten(some_list):
	"""Given a list, possibly nested to any level, return it flattened."""
	new_list = []
	for item in some_list:
		if isinstance(item, list):
			new_list.extend(flatten(item))
		else:
			new_list.append(item)
	return new_list


if __name__ == '__main__':
	DA_matrix()
