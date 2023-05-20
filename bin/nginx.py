#pip install boto3
#pip install paramiko
import boto3
import time
import paramiko
import os


#variables 
region = 'eu-central-1'
imageId = 'ami-0ec7f9846da6b0f61'
tagName = {"Key": "Name", "Value": "CA-xxx"}
keyName = 'cctkey1'
subnetId = 'subnet-0c9be6358a7c49808'

private_key_path = f'./{keyName}.pem'
directory_path = '/home/ubuntu/ca'

# Set up EC2 client
ec2_client = boto3.client('ec2', region_name=region)


ip_server = '3.126.207.56'


print(f"Starting to configure the EC2...")

# Set up SSH connection
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Load the private key
private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
ssh.connect(ip_server, username='ubuntu', pkey=private_key)


print(f"Executing few commands in ec2 server")












subdomain = "ca-silvia.cctstudents.com"    

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

    
# Criar um arquivo temporário para armazenar a configuração do Nginx
remote_filename = '/tmp/nginx_config.conf'
with ssh.open_sftp().file(remote_filename, 'w') as remote_file:
    remote_file.write(nginx_config)

#execute flask in background and create log
commands = [
    'flask --version',
    'sudo apt-get install nginx -y',
    'sudo cp {} /etc/nginx/sites-available/site.conf'.format(remote_filename),
    'sudo ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/',
    'sudo nginx -t',
    'sudo systemctl restart nginx',
    #f"nohup bash -c 'cd {directory_path} && python3 -m flask run --host=0.0.0.0 > flask.log 2>&1 &'"
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

print(f"http://{ip_server}:5000")


 



# Close the SSH connection
ssh.close()