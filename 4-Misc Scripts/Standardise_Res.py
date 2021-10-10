import cv2
import os
import numpy as np
import csv
import matplotlib.pyplot as plt

'''User Input'''
load_path = r""
save_path = r""

# cmd_check = 0 to create csv file to input the nm per pixel resolution
# cmd_check = 1 to standardise pixel resolution to 4
cmd_check = 2
'''End User Input'''

def create_res_csv():

    file_names = []
    for file in os.listdir(load_path):
        if file.endswith(".png"):
            file_names.append(file)

    with open(os.path.join(load_path, 'nm_per_pixel.csv'), 'w', newline='') as csvfile:
        file_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['File Name', 'nm_per_pixel'])

        for i in range(len(file_names)):
            file_writer.writerow([file_names[i]])

def read_data():

    with open(os.path.join(load_path, 'nm_per_pixel.csv'), mode='r') as csv_file:
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


def saveImage(imageToSave, name):

    # imageToSave[256][256] = 0
    x = np.amin(imageToSave)
    # Check if negative infinity, then replace by second smallest value.
    if np.isinf(np.amin(imageToSave)):
        x = np.partition(imageToSave.flatten(), 1)[1]

    array_scale = np.amax(imageToSave) - x
    temp = np.subtract(imageToSave, x)
    temp2 = np.divide(temp, array_scale)
    temp3 = np.multiply(temp2, 255)
    temp4 = np.rint(temp3)
    cv2.imwrite(os.path.join(save_path, name), temp4)


def loadImage():

    file_names = []
    my_images = []

    for file in os.listdir(load_path):
        if file.endswith(".png"):
            temp = cv2.imread(os.path.join(load_path, file))
            my_images.append(temp)
            file_names.append(file)

    return my_images, file_names

def main():

    if cmd_check == 0:
        create_res_csv()

    if cmd_check == 1:
        images, file_names = loadImage()
        resize = np.divide(read_data(), 4)
        resized_img = []

        for i in range(len(images)):
            width = round(images[i].shape[1]*resize[i])
            height = round(images[i].shape[0]*resize[i])
            dim = (int(width), int(height))
            resized_img.append(cv2.resize(images[i], dim, interpolation=cv2.INTER_CUBIC))

        cropped_img = []

        for i in range(len(resized_img)):
            cropped_img.append(resized_img[i][0:512, 0:512])
            cropped_img.append(resized_img[i][resized_img[i].shape[0]- 512:resized_img[i].shape[0], 0:512])
            cropped_img.append(resized_img[i][0:512, resized_img[i].shape[0] - 512:resized_img[i].shape[0]])
            cropped_img.append(resized_img[i][resized_img[i].shape[0]- 512:resized_img[i].shape[0], resized_img[i].shape[0] - 512:resized_img[i].shape[0]])


        for i in range(len(resized_img)):
            saveImage(cropped_img[i*4], "z_part0_"+ file_names[i])
            saveImage(cropped_img[i*4+1], "z_part1_" + file_names[i])
            saveImage(cropped_img[i*4+2], "z_part2_" + file_names[i])
            saveImage(cropped_img[i*4+3], "z_part3_" + file_names[i])

    if cmd_check == 2:
        images, file_names = loadImage()
        cropped_img = []
        for i in range(len(images)):
            cropped_img.append(images[i][0:512, 0:512])
            cropped_img.append(images[i][images[i].shape[0]- 512:images[i].shape[0], 0:512])
            cropped_img.append(images[i][0:512, images[i].shape[0] - 512:images[i].shape[0]])
            cropped_img.append(images[i][images[i].shape[0]- 512:images[i].shape[0], images[i].shape[0] - 512:images[i].shape[0]])

        for i in range(len(images)):
            saveImage(cropped_img[i*4], "z_part0_"+ file_names[i])
            saveImage(cropped_img[i*4+1], "z_part1_" + file_names[i])
            saveImage(cropped_img[i*4+2], "z_part2_" + file_names[i])
            saveImage(cropped_img[i*4+3], "z_part3_" + file_names[i])

if __name__=="__main__":
    main()
