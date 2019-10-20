import os
import cv2
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import pickle

# To provide refinement of the scaling factor
# Ensure that the white circle image labeled 'reference_img' is inside the parent folder.

'''User Input'''

parent_path = r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\SVM (SVR)\33DJM+Test4"

# Only check the black/white intensity in a square
# scan_limit is the distance from the centre
scan_limit = 150

# Minimum and maximum resizing allowed (Both Inclusive)
resize_min = 1.5
resize_max = 3.5
step_size = 0.01

'''End User Input'''

# Path where the images from the first round of scaling is stored.
Stored_Path = os.path.join(parent_path, r"4-FS Scaled\Rough Scaling")
# Path where the images from the second round of scaling is stored.
Output_Path_1 = os.path.join(parent_path, r"4-FS Scaled\Refined Scaling")
# To store the curves of intensity vs scale.
Output_Path_2 = os.path.join(parent_path, r"4-FS Scaled\Intensity Curves")

def read_images(path):
    file_count = 0

    # Note: First dimension of imgArray depends on the number of files. 2nd and 3rd on the number of pixels in row, height
    # Read files in path, convert matrix into a 2D array with number of images in 1D and all features in the 2nd Dimension

    for file in os.listdir(path):
        if file.endswith(".png"):
            file_count += 1

    imgArray = np.empty((file_count, 512, 512))

    i = 0
    file_names = []
    for file in os.listdir(path):
        if file.endswith(".png"):
            pic = io.imread(os.path.join(path, file))
            pic = np.asarray(pic)
            file_names.append(file)
            if pic.ndim == 3:
                pic = pic[:,:,0]
            imgArray[i] = pic
            i+=1

    return imgArray, file_names


# Recasting is performed so that only the area of interest is checked (Defined by scan_limit)
def recast_matrix(orig_matrix):
    centre_pixel = round(len(orig_matrix[0])/2)
    recasted = orig_matrix[centre_pixel-scan_limit: centre_pixel+scan_limit, centre_pixel-scan_limit: centre_pixel+scan_limit]
    recasted = recasted.astype(np.float64)
    return recasted


def main():

    print("Attempting to find the refined scale factors.")
    imgArray, file_names = read_images(Stored_Path)
    refArray,file_name = read_images(parent_path)

    recasted_img = np.empty((imgArray.shape[0], scan_limit*2, scan_limit*2))
    refined_scale = np.empty((imgArray.shape[0]))
    #refined_scale[0] = 1

    # The reference image is the white circle in the black background.
    recasted_ref = recast_matrix(refArray[0])

    # Calculate number of data points to be taken
    attempts = round((resize_max - resize_min)/step_size) + 1

    x = np.empty((imgArray.shape[0], attempts))
    y = np.empty((imgArray.shape[0], attempts))

    # The rough scaled images will grow and the total intensity is calculated using a multiplication technique
    # I.e. if one is black and one is white, then the intensity is 0
    # Highest total intensity is found when the rough scaled image grows until it matches the white circle.
    # Represented by the peak in the intensity vs scale graph.

    for a in range(x.shape[0]):
        for i in range(attempts):
            width = int(imgArray[0].shape[1]*(resize_min+i*step_size))
            height = int(imgArray[0].shape[0]*(resize_min+i*step_size))
            dim = (width, height)
            resized = cv2.resize(imgArray[a], dim, interpolation=cv2.INTER_CUBIC)
            recasted_img[a] = recast_matrix(resized)
            result = np.multiply(recasted_ref, recasted_img[a])
            # cv2.imshow('image', recasted_img[1].astype(np.uint8))
            # cv2.waitKey(0)
            x[a][i] = resize_min+i*step_size
            y[a][i] = np.sum(result)

        # A polynomial curve is fitted to the curve and the peak intensity if found
        # Scaling corresponding to peak intensity is then found
        yhat = savgol_filter(y[a], 31, 4)
        plt.clf()
        plt.plot(x[a],yhat)
        plt.plot(x[a], y[a])
        max = np.amax(yhat)
        index_max = np.where(yhat == max)[0]
        refined_scale[a] = x[a][index_max]
        # print(x_guess[0])
        plt.savefig(os.path.join(Output_Path_2, file_names[a]), bbox_inches='tight', pad_inches=0)

    # Raw scaling factor (refined_scale) is normalised(scale_factor) so that minimal scaling is done on images.
    scale_factor = np.divide(refined_scale, np.amin(refined_scale[1:]))
    # print(scale_factor)

    print("Now applying the refined scale factors to the images.")
    for i in range(len(imgArray)):
        width = int(512*scale_factor[i])
        height = int(512*scale_factor[i])
        dim = (width, height)
        resized = cv2.resize(imgArray[i], dim, interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(os.path.join(Output_Path_1, file_names[i]), resized)

    print("Now cropping the scaled images.")
    # This step is to crop the images.
    for file in os.listdir(Output_Path_1):
        if file.endswith(".png"):
            img = cv2.imread(os.path.join(Output_Path_1, file), cv2.IMREAD_UNCHANGED)
            crop_img = img[round(img.shape[0] / 2) - 256:(round(img.shape[0] / 2) + 256),
                       round(img.shape[1] / 2) - 256:(round(img.shape[1] / 2) + 256)]
            cv2.imwrite(os.path.join(Output_Path_1, file), crop_img)

    obj_output_path = os.path.join(Output_Path_1, "ft_refined_scaling")
    with open(obj_output_path, 'wb') as pickleFile:
        pickle.dump((scale_factor), pickleFile)

if __name__ =="__main__":
    main()
