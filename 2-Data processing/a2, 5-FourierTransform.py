import numpy as np
import os
import cv2
import pickle

'''User Input'''

# Outputs fourier transformed images
save_path = r"C:\Users\nicht\Desktop\To Fourier Transform"

# Must contain png images to fourier transform
load_path = r"C:\Users\nicht\Desktop\To Fourier Transform"

# Appends external, already FT images in a pickle to pickle file that is outputted (Default = False)
load_external = False

'''End User Input'''

def loadImage():

    file_count = 0
    file_names = []

    for file in os.listdir(load_path):
        if file.endswith(".png"):
            if file_count == 0:
                temp = cv2.imread(os.path.join(load_path, file), 0)
            file_names.append(file)
            file_count += 1

    temp = np.asarray(temp)
    my_images = np.empty((0, temp.shape[0], temp.shape[1]))

    for file in os.listdir(load_path):
        if file.endswith(".png"):
            temp = cv2.imread(os.path.join(load_path, file), 0)
            my_images = np.append(my_images, [temp], axis=0)

    return my_images, file_names


def saveImage(imageToSave, name):

    x = np.amin(imageToSave)
    # Should not have, but just check if negative infinity, then replace by second smallest value.
    if np.isinf(np.amin(imageToSave)):
        x = np.partition(imageToSave.flatten(), 1)[1]

    array_scale = np.amax(imageToSave) - x
    temp = np.subtract(imageToSave, x)
    temp2 = np.divide(temp, array_scale)
    temp3 = np.multiply(temp2, 255)
    temp4 = np.rint(temp3)
    cv2.imwrite(os.path.join(save_path, name), temp4)


def main():
    image_data, file_names = loadImage()

    magnitudes = []
    phases = []
    f_list = []

    print("Performing Fourier transform on the processed images.")
    for _ in range(image_data.shape[0]):

        f = np.fft.fft2(image_data[_])
        fshift = np.fft.fftshift(f)
        # Remove the centre white pixel
        fshift[np.where(fshift == np.amax(fshift))[0][0]][np.where(fshift == np.amax(fshift))[1][0]] = 0
        phase_spectrum = np.angle(fshift)
        saveImage(np.abs(fshift), file_names[_])
        # If want to see some illustratitive images
        # magnitude_spectrum = np.log(np.abs(fshift))
        # saveImage(magnitude_spectrum, file_names[_])
        magnitudes.append(np.abs(fshift)) # No logarithm.
        phases.append(phase_spectrum)
        f_list.append(f)

    if load_external:
        obj_input_path = os.path.join(load_path, "ft_data_processed")
        with open(obj_input_path, 'rb') as pickleFile:
            TempArray, phases1, f_list1 = pickle.load(pickleFile)

        for i in range(len(TempArray)):
            magnitudes.append(TempArray[i])
            phases.append(phases1[i])
            f_list.append(f_list1[i])

    # dump with pickle
    obj_input_path = os.path.join(save_path, "ft_data")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump((magnitudes, phases, f_list), pickleFile)

    obj_input_path = os.path.join(save_path, "ft_image_array")
    with open(obj_input_path, 'wb') as pickleFile:
        pickle.dump(magnitudes, pickleFile)

if __name__ == "__main__":
    main()

'''
# Inverse fourier Transform

f_ishift = np.fft.ifftshift(fshift)
img_back = np.fft.ifft2(f_ishift)
img_back = np.abs(img_back)

plt.subplot(121), plt.imshow(image_data[76], cmap='gray')
plt.title('Input Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122), plt.imshow(img_back, cmap='gray')
plt.title('Reconstruct'), plt.xticks([]), plt.yticks([])
plt.show()
'''

""" For 1 iteration

# relaxed_33dFORC_st135_Aex_12_Dind_2.4.png
# 11dFORC_st22_00_J0hOdBES_Aex_11_Dind_1.8.png
# 190305_33j_Processed.png

# Load and colour in gray scale
data = cv2.imread(os.path.join(Stored_Path, "relaxed_33dFORC_st133_Aex_10_Dind_1.4.png"), 0)

# Compute the 2-dimensional discrete Fourier Transform
f = np.fft.fft2(data)

# Shift the zero-frequency component to the center of the spectrum.
fshift = np.fft.fftshift(f)
magnitude_spectrum = 20*np.log(np.abs(fshift))

plt.subplot(121), plt.imshow(data, cmap='gray')
plt.title('Input Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122), plt.imshow(magnitude_spectrum, cmap='gray')
plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
plt.show()

saveImage(magnitude_spectrum, "f_transform.png")
"""

'''
Plot phase spectrum

f = np.fft.fft2(image_data[0])
fshift = np.fft.fftshift(f)
phase_spectrum = 20 * np.angle(fshift)

plt.subplot(121), plt.imshow(image_data[0], cmap='gray')
plt.title('Input Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122), plt.imshow(phase_spectrum, cmap='gray')
plt.title('Phase Spectrum'), plt.xticks([]), plt.yticks([])
plt.show()
'''