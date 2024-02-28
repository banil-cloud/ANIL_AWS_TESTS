import boto3
import csv

# Initialize the Boto3 clients for EC2, Lambda, ELB, VPC, and S3 services
ec2_client = boto3.client('ec2')
lambda_client = boto3.client('lambda')
elb_client = boto3.client('elbv2')
s3_client = boto3.client('s3')

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
        
        # Initialize the Boto3 client for the EC2 service in the current region
        ec2_client = boto3.client('ec2', region_name=region)
        
        # List all EC2 instances in the current region
        response = ec2_client.describe_instances()
        
        # Extract EC2 instance information from the response
        reservations = response['Reservations']
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

        # Initialize the Boto3 client for the AWS Lambda service in the current region
        lambda_client = boto3.client('lambda', region_name=region)
    
        # List all Lambda functions in the current region
        response = lambda_client.list_functions()
    
        # Extract Lambda function information from the response
        functions = response['Functions']
        
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
        print(f"Fetching ELBs in {region}...")

        # Initialize the Boto3 client for the ELB service in the current region
        elb_client = boto3.client('elbv2', region_name=region)
    
        # List all ELBs in the current region
        response = elb_client.describe_load_balancers()
    
        # Extract ELB information from the response
        elbs = response['LoadBalancers']
        
        for elb in elbs:
            creation_time = elb['CreatedTime'].strftime('%Y-%m-%d %H:%M:%S')
            dns_name = elb.get('DNSName', 'N/A')
            scheme = elb.get('Scheme', 'N/A')  # Check if 'Scheme' key exists
            row = {
                'Resource Type': 'ELB',
                'Region': region,
                'Resource Name': elb['LoadBalancerName'],
                'Resource ARN': elb['LoadBalancerArn'],
                'Creation/Last Modified Time': creation_time,
                'Other Information': f"DNS Name: {dns_name}, Scheme: {scheme}, Type: {elb['Type']}"
            }
            writer.writerow(row)
    
    # Fetch and write VPC information
    for region in aws_regions:
        print(f"Fetching VPCs in {region}...")

        # Initialize the Boto3 client for the EC2 service in the current region
        ec2_client = boto3.client('ec2', region_name=region)
    
        # List all VPCs in the current region
        response = ec2_client.describe_vpcs()
    
        # Extract VPC information from the response
        vpcs = response['Vpcs']
        
        for vpc in vpcs:
            creation_time = vpc.get('CreateTime', 'N/A')
            creation_time_str = creation_time.strftime('%Y-%m-%d %H:%M:%S') if creation_time != 'N/A' else 'N/A'
            row = {
                'Resource Type': 'VPC',
                'Region': region,
                'Resource Name': vpc['VpcId'],
                'Resource ARN': '',
                'Creation/Last Modified Time': creation_time_str,
                'Other Information': ''
            }
            writer.writerow(row)
    
    # Fetch and write S3 bucket information
    print("Fetching S3 buckets...")
    response = s3_client.list_buckets()

    # Extract S3 bucket information from the response
    buckets = response['Buckets']

    for bucket in buckets:
        creation_time = bucket.get('CreationDate', 'N/A')
        creation_time_str = creation_time.strftime('%Y-%m-%d %H:%M:%S') if creation_time != 'N/A' else 'N/A'
        row = {
            'Resource Type': 'S3 Bucket',
            'Region': 'Global',
            'Resource Name': bucket['Name'],
            'Resource ARN': '',
            'Creation/Last Modified Time': creation_time_str,
            'Other Information': ''
        }
        writer.writerow(row)
