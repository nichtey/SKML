import pickle
import numpy as np
import csv
from sklearn import svm
from random import randrange
from multiprocessing import Pool

'''User Input'''

# This script is similar to SVR.py, with redundant parts removed for the purposes of optimising hyper parameters.
# Main differences:
# 1) Optimisation is performed on all hyper parameters
# 2) Script is compatible with multiprocessing for use of multiple cores
# Refer to SVR.py for complete documentation of steps that may not be as well documented here.

# NOTE: USED FOR NSCC: qsub /scratch/users/astar/imre/chenxy14/Micromagnetics/sk-ML/Optimisation/ad_hoc.sh
# Alternatively submit using NSCC Test.py (Recommended)

file_type = r"33D DMI"
parent_path = r"" + '/' + file_type

# Number of processors to use (for multiprocessing), should be equal to number of processors
processors = 24
# Name the output file ___.csv
save_file_name = r"Broad Targeted Sweep.csv"
# Number of Manifolds
repetitions = 1000
# Number of test in each fold
no_test = 5
# Percentage tolerance for discrepancy
tolerance = 5

# AexInput.csv, DmiInput.csv or KappaInput.csv, DdivsqrtAInput.csv or any other csv files
data_file = r"DmiInput.csv"

# If want to add scale factor as one of the inputs (Does not seem to have an effect)
sf_check = False

# If want to add K_eff as one of the inputs (Does not seem to have an effect)
keff_check = False
keff_input = r"keffInput.csv"

g_factor = 0.000000000000000001
e_factor = 0.001
c_factor = 1
max_eigen = 10

# If want to perform optimisation for gamma
lower_limit = 0.00000000000000500
upper_limit = 0.00000000000005000 #8000000
step_size = (upper_limit - lower_limit)/50

# If want to perform optimisation for C and epsilon
lower_limit_c = 0.001
upper_limit_c = 1000
step_size_c = (upper_limit_c-lower_limit_c)/50

lower_limit_e = 0.00001
upper_limit_e = 10
step_size_e = (upper_limit_e - lower_limit_e)/50

'''End User Input'''

# Global variables

col_answers = []
col_predictions = []
col_prob_answers = []
col_prob_predict = []
col_prob_index = []

print("Importing relevant files.")

# Path where eigenfaces_data pickle is stored
eigenface_path = parent_path + '/' + r"7-FT Eigenfaces"
# Path where ft_image_array pickle is stored
ft_image_path = parent_path + '/' + r"2-Fourier Transformed"
# Path where ft_scaling pickle is stored
scaling_path = parent_path + '/' +  r"2-Fourier Transformed"

try:
    # Import eigenfaces
    obj_input_path = eigenface_path + '/' + "eigenface_data"
    with open(obj_input_path, 'rb') as pickleFile:
        eigenfaces = pickle.load(pickleFile)

    # Import no log image array
    obj_input_path = ft_image_path + '/' +  "ft_image_array"
    with open(obj_input_path, 'rb') as pickleFile:
        mag_array = pickle.load(pickleFile)

    # Import Scaling factor
    obj_input_path = scaling_path  + '/' + "ft_scaling"
    with open(obj_input_path, 'rb') as pickleFile:
        scale_array, popt_array, x_array, y_array = pickle.load(pickleFile)

    if sf_check:
        obj_input_path = parent_path + '/' +  "final_scale_percent"
        with open(obj_input_path, 'rb') as pickleFile:
            final_scale_percent = pickle.load(pickleFile)

except (FileNotFoundError):
    #print(f"Problem finding the following file: {obj_input_path}")
    print(FileNotFoundError)

# Only read the first 15 eigenfaces
top_ten_eigen = eigenfaces[:15]
mag_array = np.asarray(mag_array)
n_samples = mag_array.shape[0]
mean_scale = sum(scale_array)/len(scale_array)


def read_data(read_file):

    with open(parent_path + '/' +  read_file, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        my_data = []

        for row in csv_reader:

            if line_count == 0:
                line_count += 1

            else:
                my_data.append(row[1])
                line_count += 1

    my_data = np.asarray(my_data)
    my_data = my_data.astype(np.float64)
    return my_data


def make_predict(g_value, no_test, c_factor, e_factor, col_prob_disc):
    y = read_data(data_file)
    y_test = []
    x_test = []
    x_train = []
    y_train = []
    temp_index = []

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

    clf = svm.SVR(gamma=g_value, C=c_factor, epsilon=e_factor, kernel='rbf')
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

    for i in range(len(perc_dif)):
        if perc_dif[i] > tolerance:
            col_prob_predict.append(display[i])
            col_prob_answers.append(y_test[i])
            col_prob_index.append(temp_index[i])
            col_prob_disc.append(perc_dif[i])

    return col_prob_disc, np.sum(perc_dif)/no_test


def one_iteration(g_factor, no_test, c_factor = 50, e_factor = 0.05):

    ra = []
    col_prob_disc = []
    for i in range(repetitions):
        col_prob_disc, avg_disc = make_predict(g_factor, no_test, c_factor, e_factor, col_prob_disc)
        ra.append(avg_disc)

    col_prob_disc = np.asarray(col_prob_disc)

    return sum(ra)/len(ra), np.max(np.asarray(col_prob_disc)), len(col_prob_disc)


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
for a in range(n_samples):
    # Add projection values to x
    for b in range(max_eigen):
        x[a][b] = np.dot(mag_array[a].ravel(), top_ten_eigen[b].ravel())

    # Add Scaling Factor
    if sf_check:
        x[a][max_eigen] = final_scale_percent[a]# *10000000 # Dependent on magnitude

    # Add Keff
    if keff_check:
        x[a][-1] = keff_array[a]

x_ = [i for i in range(repetitions)]

# To Optimise gamma between the lower limit and upper limit, with a predefined step size
g_factor = lower_limit
gammas = []
epsilons = []
Cs = []

if __name__ == "__main__":

    #Preparing pool_input_list
    while g_factor < upper_limit:
        e_factor = lower_limit_e
        while e_factor < upper_limit_e:
            c_factor = lower_limit_c
            while c_factor < upper_limit_c:
                Cs.append(c_factor)
                epsilons.append(e_factor)
                gammas.append(g_factor)
                c_factor += step_size_c
            e_factor += step_size_e
        g_factor += step_size

    pool_input_list = []
    for i in range(len(gammas)):
        pool_input_list.append([gammas[i], no_test, Cs[i], epsilons[i]])
    print(pool_input_list)

    # Multiprocessing
    with Pool(processes=processors) as p:
        # read in all these files as one dataset
        results = p.starmap(one_iteration, pool_input_list)

    # Write info to file
    with open(parent_path + '/' + save_file_name, 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(
            ['Manifolds', 'no_test', 'no_training', 'max_eigens', 'sf_check', 'keff_check', 'file type',
             'Tests in 1 iteration'])
        file_writer.writerow([repetitions, no_test, n_samples - no_test, max_eigen, sf_check, keff_check, file_type,
                              repetitions * no_test])
        file_writer.writerow(['Perc Disc', 'Disc > ' + str(tolerance) + '%', 'Worst Disc', 'Gamma', 'C', 'Epsilon'])

        for i in range(len(results)):
            file_writer.writerow(
                [results[i][0], results[i][2], results[i][1], pool_input_list[i][0], pool_input_list[i][2], pool_input_list[i][3]])
