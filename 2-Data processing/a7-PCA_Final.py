# To import images, reduce the dimension by a fixed amount, and output the eigenfaces.
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from skimage import io
import pickle
import cv2

'''User input'''

# Outputs the eigenface_data file and the PCA images
Output_Path = r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\SVM (SVR)\33DJM+Test4\7-FT Eigenfaces"

# Must contain images, or the relevant Ft_PCA_Data
Stored_Path = r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\SVM (SVR)\33DJM+Test4\4-FS Scaled\Refined Scaling"

# Maximum n_components is equal to the number of pictures, or the number of images saved in the image
# Set n_components = "Max", or an integer smaller than the maximum.
n_components = "Max"

# Input must either be 1 for numpy array in pickle file or 0 for images in png format. Name the pickle "ft_image_array".
input_check = 0

# Do not include last __ input in pca (Default = 0)
do_not_include = 0

'''End user input'''


def saveImage(imageToSave, name):

    x = np.amin(imageToSave)

    if np.isinf(np.amin(imageToSave)):
        x = np.partition(imageToSave.flatten(), 1)[1]

    array_scale = np.amax(imageToSave) - x
    temp = np.subtract(imageToSave, x)
    temp2 = np.divide(temp, array_scale)
    temp3 = np.multiply(temp2, 255)
    temp4 = np.rint(temp3)
    cv2.imwrite(os.path.join(Output_Path, name), temp4)


# Use this if the input is images
def read_images():
    file_count = 0

    # Note: First dimension of imgArray depends on the number of files. 2nd and 3rd on the number of pixels in row, height
    # Read files in path, convert matrix into a 2D array with number of images in 1D and all features in the 2nd Dimension
    TempArray = []
    for file in os.listdir(Stored_Path):
        if file.endswith(".png"):
            TempArray.append(io.imread(os.path.join(Stored_Path, file)))
            file_count += 1

    if do_not_include !=0:
        imgArray = np.asarray(TempArray[:-do_not_include])

    else:
        imgArray = np.asarray(TempArray)
    x = np.reshape(imgArray[:, :, :], (imgArray.shape[0], imgArray.shape[1]*imgArray.shape[2]))
    return x, imgArray


# Use this if the input is an image array (For Fourier Transformed)
def read_array():
    obj_input_path = os.path.join(Stored_Path, "ft_image_array")
    with open(obj_input_path, 'rb') as pickleFile:
        image_array = pickle.load(pickleFile)
    image_array = np.asarray(image_array)
    x = np.reshape(image_array[:, :, :], (image_array.shape[0], image_array.shape[1]*image_array.shape[2]))
    return x, image_array


def main(n_components):
    # print("\n" + f"Please save your images (png) or pickle file in the directory shown below: {Stored_Path}")
    # print(f"Output images and data can be found here: {Output_Path}")

    # Input must either be numpy array (images) or images in png format.
    if input_check == 0:
        x, imgArray = read_images()

    else:
        x, imgArray = read_array()

    if n_components == "Max":
        n_components = imgArray.shape[0]

    print("Implementing PCA. Note: To get the explained variance ratio graph, uncomment plt.show() in line 91.")
    pca = PCA(n_components=n_components, svd_solver='full', whiten=False).fit(x)
    x_pca = pca.transform(x)

    variance = pca.explained_variance_ratio_*100
    variance_y = [i for i in range(n_components)]
    plt.plot(variance_y, variance.ravel())
    # print(variance.ravel())
    # plt.show()

    eigenpics = pca.components_.reshape((n_components, imgArray.shape[1], imgArray.shape[2]))

    for i in range(n_components):
        saveImage(eigenpics[i], f"{i}.png")

    # dump with pickle
    obj_input_path = os.path.join(Output_Path, "eigenface_data")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump(eigenpics, pickleFile)

    # Reconstruction of original picture from eigenpics
    # Xhat = np.dot(x_pca[:, :n_components], pca.components_[:n_components, :])
    # Xhat = np.reshape(Xhat, (file_count, imgArray.shape[1], imgArray.shape[2]))


if __name__ == "__main__":
    main(n_components)