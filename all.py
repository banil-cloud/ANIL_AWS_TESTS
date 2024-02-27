import boto3
import csv

# Initialize the Boto3 clients for EC2, Lambda, and ELB services
ec2_client = boto3.client('ec2')
lambda_client = boto3.client('lambda')
elb_client = boto3.client('elbv2')

# Fetch all AWS regions
response = ec2_client.describe_regions()
aws_regions = [region['RegionName'] for region in response['Regions']]

# Open CSV file in write mode
with open('aws_resources_info.csv', 'w', newline='') as csvfile:
    # Define field names
    fieldnames = ['Resource Type', 'Region', 'Resource Name', 'Resource ARN', 'Creation/Last Modified Time', 'Other Information']
    # Initialize CSV writer
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write header
    writer.writeheader()
    
    # Fetch and write EC2 instances information
    for region in aws_regions:
        print(f"Fetching EC2 instances in {region}...")
        ec2_response = ec2_client.describe_instances()
        reservations = ec2_response['Reservations']
        for reservation in reservations:
            instances = reservation['Instances']
            for instance in instances:
                creation_time = instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S')
                row = {
                    'Resource Type': 'EC2 Instance',
                    'Region': region,
                    'Resource Name': instance['InstanceId'],
                    'Resource ARN': '',
                    'Creation/Last Modified Time': creation_time,
                    'Other Information': f"Instance Type: {instance['InstanceType']}, State: {instance['State']['Name']}, Private IP: {instance.get('PrivateIpAddress', 'N/A')}, Public IP: {instance.get('PublicIpAddress', 'N/A')}"
                }
                writer.writerow(row)
    
    # Fetch and write Lambda functions information
    for region in aws_regions:
        print(f"Fetching Lambda functions in {region}...")
        lambda_response = lambda_client.list_functions()
        functions = lambda_response['Functions']
        for function in functions:
            last_modified = function.get('LastModified', 'N/A')
            if isinstance(last_modified, str):
                last_modified = last_modified.split('T')[0]
            row = {
                'Resource Type': 'Lambda Function',
                'Region': region,
                'Resource Name': function['FunctionName'],
                'Resource ARN': function['FunctionArn'],
                'Creation/Last Modified Time': last_modified,
                'Other Information': f"Runtime: {function['Runtime']}, Handler: {function['Handler']}, Memory: {function['MemorySize']}, Timeout: {function['Timeout']}"
            }
            writer.writerow(row)
    
    # Fetch and write ELB information
    for region in aws_regions:
        print(f"Fetching load balancers in {region}...")
        elb_response = elb_client.describe_load_balancers()
        load_balancers = elb_response['LoadBalancers']
        for lb in load_balancers:
            creation_time = lb['CreatedTime'].strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'Resource Type': 'ELB',
                'Region': region,
                'Resource Name': lb['LoadBalancerName'],
                'Resource ARN': lb['LoadBalancerArn'],
                'Creation/Last Modified Time': creation_time,
                'Other Information': f"DNS Name: {lb.get('DNSName', 'N/A')}, Type: {lb['Type']}, VPC ID: {lb['VpcId']}, Availability Zones: {lb['AvailabilityZones']}, Security Groups: {lb.get('SecurityGroups', 'N/A')}, Subnets: {lb.get('Subnets', 'N/A')}, State: {lb.get('State', 'N/A')}, Scheme: {lb.get('Scheme', 'N/A')}"
            }
            writer.writerow(row)
