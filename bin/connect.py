import paramiko

# EC2 instance details
host = '3.72.65.14'
username = 'Administrator'
private_key_path = './cctkey1.pem'

# Create an SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Load the private key file
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

    # Connect to the EC2 instance
    client.connect(hostname=host, username=username, pkey=private_key)

    # Execute commands or transfer files
    # Here you can add your logic to execute commands or transfer files to the EC2 instance

finally:
    # Close the SSH connection
    client.close()
