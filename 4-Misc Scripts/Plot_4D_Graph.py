# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

import matplotlib.pyplot as plt
import os
import csv

'''User Input'''
Stored_Path = r"C:\Users\nicht\Desktop\New folder (3)"
file_name = r"Plot 4d.csv"

'''End User Input'''

# Input should have 4 columns, with the first row being the column header

def read_data(read_file):

    with open(os.path.join(Stored_Path, read_file), mode='r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        perc_disc = []
        gamma = []
        epsilon = []
        C_value = []


        for row in csv_reader:

            # Skip first line
            if line_count == 0:
                line_count += 1

            else:
                perc_disc.append(float(row[0]))
                gamma.append(float(row[1]))
                epsilon.append(float(row[2]))
                C_value.append(float(row[3]))
                line_count += 1

    return perc_disc, gamma, epsilon, C_value

def main():

    perc_disc, gamma, epsilon, C_value = read_data(file_name)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter3D(gamma, epsilon, C_value, c= perc_disc, s=10, cmap='viridis')

    ax.set_xlabel('Gamma')
    ax.set_ylabel('Epsilon')
    ax.set_zlabel('C')
    plt.show()

if __name__ == "__main__":
    main()