# Notes on SVR

- Comprises 3 Scripts
	1) SVR
	2) OptimiseSVR
	3) NSCC Test

- Script 1: 
	Function: Perform SVR and output results
	
	Usage: 
	1) Set pathing	
	2) Specify repetitions. I.e. Number of iterations to fit and test (applicable only if random_test_check == True)
	3) Specify no_test I.e. Number of test in each iteration
	4) Specify tolerance I.e. percentage discrepancy from actual value
	5) Specify data_file I.e. the type of label SVR should read (make sure it has 2 columns and the 2nd column is filled)
	6) Specify sf_check and keff_check, but has very little impact unless its magnitude is multiplied by a large constant (constant is arbitary and difficult to determine)
	7) Specify hyperparameters (gamma, epsilon and C), and max_eigen (default = 10)
	8) For small Gamma optimisations, can be performed locally by setting limits and step size

	Note: Any change to the input file etc affects optimal hyperparameters.
	      Example: If max_eigen is changed, hyperparameters must be changed as well.

	Important: If using on experimental data where the label is not known, please fill the excel file for the label with some dummy number
	
	Outputs:
	1) Predictions, answers, percentage discrepancy and R2 coefficient (not really useful) for each iteration
	2) Overall average discrepancy, worst discrepancy and number of discrepancies more than tolerance value
	3) Graph of actual vs predicted and graph of outliers
	4) Problematic inputs will be stored in a separate folder 8-Problematic if it has a perc disc > tolerance

- Script 2:
	Function: Optimise hyperparameters for SVR
	Usage: Similar to SVR, specify the step sizes and limits for epsilon, C and gamma

- Script 3:
	Function: Submit script 2 to NSCC
	Usage: Set pathing, check sh file and params
	