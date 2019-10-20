# Pickle file is generated from Fourier_Transform.py (image array as a list)

import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

'''User Input'''

# Stores fitting graphs
save_path = r"C:\Users\Han Xuan\Desktop\OneDrive - Imperial College London\Attachments\Input Storage\Simulations\33m ML\Fourier Transformed Scaled"

# Stores fitting graphs that failed to be optimised
failed_path = r""

# Stores ft_scaling, must contain ft images (unscaled)
load_path = r"C:\Users\Han Xuan\Desktop\OneDrive - Imperial College London\Attachments\Input Storage\Simulations\33m ML\Fourier Transformed"

# Centre pixel for a 512x512 img
centre_pixel = 256

# Max pixel radius to check (lower limit => faster)
limit = 50

'''End User Input'''


# Set the amplitude for a distance from the centre
def update_radial_amp(n, r, c, distance_dict, image_array):
    dist = np.sqrt(np.power(np.abs(r - centre_pixel), 2) + np.power(np.abs(c - centre_pixel), 2))
    if dist < limit - 0.1:
        #distance_dict[round(dist, 1)].append(np.log(image_array[n][r][c]))
        distance_dict[round(dist, 1)].append(image_array[n][r][c])

def find_average(distance_dict):
    y = []
    for a in range(limit*10):
        if len(distance_dict[a/10]) != 0:
            y.append(sum(distance_dict[a/10])/len(distance_dict[a/10]))
    return y


# Gaussian function
def gauss_function(x, a, x0, sigma=3, c=11):
    return a*np.exp(-(x-x0)**2/(2*sigma**2)) + c


def fit_gaussian(x, y, a_guess, x0_guess, n):
    plt.clf()
    plt.plot(x, y)
    try:
        popt, pcov = curve_fit(gauss_function, x, y, p0=[a_guess, x0_guess, 3, 11])
        plt.plot(x, gauss_function(x, *popt))
        plt.savefig(os.path.join(save_path, str(n)), bbox_inches='tight', pad_inches=0)

    except RuntimeError:
        print(f"Optimisation could not be performed on curve {n}.")
        popt = [a_guess, x0_guess, 3, 11]
        y_return = []
        for i in range(len(x)):
            y_return.append(gauss_function(x[i], a_guess, x0_guess))
        plt.plot(x, y_return)
        plt.savefig(os.path.join(failed_path, str(n)), bbox_inches='tight', pad_inches=0)
        # plt.show()


    # To fit Gaussian function manually
    #z = []
    #for i in range(len(x)):
    #    z.append(gauss_function(x[i], a_guess, x0_guess, 3))
    #plt.plot(x, z)
    #plt.show()

    ring_dist = popt[1]
    return ring_dist, popt


def main():
    obj_input_path = os.path.join(load_path, "ft_image_array")
    with open(obj_input_path, 'rb') as pickleFile:
        image_array = pickle.load(pickleFile)

    # Remove the centre bright spot (Should have been removed earlier but just in case)
    for i in range(len(image_array)):
        image_array[i][256][256] = 0

    # Saves all these variables in a pickle
    ring_dist = []
    popt_array = []
    x_array = []
    y_array = []

    print("Plotting radial intensity curves to find rough scaling factor. This would take some time.")
    # Scans the image starting from the centre and increases outwards, measuring intensity of pixels
    for n in range(len(image_array)):
        radius_pix = [x/10 for x in range(limit*10)]
        values = [[] for i in range(limit*10)]
        distance_dict = dict(zip(radius_pix, values))
        for r in range(image_array[n].shape[0]):
            for c in range(image_array[n].shape[1]):
                update_radial_amp(n, r, c, distance_dict, image_array)
        # Fitting
        y = find_average(distance_dict)
        y = np.asarray(y)
        y = y[10:]
        x = radius_pix[10:len(y) + 10]

        a_guess = np.amax(y) - 11
        y_index = np.where(y == np.amax(y))
        x0_guess = x[y_index[0][0]]
        t1, t2 = fit_gaussian(x, y, a_guess, x0_guess, n)

        # To save these in pickle
        ring_dist.append(t1)
        popt_array.append(t2)
        x_array.append(x)
        y_array.append(y)

    # print(ring_dist)
    obj_output_path = os.path.join(load_path, "ft_scaling")
    with open(obj_output_path, 'wb') as pickleFile:
        pickle.dump((ring_dist, popt_array, x_array, y_array), pickleFile)


if __name__ == "__main__":
    main()

'''def calc_dist(n, r, c):
    dist = np.sqrt(np.power(np.abs(r-centre_pixel), 2) + np.power(np.abs(c-centre_pixel), 2))
    if dist < 30:
        return dist
    else:
        return None
'''

'''
def calc_gaussian_mean(x, y):

    # Plot histogram of magnitude against frequency
    n, bins, patches = plt.hist(x=y, bins=x, color='#0504aa', alpha=0.7, rwidth=0.85)
    x = bins[:-1]
    y = n

    # estimate mean and standard deviation
    mean = np.sum(x * y)
    sigma = np.sum(y * (x - mean)**2)

    # popt is the optimal values for parameters so sum of squared residues is minimised
    popt, pcov = curve_fit(gauss_function, x, y, p0=[np.max(n), bins[np.argmax(n)], 1])

    # Optional Plotting
    plt.grid(axis='y', alpha=0.75)
    plt.xlabel('log(Magnitude)')
    plt.ylabel('Frequency')
    plt.title('Magnitude against frequency plot')
    maxfreq = n.max()
    # Set a clean upper y-axis limit.
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    # plot the fit results
    plt.plot(x, gauss_function(x, *popt))
    plt.show()
    return popt[1]
'''

'''
mean_mag = []
for n in range(len(image_array)):
    mag_array = []
    for r in range(image_array[n].shape[0]):
        for c in range(image_array[n].shape[1]):
            mag_array.append(image_array[n][r][c])

    mean_mag.append(calc_gaussian_mean(mag_array))

print(mean_mag)
mean_dist = []  # In pixel units

for n in range(len(image_array)):
    total_dist = []
    for r in range(image_array[n].shape[0]):
        for c in range(image_array[n].shape[1]):
            if mean_mag[n]*1.3 < np.log(image_array[n][r][c]):
                if calc_dist(n, r, c)!= None:
                    dist = calc_dist(n, r, c)
                total_dist.append(dist)
    mean_dist.append(sum(total_dist)/len(total_dist))

print(mean_dist)
'''