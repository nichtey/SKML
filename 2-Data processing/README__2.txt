# Notes on Data processing before SVR

- Comprises 9 Scripts
	1) a0-Compiler
	2) a1-ProcessImage
	3) a2, 5-FourierTransform
	4) a3-FtScaling
	5) a4-RsResize
	6) a4-FsResize
	7) a4c-RefineScale
	8) a6-ScaledFtPCA
	9) a7-PCA_Final

- Script 1: 
	Function: Control all the other 8 scripts from here
	
	Usage: 
	1) Copy reference_img.png (white circle) into parent path (used for script 7)	
	2) Generate blank folders (cmd_check = 0)
	3) Paste all images into 0-Original
	4) Select settings (Default is rough + refined scale in fourier space)
	5) Start Processing (cmd_check = 1)
	6) Generate csv files (cmd_check = 2)

	Note: To view scaling factors used, open the scale_output.csv file generated
	      If have specific images that need to be tested, label it as z so it is at the bottom
	
- Script 2:
	Function: Binarises image such that 50% white and 50% black (for zero field), and applies median filter
	Usage: Set pathing, upper threshold and lower threshold

- Script 3:
	Function: Converts png files to fourier transformed images, also outputs pickled information
	Usage: Set pathing
	Note: Centre white pixel is removed

- Script 4:
	Function: To Perform rough scaling
	
	Method:
	1) Reads the raw magnitudes (Not normalised) from the fourier transformed images
	2) Create a dictionary for the magnitudes and the distance from the centre of the image
	3) Scan through each pixel (within defined limit) and input the magnitude and distance into the dictionary
	4) Plot and save a graph of the magnitude vs distance and fit a gaussian
	5) Find the peak in the graph and pickle the distance from the centre
		
	Usage: Set pathing, limit (default=50)

- Script 5: 
	Function: Normalise rough scaling factor, scale and crop in real space
	Note: Loses a lot of information so not recommended.
	Usage: Set pathing

- Script 6:
	Function: Normalise rough scaling factor, scale and crop fourier transformed image
	Note: Scaling down is not allowed to prevent loss of information
	Usage: Set pathing

- Script 7:
	Function: To perform refined scaling
	
	Method:
	1) Read the reference image (white circle) and input images
	2) Perform matrix multiplication (in range of scan_limit) for each input image and the reference image
	3) Iteratively scale up the input image (within a predefined range) and repeat step 2
	4) Plot and save a graph of the scale vs the value obtained in step 2
	5) Find the peak in the graph
	6) Normalise the refined scaling factor, scale and crop the image
	
	Note: Scaling down not permitted.
	Usage: Set pathing, resize range and step size, and scan range.

- Script 8:
	Function: Prepares things for PCA (Not compatible if rough scaling + refined scaling is specified)
	Usage: Requires ft_data from script 3

- Script 9:
	Function: To perform PCA and output the eigenfaces from the input
	
	Method:
	1) Accepts either the pickle file from script 8 or image files (specify input_check)
	2) Process data into acceptable form and calls PCA library
	3) Reconstruct PCA output into the eigenface
	
	Note: explained_variance_ratio_ can provide information about how much variance captured in each eigenface
	

	
