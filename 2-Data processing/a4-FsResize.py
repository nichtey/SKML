import pickle
import os
import cv2
import numpy as np
import math

'''User Input'''

Parent_Path = r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\SVM (SVR)\33DJM+Test4"
file_type = r"ft_scaling"

'''End User Input'''

# Must contain pickle ft_scaling/ft_refined_scaling file
Stored_Path = os.path.join(Parent_Path, r"2-Fourier Transformed")

# Outputs the scaled fourier space files
Output_Path = os.path.join(Parent_Path, r"4-FS Scaled\Rough Scaling")

def main():

    # Requires scaling data from ft_scaling
    obj_input_path = os.path.join(Stored_Path, file_type)

    if file_type == "ft_scaling":
        with open(obj_input_path, 'rb') as pickleFile:
            scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)

    obj_input_path = os.path.join(Stored_Path, "ft_image_array")
    with open(obj_input_path, 'rb') as pickleFile:
        image_array = pickle.load(pickleFile)

    file_names = []
    for file in os.listdir(os.path.join(Parent_Path, r"2-Fourier Transformed")):
        if file.endswith(".png"):
            file_names.append(file)

    largest_scale = np.amax(scale_array)
    widths = []
    image_array = np.asarray(image_array)

    print("Applying rough scaling factor on the Fourier transformed images.")
    file_number = 0
    for i in range(image_array.shape[0]):

        image_array[i][256][256] = 0

        img = image_array[i]
        scale_percent = 1/(scale_array[file_number] / largest_scale)

        width = int(img.shape[1] * scale_percent)
        widths.append(width)
        height = int(img.shape[0] * scale_percent)
        dim = (width, height)
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)

        x = np.amin(resized)
        array_scale = np.amax(resized) - x
        temp = np.subtract(resized, x)
        temp2 = np.divide(temp, array_scale)
        temp3 = np.multiply(temp2, 255)
        temp4 = np.rint(temp3)
        cv2.imwrite(os.path.join(Output_Path, file_names[i]), temp4)
        file_number += 1

    widths = np.asarray(widths)
    min_size = np.amin(widths)
    half_crop = math.trunc(min_size / 2)
    # print(half_crop)

    print("Cropping images to ensure that they are still the same size.")
    # This step is to crop the images.
    for file in os.listdir(Output_Path):
        if file.endswith(".png"):
            img = cv2.imread(os.path.join(Output_Path, file), cv2.IMREAD_UNCHANGED)
            crop_img = img[round(img.shape[0] / 2) - half_crop:(round(img.shape[0] / 2) + half_crop),
                       round(img.shape[1] / 2) - half_crop:(round(img.shape[1] / 2) + half_crop)]
            cv2.imwrite(os.path.join(Output_Path, file), crop_img)
            # print(crop_img.shape)

if __name__ == "__main__":
    main()