
import paramiko
import os

# Set up SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

#variables 
directory_path = '/home/ubuntu/ca'
ip_server = '18.197.19.217'

# Load the private key from the .pem file
private_key_path = './cctkey1.pem'
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)


#keyName = os.path.basename(key_path).split('.')[0],


# Connect to the Ubuntu machine using the key
ssh.connect(ip_server, username='ubuntu', pkey=private_key)

# # Set up SFTP client
sftp = ssh.open_sftp()

# Define the list of source folders and their corresponding destination paths
folder_mapping = {
    '../static': 'static',
     '../templates': 'templates',
}


stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {directory_path}')

# Upload files or folders to the remote server
sftp = ssh.open_sftp()

for local_folder, remote_destination in folder_mapping.items():
    local_folder_path = os.path.abspath(local_folder)
    #replace is used to fix the separator from windows '\' to linux '/'
    remote_destination_path = os.path.join(directory_path, remote_destination).replace('\\', '/') 
    
    print(f"REMOTE DESTINATION PATH: {remote_destination_path}")


    for root, dirs, files in os.walk(local_folder_path):
        # Create the corresponding remote directory structure
        remote_dir = os.path.join(remote_destination_path, root.replace(local_folder_path, '').lstrip(os.sep))
        #replace is used to fix the separator from windows '\' to linux '/'
        remote_dir = remote_dir.replace('\\', '/')

        sftp.mkdir(remote_dir)

        for file in files:
            local_file_path = os.path.join(root, file)
            #replace is used to fix the separator from windows '\' to linux '/'
            remote_file_path = os.path.join(remote_dir, file).replace('\\', '/')
            sftp.put(local_file_path, remote_file_path)
            print(f"Uploaded {local_file_path} to {remote_file_path}")


sftp.put('../app.py', os.path.join(directory_path, 'app.py').replace('\\', '/'))

# Close the SFTP client
sftp.close()

#run flask
stdin, stdout, stderr = ssh.exec_command(f'cd {directory_path}')
stdin, stdout, stderr = ssh.exec_command(f'python3 -m flask run --host=0.0.0.0')





# Close the SSH connection
ssh.close()