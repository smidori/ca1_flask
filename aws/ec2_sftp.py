#pip install boto3
#pip install paramiko
import boto3
import time
import paramiko
import os


#variables 
region = 'eu-central-1'
imageId = 'ami-0ec7f9846da6b0f61'
tagName = {"Key": "Name", "Value": "CA-Silvia"}
keyName = 'cctkey1'
subnetId = 'subnet-0c9be6358a7c49808'
sec_grp = 'sg-036cfa85ed283ecc7'
private_key_path = f'./{keyName}.pem'
directory_path = '/home/ubuntu/ca'
hosted_zone_id = 'Z0377007Q8BSIW3W8YMM'
subdomain = "ca-silvia.cctstudents.com"

# Set up EC2 client
ec2_client = boto3.client('ec2', region_name=region)

# Specify the parameters for creating the instance
instance_params = {
    'ImageId': imageId,
    'InstanceType': 't2.micro',
    'KeyName': keyName,
    'MinCount': 1,
    'MaxCount': 1,
    'SecurityGroupIds': [sec_grp],
    'SubnetId': subnetId,
    'TagSpecifications': [
        {
            'ResourceType': 'instance',
            'Tags': [tagName]
        },
    ],
    'BlockDeviceMappings': [
        {
            'DeviceName': '/dev/sda1',
            'Ebs': {
                'DeleteOnTermination': True,
            }
        },
    ],
}


# Create the EC2 instance
response = ec2_client.run_instances(**instance_params)

# Get the instance ID of the newly created instance
instance_id = response['Instances'][0]['InstanceId']
print(f"Created EC2 instance with ID: {instance_id}")


print(f"Waiting for the instance to be in the 'running' state...")
while True:
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
    if instance_state == 'running':
        break
    time.sleep(5)  # Wait for 5 seconds before checking again

# Get the public IP address of the EC2 instance
response = ec2_client.describe_instances(InstanceIds=[instance_id])
ip_server = response['Reservations'][0]['Instances'][0]['PublicIpAddress']



#CREATING ROUTE53
print(f'Creating or updating the route53: {subdomain}')
response = boto3.client('route53').change_resource_record_sets(
    HostedZoneId=hosted_zone_id,
    ChangeBatch={
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': subdomain,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [
                        {
                            'Value': ip_server
                        },
                    ],
                }
            },
        ]
    }
)

print(f"Starting to configure the EC2...")

# Set up SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Load the private key
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)


#try to connect through the SSH
retry_count = 5 #max attempts
retry_delay = 10 #time between every attempt

for _ in range(retry_count):
    try:
        ssh.connect(ip_server, username='ubuntu', pkey=private_key)
        print("SSH connection successful")
        break
    except Exception as e:
        print(f"SSH connection failed: {str(e)}")
        print("Retrying...")
        time.sleep(retry_delay)

# Connect to the instance using the key
#ssh.connect(ip_server, username='ubuntu', pkey=private_key)

print('Uploading files to the instance ...')
# Set up SFTP client
sftp = ssh.open_sftp()

#create directory in the instance
stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {directory_path}')

#copy the fileapp.py
sftp.put('../app.py', os.path.join(directory_path, 'app.py').replace('\\', '/'))

# List of folders that needs to be copied and place to where
folder_mapping = {
    '../static': 'static',
     '../templates': 'templates',
}

# Upload files or folders to the remote server

for local_folder, remote_destination in folder_mapping.items():
    local_folder_path = os.path.abspath(local_folder)
    #replace is used to fix the separator from windows '\' to linux '/'
    remote_destination_path = os.path.join(directory_path, remote_destination).replace('\\', '/') 


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

# Close the SFTP client
sftp.close()

print(f"Executing few commands in ec2 server")
# Nginx configuration
nginx_config = f"""
server {{
    listen 80;
    server_name {subdomain};

    location / {{
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""

    
# create a tmp file to save tge nginx configuration
remote_filename = '/tmp/nginx_config.conf'
with ssh.open_sftp().file(remote_filename, 'w') as remote_file:
    remote_file.write(nginx_config)


# Command list
#execute flask in background and create log
commands = [
    'sudo apt update',
    'sudo apt install python3-pip -y',
    'sudo pip3 install flask',
    'flask --version',
    'sudo apt-get install nginx -y', #used to redirect request from port 80 to 5000
    f"nohup bash -c 'cd {directory_path} && python3 -m flask run --host=0.0.0.0 > flask.log 2>&1 &'",
    'sudo apt-get install nginx -y',
    'sudo cp {} /etc/nginx/sites-available/site.conf'.format(remote_filename),
    'sudo ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/',
    'sudo nginx -t',
    'sudo systemctl restart nginx',
]


# Execute commands sequentially
for command in commands:
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    # Check if the command executed successfully
    if exit_status == 0:
        print(f"Command '{command}' executed successfully")
    else:
        error = stderr.read().decode().strip()
        print(f"Command '{command}' failed with error:\n{error}")
        break


print('The application is available on:')

print(f"http://{ip_server}:5000 or http://{subdomain}")


# Close the SSH connection
ssh.close()