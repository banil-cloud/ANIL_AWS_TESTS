import csv
import boto3
from io import StringIO

def fetch_data():
    # Initialize Boto3 clients for S3, EC2, and VPC
    s3_client = boto3.client('s3')
    ec2_client = boto3.client('ec2')
    vpc_client = boto3.client('ec2')

    # Fetching S3 bucket information
    s3_response = s3_client.list_buckets()
    s3_buckets = [bucket['Name'] for bucket in s3_response['Buckets']]

    # Fetching EC2 instance information
    ec2_response = ec2_client.describe_instances()
    ec2_instances = []
    for reservation in ec2_response['Reservations']:
        for instance in reservation['Instances']:
            ec2_instances.append({
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name']
            })

    # Fetching VPC information
    vpc_response = vpc_client.describe_vpcs()
    vpcs = vpc_response['Vpcs']

    return s3_buckets, ec2_instances, vpcs

def save_to_csv(s3_buckets, ec2_instances, vpcs):
    # Prepare CSV data
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write S3 bucket information
    csv_writer.writerow(['S3 Buckets'])
    for bucket in s3_buckets:
        csv_writer.writerow([bucket])

    # Write EC2 instance information
    csv_writer.writerow([])  # Add an empty row for separation
    csv_writer.writerow(['EC2 Instances'])
    csv_writer.writerow(['Instance ID', 'Instance Type', 'State'])
    for instance in ec2_instances:
        csv_writer.writerow([instance['InstanceId'], instance['InstanceType'], instance['State']])

    # Write VPC information
    csv_writer.writerow([])  # Add an empty row for separation
    csv_writer.writerow(['VPCs'])
    csv_writer.writerow(['VPC ID', 'CIDR Block', 'State'])
    for vpc in vpcs:
        csv_writer.writerow([vpc['VpcId'], vpc['CidrBlock'], vpc['State']])

    # Reset the StringIO buffer position to the beginning
    csv_data.seek(0)

    return csv_data

def lambda_handler(event, context):
    # Fetch data
    s3_buckets, ec2_instances, vpcs = fetch_data()

    # Save data to CSV
    csv_data = save_to_csv(s3_buckets, ec2_instances, vpcs)

    # Initialize Boto3 client for S3
    s3_client = boto3.client('s3')

    # Upload the CSV data to S3
    bucket_name = 'abctesting789'
    file_key = 'aws_info.csv'  # Desired filename in S3
    s3_client.put_object(Body=csv_data.getvalue(), Bucket=bucket_name, Key=file_key)

    return {
        'statusCode': 200,
        'body': 'CSV file created and saved to S3'
    }

