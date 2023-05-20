import boto3

def get_vcpu_limit():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_account_attributes(
        AttributeNames=['maxvcpus']
    )
    for attribute in response['AccountAttributes']:
        if attribute['AttributeName'] == 'maxvcpus':
            return int(attribute['AttributeValues'][0]['AttributeValue'])

# Usage
vcpu_limit = get_vcpu_limit()
print(f"Current vCPU limit: {vcpu_limit}")
