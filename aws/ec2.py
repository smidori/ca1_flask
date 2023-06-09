#pip install boto3
#pip install paramiko
import boto3
import time
import paramiko
import os


#variables
ca_name = 'ca-silvia' 
region = 'eu-central-1'
imageId = 'ami-0ec7f9846da6b0f61'
tagName = {"Key": "Name", "Value": ca_name}
keyName = 'cctkey1'
subnetId = 'subnet-0c9be6358a7c49808'
sec_grp = 'sg-036cfa85ed283ecc7'
private_key_path = f'./{keyName}.pem'
directory_path = '/home/ubuntu/ca'
hosted_zone_id = 'Z0377007Q8BSIW3W8YMM'
subdomain = ca_name + ".cctstudents.com"
file_name_bucket = 'ca_files.zip'
s3_url = 'https://s3.eu-west-1.amazonaws.com/15.cctstudents.com/'+file_name_bucket
nginx_filename = '/tmp/nginx_config.conf'

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
        # Connect to the instance using the key
        ssh.connect(ip_server, username='ubuntu', pkey=private_key)
        print("SSH connection successful")
        break
    except Exception as e:
        print(f"SSH connection failed: {str(e)}")
        print("Retrying...")
        time.sleep(retry_delay)

#print('Uploading files to the instance ...')

# Set up SFTP client
#sftp = ssh.open_sftp()

print(f"Executing few commands in ec2 server")
# Nginx configuration
# nginx_config = f"""
# server {{
#     listen 80;
#     server_name {subdomain};

#     location / {{
#         proxy_pass http://localhost:5000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }}
# }}
# """    
# # create a tmp file to save tge nginx configuration
# with sftp().file(nginx_filename, 'w') as nginx_file:
#     nginx_file.write(nginx_config)

# Command list
commands = [
    'mkdir -p {}'.format(directory_path),
    'sudo apt-get update',
    'sudo apt update && sudo apt-get install -y wget unzip nginx gunicorn',
    'cd {} && sudo wget {}'.format(directory_path, s3_url),    
    'cd {} && sudo unzip {} '.format(directory_path, file_name_bucket),
    "sudo sed -i 's/domain/{}/g' {}/site.conf".format(subdomain, directory_path),
    'sudo apt install python3-pip -y',
    'sudo pip3 install flask',
    'flask --version',
    'sudo mv {}/gunicorn.service /etc/systemd/system/'.format(directory_path),
    'sudo systemctl enable gunicorn',
    'sudo systemctl daemon-reload',
    'sudo systemctl start gunicorn',
    'sudo mv {}/site.conf /etc/nginx/sites-available/site.conf'.format(directory_path),
    'sudo ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/',
    'sudo nginx -t',
    'sudo systemctl restart nginx',
]

#in case there is any error while executing the commands, this variable will be false
success = True

# Execute commands sequentially
for command in commands:
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    # Check if the command executed successfully
    if exit_status == 0:
        print(f"Command '{command}' executed successfully")
    else:
        success = False
        error = stderr.read().decode().strip()
        print(f"Command '{command}' failed with error:\n{error}")
        break

if success: 
    print('The application is available on:')
    print(f"http://{ip_server}:5000 or http://{subdomain}")
else:
    print('Something went wrong :(')

# Close the SFTP client
#sftp.close()

# Close the SSH connection
ssh.close()