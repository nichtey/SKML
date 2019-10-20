# Notes on 3 Miscellaneous Scripts
# These scripts are either non-essential or works in progress.

Standardise_Res.py
	Function: Scales experimental data in real space based on the resolution of the experimental image (in nm per pixel)
	Note: Usually this involves scaling up since resolution of simulation is much smaller (4 nm per pixel)
	Output: 4 cropped images of the 4 corners of the image.

	Caution: Scaling is non-ideal and paint should be used until this is rectified. This program should only be used to automate
		 the cropping of the images.

Recon_EF_Proj.py
	Function: Reconstructs original real space image from the projection vectors of the inputs.

	Method: 
	1) Sum up the product of the eigenface matrix and the eigenface projection value for each image for the first max_eigen number of images
	2) Combine resultant magnitude information with the phase information to form re^i(theta)
	3) Perform inverse fourier transform.

	Note: This is only for visualisation and insight into what the PCA is capturing in the first few eigenfaces
	      The resulting image may sometimes be unintuitive and hard to understand


Process_odd_FT_img.py
	Function: To fourier transform, then zero pad, then interpolate the image to obtain 512x512 FT image
	Note: This method is for reference only as it does not seem to be working well. Using Standardise_Res is recommended.

Plot_4D_Graph.py
	Function: To plot 4D graphs.