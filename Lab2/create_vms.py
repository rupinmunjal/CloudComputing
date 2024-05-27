# Import the required Boto3 library
import boto3

# Initialize EC2 resource and client objects
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

# Define Subnet IDs and CIDR blocks
subnet_ids = ['subnet-013ef85248cb81a9f', 'subnet-03dfff402c3c5ddbf', 'subnet-0ec3e97ca098ebfd8']
CIDR = ['172.31.0.0/20', '172.31.16.0/20', '172.31.32.0/20']

# Define security group IDs
security_group_ids = ['sg-0a6d933a187bfa088', 'sg-0c54bdbc136462e52', 'sg-0e11528e7100c9b10']

# User data script for VM1, VM2, and VM3
user_data_vm1 = '''#!/bin/bash
sudo yum update -y
sudo yum install -y httpd
sudo systemctl start httpd
sudo systemctl enable httpd
'''

user_data_vm2 = '''#!/bin/bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo docker run -p 8081:80 -d nginx
sudo docker run -p 8082:80 -d nginx
sudo docker run --name mongodb1 -d -p 27017:27017 mongo
'''

user_data_vm3 = '''#!/bin/bash
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo docker run -p 8083:80 -d nginx
sudo docker run -p 8084:80 -d nginx
sudo docker run --name mongodb1 -d -p 27017:27017 mongo
'''

# Instances and their corresponding subnets, security group, and CIDR blocks
instances = [
    {'name': 'VM1', 'subnet_index': subnet_ids[0], 'user_data': user_data_vm1, 'security_group_id': security_group_ids[0], 'CIDR': CIDR[0]},
    {'name': 'VM2', 'subnet_index': subnet_ids[1], 'user_data': user_data_vm2, 'security_group_id': security_group_ids[1], 'CIDR': CIDR[1]},
    {'name': 'VM3', 'subnet_index': subnet_ids[2], 'user_data': user_data_vm3, 'security_group_id': security_group_ids[2], 'CIDR': CIDR[2]}
]

# Launch instances using a for loop
for instance in instances:
    # Create instances with specified parameters
    launch = ec2_client.run_instances(
        ImageId='ami-0d887a308369b6881',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='My Key',
        UserData=instance['user_data'],
        NetworkInterfaces=[{
            'SubnetId': instance['subnet_index'],
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [instance['security_group_id']]
        }],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance['name']
                    }
                ]
            }
        ]
    )

    # Print status message indicating successful deployment
    print(f"Instance ID is {launch['Instances'][0]['InstanceId']} with Private IP {launch['Instances'][0]['PrivateIpAddress']} in Subnet {instance['subnet_index']} with CIDR {instance['CIDR']}")
