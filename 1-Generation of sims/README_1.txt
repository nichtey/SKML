# Notes on generation of Mumax Sims.

- Comprises 4 scripts: 
	1) 01-GenerateMumaxSims - Modified
	2) 02-SubmitSimsToNSCC
	3) 03-NSCCCollateResults
	4) 04-ConvertOVF

- Script 1: 
	Function: To generate a non-discrete series of mumax txt files within a defined range of A and D.
	Outputs: mumax txt files and csv file containing the values of A and D generated for the mumax sims.
	Usage: set mx3_output_path, sim_batch_name, upper and lower Aex and Dind, number_samples, Msat_var and Ku1_var
	Notes: Check thermal seed in txt file is random

-Script 2:
	Function: Submits txt files into NSCC
	Usage: Edit json files, params and file paths

-Script 3:
	Function: Collates all ovf files (local) returned by the NSCC into a folder
	Usage: Set file paths

Script 4:
	Function: Convert OVF files into png files in the same location
	Usage: No config req
