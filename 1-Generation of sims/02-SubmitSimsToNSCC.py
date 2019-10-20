"""
This script reads in a parameters file, a template sh file and a folder of mx3 files, then submit the mx3 files to NSCC server.
"""

import os, paramiko, time, re
import json, uuid
from copy import deepcopy
from dataclasses import dataclass, field

@dataclass
class Sh_Replacement_Keys:
	name: str = ''
	walltime: str = ''
	project: str = ''
	mx3_file: str = ''

@dataclass
class Parameters:
	job_set_name: str = 'st014'
	cache_path: str = ''
	local_path: str = r'C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\33series - extra simulations\mx3-files'
	ssh_hostname: str = 'astar.nscc.sg'
	remote_mx3_path: str = ''
	remote_username: str = ''
	rsa_key_path: str = ''
	walltime: str = '24:00:00'
	project: str = ''

	sh_replacement_keys: Sh_Replacement_Keys = Sh_Replacement_Keys()

	# used to scan an input mx3 file for keywords to replace
	replacement_dict: dict = field(default_factory=dict)


def submit_jobs_to_NSCC():

	params = Parameters()
	params_path_and_filename = r'C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Input Storage\33series - extra simulations\02-SubmitSimsToNSCC-Parameters.json'

	# Load parameters if available
	if params_path_and_filename != '' and os.path.isfile(params_path_and_filename):
		with open(params_path_and_filename) as data_file:
			params_dict = json.load(data_file)
			update_obj_from_dict_recursively(params, params_dict)

	else:
		# user cancelled, or file not found
		return

	# open local_mx3path and find all the mx3 files
	mx3_file_list = [file for file in os.listdir(params.local_path) if file.endswith('.mx3')]

	# check that mx3 files are found
	if len(mx3_file_list) == 0:
		print('No .mx3 files found in %s...\n' % params.local_path)
		return

	# sh file should be kept in the same directory as the json file
	local_sh_path = os.path.split(params_path_and_filename)[0]

	# open local_mx3path and find all the sh files
	sh_file_list = [file for file in os.listdir(local_sh_path) if file.endswith('.sh')]

	# there should be only one sh template file
	assert (len(sh_file_list) == 1)
	sh_template_filename = sh_file_list[0]

	try:
		# setup ssh
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		rsakey = paramiko.RSAKey.from_private_key_file(params.rsa_key_path)

		ssh_client.connect(params.ssh_hostname, username=params.remote_username, pkey=rsakey)
		ftp_client = ssh_client.open_sftp()
		# update remote mx3 path
		params.remote_mx3_path = params.remote_mx3_path + '/' + params.job_set_name

		# check if remote folder exist
		try:
			ftp_client.chdir(params.remote_mx3_path)
			print('Remote directory %s already exist.'%params.remote_mx3_path)
		except:
			print('Remote directory %s does not exist. Making directory.'%params.remote_mx3_path)
			# create new remote folder
			ftp_client.mkdir(params.remote_mx3_path)

		# create a new folder in cache
		cache_folder_tmp = os.path.join(params.cache_path,str(uuid.uuid4()))
		os.makedirs(cache_folder_tmp)

	except Exception as Argument:
		print('Connection to remote location failed with exception: %s'%Argument)

		return

	# constructs replacement dict for sh file
	sh_replacement_dict_general = {
		params.sh_replacement_keys.name: params.job_set_name,
		params.sh_replacement_keys.project: params.project,
		params.sh_replacement_keys.walltime: params.walltime
	}

	# filters, copies to remote, then the job
	for filename in mx3_file_list:

		# filters mx3 file, and dump them in cache
		local_mx3_path_and_filename = os.path.join(cache_folder_tmp, filename)
		remote_mx3_path_and_filename = params.remote_mx3_path + '/' + filename
		FilterFile(params.replacement_dict, os.path.join(params.local_path, filename), local_mx3_path_and_filename)

		# copies mx3 file to remote location
		ftp_client.put(local_mx3_path_and_filename, remote_mx3_path_and_filename)

		# constructs replacement dict for the specific sh file
		sh_replacement_dict = deepcopy(sh_replacement_dict_general)
		sh_replacement_dict[params.sh_replacement_keys.mx3_file] = remote_mx3_path_and_filename

		# filters sh file, and dump them in cache
		local_sh_path_and_filename = os.path.join(cache_folder_tmp, sh_template_filename)
		remote_sh_path_and_filename = params.remote_mx3_path + '/' + sh_template_filename

		# FilterFile use \n as newline character
		FilterFile(sh_replacement_dict, os.path.join(local_sh_path, sh_template_filename), local_sh_path_and_filename)

		# copies sh file to remote location
		ftp_client.put(local_sh_path_and_filename, remote_sh_path_and_filename)

		# tries to submits the sh file using qsub
		try:
			# chan = ssh_client.get_transport().open_session()
			stdin, stdout, stderr = ssh_client.exec_command('qsub ' + remote_sh_path_and_filename)
			print('Submitted job: %s ' % filename)
			msg = stdout.channel.recv(4096).decode('ascii')
			exit_status = stdout.channel.recv_exit_status()
			print('Submitted job: %s with message: %s and exit status: %d'%(filename, msg, exit_status))

			if exit_status != 0:
				raise Exception("Error submitting job.")

		except Exception as Argument:
			print('Failed to submit job with exception: %s' % Argument)

	pass
	return

def FilterFile(replacement_dict: dict, old_path_and_filename, new_path_and_file_name):

	""" Open file and replace all keywords as indicated by replacement_dict. Note that the keys are treated as
	regular expressions."""

	if replacement_dict is not None:

		# set local path and filename
		# local_path_and_filename = os.path.join(params.local_mx3path, filename)

		with open(old_path_and_filename, 'r') as file:
			file_content = file.read()

		# do filtering here
		# NOTE: key is treated as a regular expression
		for key, val in replacement_dict.items():
			# give a lambda function that returns val, to avoid the extra processing of backslash escapes
			file_content = re.sub(key, lambda x: val, file_content)

		# write new contents to file
		# this discard all contents if the file already exist
		# use the linux newline standard
		with open(new_path_and_file_name, 'w', newline='\n') as file:
			file.write(file_content)

def update_obj_from_dict_recursively(some_obj, some_dict):
	"""
	Useful to convert nested json files into nested dataclasses

	Example
	-------
	@dataclass
	class InputOptions:
		path: str = None
		n1: float = 0
		some_thing: Opt2 = Opt2()

	@dataclass
	class Opt2:
		some_string:str = None
		some_num:float = 0.0

	...

	input_dict_list = UI_load_json_file()

	...

	in_opt = InputOptions()
	update_obj_from_dict_recursively (in_opt, input_dict)

	:param some_obj:
	:param some_dict:
	:return:
	"""
	for k in some_dict:
		tmp_v = some_dict[k]
		if isinstance(tmp_v, dict):
			tmp_obj = some_obj.__dict__[k]
			# check if tmp_obj is actually a dict
			if isinstance(tmp_obj, dict):
				# direct update
				some_obj.__dict__[k] = tmp_v
			else:
				# some other object
				update_obj_from_dict_recursively(tmp_obj, tmp_v)

		else:
			some_obj.__dict__.update({k:tmp_v})

if __name__ == '__main__':
	submit_jobs_to_NSCC()
