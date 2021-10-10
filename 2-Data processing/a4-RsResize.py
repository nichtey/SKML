# Pickle file is generated from ft_scaling.py (array of scaling sizes)

import pickle
import os
import cv2
import numpy as np
import math

'''User Input'''

# Must contain images to scale (Real Space)
Stored_Path = r""

# Must contain pickle ft_scaling file
Stored_Path_2 = r""

# Output Scaled Images
Output_Path = r""

# Output Cropped and Scaled Images
Output_Path_2 = r""

'''End User Input'''

#def find_smallest():


def main():
    # Requires phase data from ft_data and scaling data from ft_scaling
    obj_input_path = os.path.join(Stored_Path_2, "ft_scaling")
    with open(obj_input_path, 'rb') as pickleFile:
        scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)
    mean_scale = sum(scale_array)/len(scale_array)

    widths = []

    file_number = 0
    for file in os.listdir(Stored_Path):
        if file.endswith(".png"):
            img = cv2.imread(os.path.join(Stored_Path, file), cv2.IMREAD_UNCHANGED)
            scale_percent = scale_array[file_number] / mean_scale
            width = int(img.shape[1] * scale_percent)
            widths.append(width)
            height = int(img.shape[0] * scale_percent)
            dim = (width, height)
            resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            cv2.imwrite(os.path.join(Output_Path, file), resized)
            file_number += 1

    # Smallest Image size is 175 pixels
    widths = np.asarray(widths)
    min_size = np.amin(widths)
    half_crop = math.trunc(min_size/2)
    # print(half_crop)

    for file in os.listdir(Output_Path):
        if file.endswith(".png"):
            img = cv2.imread(os.path.join(Output_Path, file), cv2.IMREAD_UNCHANGED)
            crop_img = img[round(img.shape[0]/2)-half_crop:(round(img.shape[0]/2)+half_crop), round(img.shape[1]/2)-half_crop:(round(img.shape[1]/2)+half_crop)]
            cv2.imwrite(os.path.join(Output_Path_2, file), crop_img)
            # print(crop_img.shape)

if __name__ == "__main__":
    main()
