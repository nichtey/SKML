import os
import pickle
import numpy as np
import csv
from sklearn import svm
from random import randrange
import matplotlib.pyplot as plt
import cv2

'''User Input'''
# Note: This script is similar to SVR.py except that its function is to reconstruct the original image from eigenface projections.
# Refer to SVR.py for detailed documentation.
# Important difference starts from line 201.

parent_path = r""

repetitions = 1000
no_test = 20
tolerance = 15
# AexInput.csv, DmiInput.csv or KappaInput.csv
data_file = r"DdivsqrtAInput.csv"

# If want to add scale factor as one of the inputs
sf_check = False

# If you want to add K_eff as one of the inputs
keff_check = False
keff_input = r"keffInput.csv"

g_factor = 0.00000000000000045
max_eigen = 10

# If want to perform optimisation for gamma
gamma_opt = False
lower_limit = 0.00000000000000005
upper_limit = 0.0000000000000010
step_size = 0.00000000000000005

# Low C allows for misclassification, so that generalisation is possible and outliers wont affect the fit so much
# High C reduces misclassification, but outliers may affect the fit significantly


'''End User Input'''

# Path where eigenfaces_data pickle is stored
eigenface_path = os.path.join(parent_path, r"7-FT Eigenfaces")
# Path where ft_image_array pickle is stored
ft_image_path = os.path.join(parent_path, r"2-Fourier Transformed")
# Path where ft_scaling pickle is stored
scaling_path = os.path.join(parent_path, r"2-Fourier Transformed")
# Path where ft_data is stored
ft_data_path = os.path.join(parent_path, r"2-Fourier Transformed")

with open(os.path.join(ft_data_path,"ft_data"), 'rb') as pickleFile:
    magnitude, phases, f_no_PCA = pickle.load(pickleFile)

with open(os.path.join(eigenface_path, "eigenface_data"), 'rb') as pickleFile:
    eigenfaces = pickle.load(pickleFile)

with open(os.path.join(ft_image_path, "ft_image_array"), 'rb') as pickleFile:
    mag_array = pickle.load(pickleFile)

top_ten_eigen = eigenfaces[:15]
mag_array = np.asarray(mag_array)
n_samples = mag_array.shape[0]

# Import Scaling factor
obj_input_path = os.path.join(scaling_path, "ft_scaling")
with open(obj_input_path, 'rb') as pickleFile:
    scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)

mean_scale = sum(scale_array)/len(scale_array)


def read_data(read_file):

    with open(os.path.join(parent_path, read_file), mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        my_data = []

        for row in csv_reader:

            if line_count == 0:
                #print("\n" + f'Variable declared: {row[1]}')
                line_count += 1

            else:
                my_data.append(row[1])
                line_count += 1

        # print(f'Number of training data points obtained: {line_count - 1}' + "\n")

    my_data = np.asarray(my_data)
    my_data = my_data.astype(np.float64)
    return my_data


def make_predict(g_value, no_test = 10):
    y = read_data(data_file)

    random = [i for i in range(n_samples)]
    y_test = []
    x_test = []
    x_train = []
    y_train = []
    temp_index = []
    for i in range(no_test):
        Temp = random.pop(randrange(len(random)))
        y_test.append(y[Temp])
        x_test.append(x[Temp])
        temp_index.append(Temp)

    for a in range(len(random)):
        x_train.append(x[random[a]])
        y_train.append(y[random[a]])

    clf = svm.SVR(gamma=g_value, C=50, epsilon=0.05, kernel='rbf')
    clf.fit(x_train, y_train)

    display = []
    for i in clf.predict(x_test):
        i = np.round(i, 4)
        display.append(i)

    # To find percentage discrepancy
    answers = np.round(y_test,5)
    diff = np.abs(np.subtract(answers, display))
    perc_dif = np.multiply(100, np.divide(diff, y_test))

    print("")
    print(f'Predictions: {display}')
    print(f'    Answers: {np.round(y_test,4)}')
    print(f"Perc disc  : {np.round(perc_dif, 3)}")
    print(f"Avg disc   : {np.sum(np.round(perc_dif, 3))/len(y_test)}")
    print(f"R^2 Coef   : {round(clf.score(x_test, y_test),5)}")
    return round(clf.score(x_test, y_test)*100, 1), np.sum(perc_dif)/no_test


def one_iteration(g_factor, no_test):

    ra = []
    for i in range(repetitions):
        real_acc, avg_disc = make_predict(g_factor, no_test)
        ra.append(avg_disc)

    plt.plot(x_, ra, label="Avg Real Accuracy")
    plt.legend()

    print("")
    print(f"Overall average discrepancy(%): {sum(ra)/len(ra)}")
    # plt.show()
    return sum(ra)/len(ra)

extra_eigens = 0

if sf_check:
    extra_eigens += 1

if keff_check:
    extra_eigens += 1
    keff_array = read_data(keff_input)

x = np.empty((n_samples, max_eigen + extra_eigens))

for a in range(n_samples):
    for b in range(max_eigen):
        x[a][b] = np.dot(mag_array[a].ravel(), top_ten_eigen[b].ravel())

    # Add Scaling Factor
    if sf_check:
        x[a][max_eigen] = 1/(scale_array[a]/mean_scale)

    # Add Keff
    if keff_check:
        x[a][-1] = keff_array[a]

print(x[0])

phases = np.asarray(phases)
save_path = r"C:\Users\nicht\Desktop\New folder"
file_names = []
for file in os.listdir(os.path.join(parent_path, r"0-Original")):
    if file.endswith(".png"):
        file_names.append(file)

def saveImage(imageToSave, name):

    x = np.amin(imageToSave)

    if np.isinf(np.amin(imageToSave)):
        x = np.partition(imageToSave.flatten(), 1)[1]

    array_scale = np.amax(imageToSave) - x
    temp = np.subtract(imageToSave, x)
    temp2 = np.divide(temp, array_scale)
    temp3 = np.multiply(temp2, 255)
    temp4 = np.rint(temp3)
    cv2.imwrite(os.path.join(save_path, name), temp4)

for a in range(phases.shape[0]):
    new_image = np.empty((512, 512))
    f_shift_recon = np.empty((512, 512), dtype=np.complex)

    # Summation of the product of eigenface projection and eigenface matrix
    for i in range(10):
        new_image += x[a][i]*top_ten_eigen[i]

    # Recombine with phase data
    for b in range(512):
        for c in range(512):
            f_shift_recon[b][c] = new_image[b][c] * np.exp(1j * phases[a][b][c])

    # Inverse Fourier Transform
    f_ishift = np.fft.ifftshift(f_shift_recon)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    saveImage(img_back, f"{file_names[a]}.png")

'''
ra = []
x_ = [i for i in range(repetitions)]

# If only want 1 iteration
if not gamma_opt:
    one_iteration(g_factor, no_test)

else:
    # To Optimise
    acc = []
    g_factor = lower_limit
    gammas = []

    while g_factor < upper_limit:
        gammas.append(g_factor)
        acc.append(one_iteration(g_factor, no_test))
        g_factor += step_size

    plt.clf()
    plt.plot(gammas, acc)
    plt.show()
'''
