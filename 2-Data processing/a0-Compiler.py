import os
import importlib
import csv
import pickle
import numpy as np

'''User Input'''

parent_path = r""

# 0: Create folders, 1: Initialise, 2: Create csv files
cmd_check = 2

# Check if required to perform scaling in real space then fourier transform
# Loses a lot of information. (Default = False)
scale_check = False

# Check if required to perform scaling in fourier space (Default = True)
# Default is True as it improves SVR accuracy
# Make sure that the eigenface output has a pixel dimension of 512 x 512.
ft_scale_check = True

# Refinement of the scaling will be performed if true (Default = True)
ft_refine_scale_check = True

# Don't include the last __ images in eigenface
# Is used to test if the test data should be included in the calculation of eigenface
# It is found that including all test data in the calculation of eigenface is better
# i.e. Default do_not_include = 0
do_not_include = 0

# If need to append additional FT image (Default = False)
load_external = False

'''End User Input'''

output_paths = []
folder_names = [r"0-Original",                          # index 0
                r"1-Processed",                         # index 1
                r"2-Fourier Transformed",               # index 2
                r"3-Fitting Curves",                    # index 3
                r"4a-RS Scaled",                        # index 4
                r"4b-RS Scaled and Cropped",            # index 5
                r"5-FT Scaled",                         # index 6
                r"7-FT Eigenfaces",                     # index 7
                r"8-Problematic"]                       # index 8

output_sub_paths = []
sub_folders = [r"3-Fitting Curves\Failed Optimisations",    # index 0
               r"4-FS Scaled\Rough Scaling",
               r"4-FS Scaled\Intensity Curves",
               r"4-FS Scaled\Refined Scaling"]

script_names = [r"a1-ProcessImage",             # index 0
                r"a2, 5-FourierTransform",      # index 1
                r"a3-FtScaling",                # index 2
                r"a4-RsResize",                 # index 3
                r"a6-ScaledFtPCA",              # index 4
                r"a7-PCA_Final",                # index 5
                r"a4-FsResize",                 # index 6
                r"a4c-RefineScale"]             # index 7

mods = []


def create_folders():
    for i in range(len(folder_names)):
        output_paths.append(os.path.join(parent_path, folder_names[i]))

    for i in range(len(output_paths)):
        if not os.path.exists(output_paths[i]):
            os.makedirs(output_paths[i])

    for i in range(len(sub_folders)):
        output_sub_paths.append(os.path.join(parent_path, sub_folders[i]))

    for i in range(len(output_sub_paths)):
        if not os.path.exists(output_sub_paths[i]):
            os.makedirs(output_sub_paths[i])

    print("Folders created. Add the original images to the 1-Original folder.")

def initialise():

    print("Importing scripts.")
    for i in range(len(script_names)):
        mods.append(importlib.import_module(script_names[i]))

    print("Scripts imported. Initialising.")
    # Process Image
    mods[0].Stored_Path = os.path.join(parent_path, folder_names[0])
    mods[0].Output_Path = os.path.join(parent_path, folder_names[1])
    mods[0].main()
    print("Module a1 completed.")
    # Note: Ensure upper and lower threshold for binarisation is adequate. Default is 200 and 60 respectively.

    # Fourier Transform Processed Image
    mods[1].load_path = os.path.join(parent_path, folder_names[1])          # mods[0].Output_Path
    mods[1].save_path = os.path.join(parent_path, folder_names[2])
    if load_external:
        mods[1].load_external = True
    mods[1].main()
    print("Module a2 completed.")

    # Scale Fourier Transformed Image
    mods[2].load_path = os.path.join(parent_path, folder_names[2])          # mods[1].save_path
    mods[2].save_path = os.path.join(parent_path, folder_names[3])
    mods[2].failed_path = os.path.join(parent_path, sub_folders[0])
    mods[2].main()
    print("Module a3 completed.")
    # Note: Default centre pixel set at 256, 256.

    if scale_check:
        # Apply scale and cropping on Real Space Processed Image
        mods[3].Stored_Path = os.path.join(parent_path, folder_names[1])        # mods[0].Output_Path
        mods[3].Stored_Path_2 = os.path.join(parent_path, folder_names[2])      # mods[1].save_path
        mods[3].Output_Path = os.path.join(parent_path, folder_names[4])
        mods[3].Output_Path_2 = os.path.join(parent_path, folder_names[5])
        mods[3].main()
        print("Module 4 of 8 completed.")

        # Fourier Transform Scaled and Cropped RS Image
        mods[1].load_path = os.path.join(parent_path, folder_names[5])  # mods[3].Output_Path
        mods[1].save_path = os.path.join(parent_path, folder_names[6])
        mods[1].main()
        print("Module 5 of 8 completed.")

        # Set the PCA location to scaled images
        mods[4].load_path = os.path.join(parent_path, folder_names[6])  # mods[1].Output_Path
        # Output PCA Matrix for magnitude component of FT Scaled Image
        mods[4].main(mods[4].n_components)
        print("Module 6 of 8 completed.")

        # Perform PCA and get the eigenface data
        mods[5].input_check = 1
        mods[5].Stored_Path = os.path.join(parent_path, folder_names[6])  # mods[1].Output_Path
        mods[5].Output_Path = os.path.join(parent_path, folder_names[7])
        mods[5].main(mods[5].n_components)
        print("Module 7 of 8 completed.")

    # If no scaling in real space is performed
    elif not scale_check:

        # If scaling in fourier space is required, perform first round of scaling
        if ft_scale_check:
            mods[6].Parent_Path = os.path.join(parent_path)
            mods[6].Stored_Path = os.path.join(parent_path, folder_names[2])
            mods[6].Output_Path = os.path.join(parent_path, sub_folders[1])
            mods[6].file_type = r"ft_scaling"
            mods[6].main()
            print("Module a4(FS) completed")

            # Perform PCA and get the eigenface data
            mods[5].input_check = 0  # Input is image.
            if ft_refine_scale_check:
                mods[7].parent_path = parent_path
                mods[7].Stored_Path = os.path.join(parent_path, r"4-FS Scaled\Rough Scaling")
                mods[7].Output_Path_1 = os.path.join(parent_path, r"4-FS Scaled\Refined Scaling")
                mods[7].Output_Path_2 = os.path.join(parent_path, r"4-FS Scaled\Intensity Curves")
                mods[7].main()
                mods[5].Stored_Path = os.path.join(parent_path, sub_folders[3])
                print("Module a4c completed.")
            else:
                mods[5].Stored_Path = os.path.join(parent_path, sub_folders[1])
            mods[5].Output_Path = os.path.join(parent_path, folder_names[7])
            mods[5].do_not_include = do_not_include
            mods[5].main(mods[5].n_components)
            print("Module a7 completed.")

        # If no scaling is performed in real or fourier space
        elif not ft_scale_check:
            # Set the PCA location to unscaled images
            mods[4].load_path = os.path.join(parent_path, folder_names[2])  # mods[1].Output_Path
            # Output PCA Matrix for magnitude component of FT Scaled Image
            mods[4].main(mods[4].n_components)
            print("Module 6 of 8 completed.")

            # Perform PCA and get the eigenface data
            mods[5].input_check = 1                                           # Input is numpy array and not an image.
            mods[5].Stored_Path = os.path.join(parent_path, folder_names[2])  # mods[1].Output_Path
            mods[5].Output_Path = os.path.join(parent_path, folder_names[7])
            mods[5].main(mods[5].n_components)
            print("Module 7 of 8 completed.")

    print("\n" + "The following information is required for module 8(a8-SVR.py):")
    print("parent_path:" + "\n" + parent_path)


# Creates blank data files to be filled and used as the labels when doing SVR
# Fill in these blank data files before performing SVR
# Also creates a scale_output csv file containing information about how much scaling was done on the original inputs.
def data_files():
    print("Creating CSV files.")

    obj_input_path = os.path.join(os.path.join(parent_path, folder_names[2]), "ft_scaling")
    with open(obj_input_path, 'rb') as pickleFile:
        scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)

    obj_input_path = os.path.join(os.path.join(parent_path, r"4-FS Scaled\Refined Scaling"), "ft_refined_scaling")
    with open(obj_input_path, 'rb') as pickleFile:
        r_scale_percent = pickle.load(pickleFile)

    file_names = []
    for file in os.listdir(os.path.join(parent_path, r"0-Original")):
        if file.endswith(".png"):
            file_names.append(file)

    with open(os.path.join(parent_path, 'KappaInput.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'Kappa'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i]])

    with open(os.path.join(parent_path, 'AexInput.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'Aex'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i]])

    with open(os.path.join(parent_path, 'DmiInput.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'Dmi'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i]])

    scale_percent = []
    largest_scale = np.amax(scale_array)
    for file_number in range(len(scale_array)):
        scale_percent.append(1/(scale_array[file_number] / largest_scale))
    final_scale_percent = np.multiply(scale_percent, r_scale_percent)

    with open(os.path.join(parent_path, 'ScaleOutput.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'Rough Scale', 'Refined Scale', 'Final Scale'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i], scale_percent[i], r_scale_percent[i], final_scale_percent[i]])

    with open(os.path.join(parent_path, 'DdivsqrtAInput.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'D/sqrtA'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i]])

    obj_input_path = os.path.join(parent_path, "final_scale_percent")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump((final_scale_percent), pickleFile)

if cmd_check == 0:
    create_folders()

if cmd_check == 1:
    initialise()

if cmd_check == 2:
    data_files()
