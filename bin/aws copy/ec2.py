import boto3
import time
import paramiko


# Set up EC2 client
ec2_client = boto3.client('ec2', region_name='eu-central-1')

# Specify the parameters for creating the instance
instance_params = {
    'ImageId': 'ami-0ec7f9846da6b0f61',
    'InstanceType': 't2.micro',
    'KeyName': 'cctkey1',
    'MinCount': 1,
    'MaxCount': 1,
    'SecurityGroupIds': ['sg-036cfa85ed283ecc7','sg-046122f5e215dc6b8'],
    'SubnetId': 'subnet-0c9be6358a7c49808',
    'UserData': '''
        #!/bin/bash
        echo "Running a Linux commands -> updating, installing flask and setup environment"
        sudo apt update
        sudo apt install python3-pip -y
        sudo pip3 install flask
        flask --version 
    ''',
    'TagSpecifications': [
        {
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': 'CA-Silvia'},
            ]
        },
    ]
}


# Create the EC2 instance
response = ec2_client.run_instances(**instance_params)

# Get the instance ID of the newly created instance
instance_id = response['Instances'][0]['InstanceId']
print(f"Created EC2 instance with ID: {instance_id}")



# Wait for the instance to be in the 'running' state
while True:
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
    if instance_state == 'running':
        break
    time.sleep(5)  # Wait for 5 seconds before checking again

# Get the public IP address of the EC2 instance
response = ec2_client.describe_instances(InstanceIds=[instance_id])
public_ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

# Set up SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Connect to the EC2 instance using SSH
private_key_path = './cctkey1.pem'
ssh_client.connect(hostname=public_ip, username='ec2-user', key_filename=private_key_path)

