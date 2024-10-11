import boto3

# Initialize EC2 client
ec2_client = boto3.client('ec2')

# Specify EC2 instance parameters
instance_params = {
    'ImageId': 'ami-051f8a213df8bc089',  # Specify the AMI ID of the instance
    'InstanceType': 't2.micro',  # Specify the instance type
    'KeyName': 'vockey',  # Specify the key pair name
    'MinCount': 1,
    'MaxCount': 1,
    'TagSpecifications': [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'EC2_S2110978'  # Specify the name for the instance
                },
            ]
        },
    ]
}

# Launch EC2 instance
response = ec2_client.run_instances(**instance_params)

# Get instance ID
instance_id = response['Instances'][0]['InstanceId']
print("EC2 instance created with ID:", instance_id)

# Initialize S3 client
s3_client = boto3.client('s3')

# Specify S3 bucket name
bucket_name = 's3-s2110978'

# Create S3 bucket
s3_client.create_bucket(Bucket=bucket_name)
print("S3 bucket created with name:", bucket_name)
