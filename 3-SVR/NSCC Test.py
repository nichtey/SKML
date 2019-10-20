import pickle
from dataclasses import dataclass, field
import os, paramiko, time, re
import json


@dataclass
class Sh_Replacement_Keys:
	name: str = ''
	walltime: str = ''
	project: str = ''
	mx3_file: str = ''


@dataclass
class Parameters:
    job_set_name: str = 'Optimisation'
    local_path: str = r'C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Python Scripts\For NSCC'
    local_file: str = r'OptimiseSVR.py'
    ssh_hostname: str = 'astar.nscc.sg'
    remote_path: str = '/scratch/users/astar/imre/chenxy14/Micromagnetics/sk-ML'
    remote_username: str = 'chenxy1e'
    rsa_key_path: str = r'C:/Users/nicht/OneDrive - Imperial College London/Python 3.7.3/Input Storage/33series - extra simulations/rsa-key//nscc_imre.txt'
    walltime: str = '1:00:00'
    project: str = '13001265'


def main():
    params = Parameters()
    sh_keys = Sh_Replacement_Keys()
    sh_path = r'C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Python Scripts\For NSCC\ad_hoc.sh'

    try:
        # setup ssh
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        rsakey = paramiko.RSAKey.from_private_key_file(params.rsa_key_path)

        ssh_client.connect(params.ssh_hostname, username=params.remote_username, pkey=rsakey)
        ftp_client = ssh_client.open_sftp()
        # update remote mx3 path
        params.remote_path = params.remote_path + '/' + params.job_set_name

        try:
            ftp_client.chdir(params.remote_path)
            print('Remote directory %s already exist.' % params.remote_path)
        except:
            print('Remote directory %s does not exist. Making directory.' % params.remote_path)
            # create new remote folder
            ftp_client.mkdir(params.remote_path)

    except Exception as Argument:
        print('Connection to remote location failed with exception: %s' % Argument)
        return
    local_sh_path_and_filename = os.path.join(r"C:\Users\nicht\OneDrive - Imperial College London\Python 3.7.3\Python Scripts\For NSCC", "ad_hoc.sh")
    remote_sh_path_and_filename = params.remote_path + '/' + "ad_hoc.sh"

    ftp_client.put(local_sh_path_and_filename, remote_sh_path_and_filename)
    ftp_client.put(os.path.join(params.local_path, params.local_file), params.remote_path + "/" + params.local_file)

    try:
        # chan = ssh_client.get_transport().open_session()
        stdin, stdout, stderr = ssh_client.exec_command('qsub ' + remote_sh_path_and_filename)
        print('Submitted job: %s ' % params.local_file)
        msg = stdout.channel.recv(4096).decode('ascii')
        exit_status = stdout.channel.recv_exit_status()
        print('Submitted job: %s with message: %s and exit status: %d' % (params.local_file, msg, exit_status))

        if exit_status != 0:
            raise Exception("Error submitting job.")

    except Exception as Argument:
        print('Failed to submit job with exception: %s' % Argument)


main()
