# Import the required Boto3 library
import boto3

# Initialize EC2 resource and client objects
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# User data to configure httpd websites
user_data = '''#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
echo "Hi from $(hostname) and Rupin Munjal." > /var/www/html/index.html'''

# Get the default VPC
vpc = list(ec2.vpcs.filter(Filters=[{'Name': 'isDefault', 'Values': ['true']}]))[0]

# Get all subnets in the default VPC and their 'Name' tags
subnets = list(vpc.subnets.all())
for subnet in subnets:
    for tag in subnet.tags:
        if tag['Key'] == 'Name':
            subnet.name = tag['Value']

# Sort the subnets by name
subnets.sort(key=lambda subnet: subnet.name)

# Deploy one EC2 instance per each subnet
for i, subnet in enumerate(subnets, start=1):
    # Create an EC2 instance
    instance = ec2.create_instances(
        ImageId='ami-0d887a308369b6881',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='My Key',
        NetworkInterfaces=[{
            'SubnetId': subnet.id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': ['sg-01fea99d2ef2387ad']
        }],
        UserData=user_data
    )[0]

    # Name the instance
    name = f'VM{i}'
    ec2_client.create_tags(Resources=[instance.id], Tags=[{'Key': 'Name', 'Value': name}])

    # Print instance details
    print(f"Instance {name} (ID: {instance.id}) in Subnet {subnet.id} with Private IP: {instance.private_ip_address}")
