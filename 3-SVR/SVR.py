import os
import pickle
import numpy as np
import csv
from sklearn import svm
from random import randrange
import matplotlib.pyplot as plt
import shutil

'''User Input'''
parent_path = r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\SVM (SVR)\33DJM+Test4"

# Number of repetitions for a combination of hyper parameters that is required
# Repetitions only relevant if random_test_check = True, otherwise same results will be repeated
# Random_test_check will select random samples for testing.
# Disabling it will select the last no_test for testing.
repetitions = 1000
random_test_check = False

# No. of test in 1 repetition in 1 iteration
no_test = 24

# Tolerance defines the percentage discrepancy above which should be considered non-ideal
tolerance = 5

# AexInput.csv, DmiInput.csv or KappaInput.csv, DdivsqrtAInput.csv or any other csv files
# Ensure file has 2 columns with 2nd column containing the values of the label to be read
data_file = r"DmiInput.csv"

# If want to add scale factor as one of the inputs
# Only has an effect if this is multiplied by some large, arbitrary constant
sf_check = False

# If want to add K_eff as one of the inputs
# Only has an effect if this is multiplied by some large, arbitrary constant
keff_check = False
keff_input = r"keffInput.csv"

# Some quick (and good) combinations of gamma, epsilon and C for 10 max_eigen (sf_check and keff_check == False):
# Low fitting combination:  g = 0.0000000000000464, e = 0.00001, C = 20
# Med fitting combination:  g = 0.0000000000000181181, e = 0.05, C = 50
# High fitting combination: g = 0.000000000000000362, e = 0.1535, C = 401
# There exists many more combinations of hyperparameters that would work well. Use OptimiseSVR.py to find them.
g_factor = 0.0000000000000464
epsilon_factor = 0.00001
c_factor = 20
max_eigen = 10

# If want to perform optimisation for gamma
# Note that OptimiseSVR.py is more comprehensive and gamma, epsilon and C can be varied together
gamma_opt = False
lower_limit = 0.00000000000001810
upper_limit = 0.00000000000000038
step_size = 0.000000000000000001

# Low C allows for misclassification, so that generalisation is possible and outliers wont affect the fit so much
# High C reduces misclassification, but outliers may affect the fit significantly
# Weights can also be added to each sample to correct a skewed distribution of training data (Refer to documentation)
'''End User Input'''

# Global variables
if not random_test_check:
    repetitions = 1

col_answers = []
col_predictions = []
col_prob_answers = []
col_prob_predict = []
col_prob_index = []
col_prob_disc = []

print("Importing relevant files.")

# Path where eigenfaces_data pickle is stored
eigenface_path = os.path.join(parent_path, r"7-FT Eigenfaces")
# Path where ft_image_array pickle is stored
ft_image_path = os.path.join(parent_path, r"2-Fourier Transformed")
# Path where ft_scaling pickle is stored
scaling_path = os.path.join(parent_path, r"2-Fourier Transformed")

try:
    # Import eigenfaces
    obj_input_path = os.path.join(eigenface_path, "eigenface_data")
    with open(obj_input_path, 'rb') as pickleFile:
        eigenfaces = pickle.load(pickleFile)

    # Import no log image array
    obj_input_path = os.path.join(ft_image_path, "ft_image_array")
    with open(obj_input_path, 'rb') as pickleFile:
        mag_array = pickle.load(pickleFile)

    # Import Scaling factor
    obj_input_path = os.path.join(scaling_path, "ft_scaling")
    with open(obj_input_path, 'rb') as pickleFile:
        scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)

    if sf_check:
        obj_input_path = os.path.join(parent_path, "final_scale_percent")
        with open(obj_input_path, 'rb') as pickleFile:
            final_scale_percent = pickle.load(pickleFile)

except (FileNotFoundError):
    print(f"Problem finding the following file: {obj_input_path}")

# Only read the first 15 eigenfaces
top_ten_eigen = eigenfaces[:15]
mag_array = np.asarray(mag_array)
n_samples = mag_array.shape[0]


# Reads any CSV file with title in the first row, and data in the 2nd column, starting from 2nd row
def read_data(read_file):

    with open(os.path.join(parent_path, read_file), mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        my_data = []

        for row in csv_reader:

            # Skip first line
            if line_count == 0:
                line_count += 1

            else:
                my_data.append(row[1])
                line_count += 1

    my_data = np.asarray(my_data)
    my_data = my_data.astype(np.float64)
    return my_data


def make_predict(g_value, no_test = 10):
    y = read_data(data_file)
    y_test = []
    x_test = []
    x_train = []
    y_train = []
    temp_index = []

    # Pop some random index and then use that index to choose x input and y label
    if random_test_check:
        random = [i for i in range(n_samples)]
        for i in range(no_test):
            Temp = random.pop(randrange(len(random)))
            y_test.append(y[Temp])
            col_answers.append(y[Temp])
            x_test.append(x[Temp])
            temp_index.append(Temp)

        for a in range(len(random)):
            x_train.append(x[random[a]])
            y_train.append(y[random[a]])

    if not random_test_check:
        x_train = x[:-no_test]
        y_train = y[:-no_test]
        x_test = x[-no_test:]
        y_test = y[-no_test:]

        for i in range(no_test):
            col_answers.append(y_test[i])

        _ = [i for i in range(x.shape[0])]
        temp_index = _[-no_test:]

    # Setting up the SVR and fitting to training data is done here
    clf = svm.SVR(gamma=g_value, C=c_factor, epsilon=epsilon_factor, kernel='rbf')
    clf.fit(x_train, y_train)

    display = []
    for i in clf.predict(x_test):
        i = np.round(i, 4)
        col_predictions.append(i)
        display.append(i)

    # To find percentage discrepancy
    answers = np.round(y_test,5)
    diff = np.abs(np.subtract(answers, display))
    perc_dif = np.multiply(100, np.divide(diff, y_test))

    # Collected to display some statistics later
    for i in range(len(perc_dif)):
        if perc_dif[i] > tolerance:
            col_prob_predict.append(display[i])
            col_prob_answers.append(y_test[i])
            col_prob_index.append(temp_index[i])
            col_prob_disc.append(perc_dif[i])

    print("")
    print(f'Predictions: {display}')
    print(f'    Answers: {list(np.round(y_test,4))}')
    print(f"Perc disc  : {list(np.round(perc_dif, 3))}")
    print(f"Avg disc   : {np.round(np.sum(np.round(perc_dif, 3))/len(y_test), 3)}")
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
    print(f"Overall average discrepancy(%): {np.round(sum(ra)/len(ra), 3)}")
    # plt.show()
    return sum(ra)/len(ra)


# Displays 2 graphs, first graph plots all test data points with an ideal predicted vs ideal y=x line.
# Second graph plots all test data points with perc discrepancy > tolerance against y=x line.
# Identifies inputs with a perc discrepancy more than tolerance, and dumps them in 8-Problematic folder
# Note: 8-Problematic folder is not cleaned and will need to be manually cleaned after each run if desired
def analyse_results():

    plt.clf()
    print(f"Total number of tests: {repetitions*no_test}")
    print(f"Number of discrepancies more than {tolerance}%: {len(col_prob_disc)}")

    if len(col_prob_disc) == 0:
        print(f"No significant discrepancies more than {tolerance}%.")

    else:
        print(f"Worst discrepancy: {np.round(np.max(np.asarray(col_prob_disc)), 3)}")

        plt.scatter(col_predictions, col_answers)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        lims = [
            np.min([col_predictions, col_answers]),  # min of both axes
            np.max([col_predictions, col_answers]),  # max of both axes
        ]
        plt.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        plt.show()

        plt.clf()
        plt.scatter(col_prob_predict, col_prob_answers)
        plt.xlabel("Predicted")
        plt.ylabel("Actual")
        lims = [
            np.min([col_prob_predict, col_prob_answers]),  # min of both axes
            np.max([col_prob_predict, col_prob_answers]),  # max of both axes
        ]
        plt.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
        plt.show()

        prob_data = list(dict.fromkeys(col_prob_index))

        file_number = 0
        for file in os.listdir(os.path.join(parent_path, r"0-Original")):
            if file.endswith(".png"):
                for i in range(len(prob_data)):
                    if file_number == prob_data[i]:
                        shutil.copy2(os.path.join(os.path.join(parent_path, r"0-Original"), file),
                                     os.path.join(parent_path, r"8-Problematic"))

                file_number += 1

# Add extra input data if sf_check and keff_check is true.
extra_eigens = 0

if sf_check:
    extra_eigens += 1
if keff_check:
    extra_eigens += 1
    keff_array = read_data(keff_input)

# Defines the number of inputs for each sample
# (I.e. projections on eigenfaces + any additional things added like scaling factor)
x = np.empty((n_samples, max_eigen + extra_eigens))

print("Compiling inputs for each image.")

# Note: Only magnitude affects stuff here not the order of the input etc.
for a in range(n_samples):
    # Find the projection values and add to the input data
    for b in range(max_eigen):
        x[a][b] = np.dot(mag_array[a].ravel(), top_ten_eigen[b].ravel())

    # Add Scaling Factor (Add an arbitary magnitude if want to see any effect)
    if sf_check:
        x[a][max_eigen] = final_scale_percent[a]    # *10000000

    # Add Keff (Same as scaling factor, needs an arbitrary magnitude)
    if keff_check:
        x[a][-1] = keff_array[a]

# For debugging projection values for a particular eigenface
# for i in range(n_samples):
#    print(x[i][9])

x_ = [i for i in range(repetitions)]

# If only want 1 iteration with a fixed gamma value (still has *n* repetitions)
if not gamma_opt:
    one_iteration(g_factor, no_test)

else:
    # To Optimise gamma between the lower limit and upper limit, with a predefined step size
    # Plots a graph of gamma versus average discrepancy for one iterations (ie avg discrepancies of *n* repetitions)
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

analyse_results()


