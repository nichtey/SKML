import os
import numpy as np
from skimage import io
import matplotlib.pyplot as plt
import cv2
import pickle

'''User input'''

Stored_Path = r"C:\Users\nicht\Desktop\To Fourier Transform\FT"
Output_Path = r"C:\Users\nicht\Desktop\To Fourier Transform\FT Processed"

desired_nm_per_pixel = 4
desired_width = 512
desired_height = 512
current_nm_per_pixel = 11.4

'''End User input'''

def read_images():

    file_names = []
    # Note: First dimension of imgArray depends on the number of files. 2nd and 3rd on the number of pixels in row, height
    # Read files in path, convert matrix into a 2D array with number of images in 1D and all features in the 2nd Dimension
    TempArray = []
    for file in os.listdir(Stored_Path):
        if file.endswith(".png"):
            #TempArray.append(io.imread(os.path.join(Stored_Path, file)))
            file_names.append(file)

    obj_input_path = os.path.join(Stored_Path, "ft_data")
    with open(obj_input_path, 'rb') as pickleFile:
        TempArray, phases, f_list = pickle.load(pickleFile)

    return TempArray, file_names, phases, f_list

def saveImage(imageToSave, name):

    x = np.amin(imageToSave)
    # Check if negative infinity, then replace by second smallest value.
    if np.isinf(np.amin(imageToSave)):
        x = np.partition(imageToSave.flatten(), 1)[1]

    array_scale = np.amax(imageToSave) - x
    temp = np.subtract(imageToSave, x)
    temp2 = np.divide(temp, array_scale)
    temp3 = np.multiply(temp2, 255)
    temp4 = np.rint(temp3)
    cv2.imwrite(os.path.join(Output_Path, name), temp4)

def main():
    imgArray, file_names, phases, f_list = read_images()

    pad_array = []
    resized_img = []

    for i in range(len(imgArray)):
        # Create zero padding
        img_width = imgArray[i].shape[1]
        img_height = imgArray[i].shape[0]
        pad_width = round((current_nm_per_pixel/desired_nm_per_pixel)*img_width)
        pad_height = round((current_nm_per_pixel/desired_nm_per_pixel)*img_height)
        pad_array.append(np.zeros((pad_height, pad_width)))

        pad_width_centre = round(pad_width/2)
        pad_height_centre = round(pad_height/2)
        pad_array[i][pad_height_centre - round(img_height/2): pad_height_centre - round(img_height/2) + img_height, pad_width_centre - round(img_width/2): pad_width_centre - round(img_width/2) + img_width] = imgArray[i]

        dim = (512, 512)
        resized_img.append(cv2.resize(pad_array[i], dim, interpolation=cv2.INTER_CUBIC))
        saveImage(resized_img[i], file_names[i])

    obj_input_path = os.path.join(Output_Path, "ft_image_array_processed")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump(resized_img, pickleFile)

    obj_input_path = os.path.join(Output_Path, "ft_data_processed")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump((resized_img, phases, f_list), pickleFile)

if __name__ == "__main__":
    main()