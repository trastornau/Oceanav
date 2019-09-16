__author__ = 'amu-onlnav'
#Connect to unix remote machine using ssh protocol and run command on it
import paramiko
ssh  = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('136.249.176.191',username='trinop',password='operator')
stdin,stdout,stderr = ssh.exec_command('ls')

ssh.close()