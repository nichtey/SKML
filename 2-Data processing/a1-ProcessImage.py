import cv2
import os
from PIL import Image
import numpy as np
from skimage.filters import median

# Binarisation will stop if error < acceptable error or if no. of black pixels
# have no change after applying mid point theorem
# Note that the goal is to achieve 50% white and 50% black corresponding to zero field magnetisation
# Also applies median filter from the Median_filter script.

'''User Input'''

Stored_Path = r"C:\Users\Han Xuan\Desktop\OneDrive - Imperial College London\Attachments\Input Storage\Simulations\33m ML\33m Original"
Output_Path = r"C:\Users\Han Xuan\Desktop\OneDrive - Imperial College London\Attachments\Input Storage\Simulations\33m ML\33m Processed"

# Type of image file to convert
file_type = ".png"

# Threshold when majority is white
upper_threshold = 200

# Threshold when majority is black
lower_threshold = 60

# Acceptable error (fractional)
error = 0.01

# Perform Median Filtering if true
mf_check = True

'''End User Input'''


def redraw(threshold, file):

    # img is the original image, thresh1 is the binarised image
    img = cv2.imread(os.path.join(Stored_Path, file))
    ret, thresh1 = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    images = [img, thresh1]
    cv2.imwrite(os.path.join(Output_Path, file), images[1])


def count_pixel(file):

    im = Image.open(os.path.join(Output_Path, file))
    pix = im.load()
    black_pixel = 0
    white_pixel = 0

    for x in range(im.size[0]):
        for y in range(im.size[1]):
            if pix[x, y][0] == 255:
                white_pixel += 1
            else:
                black_pixel += 1

    return black_pixel, white_pixel


def repeater(file, upper_threshold, lower_threshold):

    black_pixel_previous = 0
    mid_threshold = (upper_threshold+lower_threshold)/2
    redraw(mid_threshold, file)
    black_pixel, white_pixel = count_pixel(file)

    if (black_pixel > white_pixel):
        upper_threshold = mid_threshold

    else:
        lower_threshold = mid_threshold

    while black_pixel/white_pixel > (1+error) or black_pixel/white_pixel < (1-error):

        mid_threshold = (upper_threshold + lower_threshold) / 2
        redraw(mid_threshold, file)
        black_pixel, white_pixel = count_pixel(file)

        if black_pixel == black_pixel_previous:
            break

        elif black_pixel != black_pixel_previous:
            black_pixel_previous = black_pixel

        if black_pixel > white_pixel:
            upper_threshold = mid_threshold

        else:
            lower_threshold = mid_threshold

    # print(black_pixel, white_pixel)
    # print(mid_threshold)


def median_filter(Stored_Path, Output_Path):
    for file in os.listdir(Stored_Path):
        if file.endswith(file_type):
            img = cv2.imread(os.path.join(Stored_Path, file))
            img = np.asarray(img)
            img = img[:, :, 1]
            med = median(img)
            cv2.imwrite(os.path.join(Output_Path, file), med)


def main():

    # Binarise images such that there is zero field (50% black and 50% white pixels)
    print("Binarising images.")
    for file in os.listdir(Stored_Path):
        if file.endswith(file_type):
            repeater(file, upper_threshold, lower_threshold)

    print("Using median filter on the binarised images.")
    if mf_check:
        median_filter(Output_Path, Output_Path)

if __name__ == "__main__":
    main()