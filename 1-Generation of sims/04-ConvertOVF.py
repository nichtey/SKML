import numpy as np
import os, re
from tkinter import filedialog
from multiprocessing import Pool
from PIL import Image

# from core.data_parser import DataParser
# from core.plotter import Plotter
# from core.util import Vector, ParamsHL

NUM_PROCS = 4

def process_main():

	files = filedialog.askopenfilenames(title='Select .ovf files')
	num_files = len(files)
	grid_spacing = 0.004 # in um, usually 0.004 um
	z_layer_number = 0

	pool_input_list = []

	# build pool input list
	for ind, pathandfilename in enumerate(files):
		pool_input_list.append((pathandfilename, z_layer_number, grid_spacing, float(ind / num_files)))
	# process domains with multiprocessing
	with Pool(processes=NUM_PROCS) as p:
		# read in all these files as one dataset
		p.starmap(do_conversion, pool_input_list)

def import_ovf(path_and_filename=None, path=None, filename=None, z_layer_number = 0, mag_direction = 2, header_bytes = 1000,  grid_spacing = 1, **kwargs):
	"""
	Import the data
	mag_direction: 0-2: x,y,z. Direction of mag to output.								 Negative to output all
	"""

	# only outputs one direction
	assert(mag_direction >=0 and mag_direction <=2)

	print(path)
	print(filename)
	# path_and_filename = path_and_filename
	# path_and_filename = os.path.join(path_and_filename, path, filename)
	# Path, Filename is null?

	# First read the header byte and find the the number of xnodes, ynodes, znodes
	with open(path_and_filename) as fin:
		header_data = fin.read(header_bytes)

	num_nodes = re.search('# xnodes: (\+?-?\d+)\s*# ynodes: (\+?-?\d+)\s*# znodes: (\+?-?\d+)', header_data)
	x_len = int(num_nodes.group(1))
	y_len = int(num_nodes.group(2))
	z_len = int(num_nodes.group(3))

	# number of comment lines
	num_comment_lines = header_data.count('#')

	single_layer_size = x_len*y_len
	read_line_start = z_layer_number*single_layer_size+num_comment_lines
	read_line_end = read_line_start+single_layer_size
	line_index= 0
	data_index = 0

	data = np.zeros(single_layer_size, dtype=np.double)

	# User must be responsible for checking the validity of imported data!

	# data = np.genfromtxt(path_and_filename, comments='#', **kwargs)
	with open(path_and_filename) as fin:
		for line in enumerate(fin):
			line_str = line[1]
			# check if it is within read_line_start and read_line_end
			if line_index >= read_line_start:
				if line_index < read_line_end:
					tmp_list = np.fromstring(line_str,dtype=np.double,sep=' ')
					data[data_index] = tmp_list[mag_direction]
					data_index += 1
				else:
					break

			line_index+=1


	# reshape into original shape
	data = data.reshape(x_len, y_len)

	# wrap data inside a Shuju
	# shuju_obj = Shuju(data, MetaData())
	# mesh1, mesh2 = np.meshgrid(np.arange(0,y_len)*grid_spacing, np.arange(0,x_len)*grid_spacing)
	# shuju_obj.metadata.axes = Vector(mesh1, mesh2)

	return data

def do_conversion(pathandfilename, z_layer_number, grid_spacing, progress):
	# progress
	print('Processing... %0.1f%% complete.  Loading %s.' % (progress * 100, pathandfilename))
	data = import_ovf(path_and_filename=pathandfilename, z_layer_number=z_layer_number, grid_spacing=grid_spacing)

	# header_text = "ovf image"
	# data.metadata.label = header_text
	# data.metadata.axes_labels = Vector('x (um)', 'y (um)')
	# Plotter.pcolormesh(data=data, equal_aspect=True, vlim=ParamsHL(1, -1))

	# create image
	im = Image.fromarray((data * 255).astype(np.uint8), mode='L')
	# save image
	image_filename = os.path.splitext(pathandfilename)[0] + '.png'
	im.save(image_filename)

	# fig = plt.pcolormesh(data.data, cmap='viridis')
	# plt.gca().set_aspect('equal')
	# plt.axis('off')
	# fig.axes.get_xaxis().set_visible(False)
	# fig.axes.get_yaxis().set_visible(False)
	#
	# image_filename = os.path.splitext(pathandfilename)[0] + '.png'
	# plt.savefig(image_filename, dpi=300, bbox_inches='tight', pad_inches=0)
	# plt.close('all')

# run the main function
if __name__ == '__main__':
	process_main()  # test()