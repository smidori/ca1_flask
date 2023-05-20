import boto3

client = boto3.client('route53')
hosted_zone_id = 'Z0377007Q8BSIW3W8YMM'
new_record_name = 'a2.cctstudents.com'
new_record_value = '3.126.207.56'

response = client.change_resource_record_sets(
    HostedZoneId=hosted_zone_id,
    ChangeBatch={
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': new_record_name,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [
                        {
                            'Value': new_record_value
                        },
                    ],
                }
            },
        ]
    }
)

print('DNS record created successfully.')
