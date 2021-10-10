import os, shutil, re

# This is a simple script to copy and rename ovf files at different Hr to a common location

# ---------------Input parameters---------------

local_mode = True
source_dir = r''
destination_dir = r''
#source_folders_regex = r'.*\.out'
items_regex = 'Dind_.*.ovf'
out_folder_regex = r'\.out'
#table_file_str = 'table.txt'


# ---------------End of Input parameters---------------

# to gather files in NSCC and local cluster
def main():

	print(os.path.exists(destination_dir))
	# make directory if needed
	if os.path.exists(destination_dir) == False:
		os.makedirs(destination_dir)
		print("Hello")

	# find all folders in source_dir that we want
	folder_list = [folder for folder in os.listdir(source_dir) if (os.path.isdir(os.path.join(source_dir, folder))
																   and re.search(out_folder_regex,  folder))]

	#folder_list.sort(key = lambda name : int(re.search(source_folders_regex, name).group(1)))

	for ind,folder in enumerate(folder_list):

		curr_path = os.path.join(source_dir, folder)

		# find all files in a single Hr folder
		filename_list = os.listdir(curr_path)

		# find desired ovf file
		ovf_files = [name for name in filename_list if re.search(items_regex, name)]
		
		for ovf_file in ovf_files:
			if ovf_file is not None:
				# copy file to destination
				shutil.copyfile(os.path.join(curr_path, ovf_file), os.path.join(destination_dir, ovf_file))

		# if local_mode and out_folder is not None:

			# # copy the table file also
			# shutil.copyfile(os.path.join(curr_path, table_file_str), os.path.join(destination_dir, folder + '_' + table_file_str))


# run the main function
if __name__ == '__main__':
	main()

