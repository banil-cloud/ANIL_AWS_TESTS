import boto3
import csv
from io import StringIO
from datetime import datetime

def fetch_ec2_instances():
    # Initialize Boto3 client for EC2
    ec2_client = boto3.client('ec2')

    # Fetching EC2 instance information
    ec2_regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    ec2_instances = []

    # Get current time
    current_time = datetime.utcnow()

    # Iterate through each region
    for region in ec2_regions:
        # Initialize EC2 client for the current region
        ec2 = boto3.client('ec2', region_name=region)

        # Fetch instances for the region
        ec2_response = ec2.describe_instances()
        
        # Extract instance information
        for reservation in ec2_response['Reservations']:
            for instance in reservation['Instances']:
                launch_time = instance['LaunchTime']
                launch_datetime = datetime.strptime(launch_time.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
                # Calculate the difference in days
                time_difference = current_time - launch_datetime
                if time_difference.days >= 2:
                    ec2_instances.append({
                        'Region': region,
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'LaunchTime': launch_datetime
                    })
                    print(f"New instance detected in {region} region: {instance['InstanceId']}")

    return ec2_instances

def save_to_s3(bucket_name, file_key, csv_data):
    # Initialize Boto3 client for S3
    s3_client = boto3.client('s3')

    # Upload the CSV data to S3
    s3_client.put_object(Body=csv_data.getvalue(), Bucket=bucket_name, Key=file_key)

def lambda_handler(event, context):
    # Fetch EC2 instances data
    ec2_instances = fetch_ec2_instances()

    # Print EC2 instances with regions
    print("EC2 Instances:")
    for instance in ec2_instances:
        print(f"Region: {instance['Region']}, Instance ID: {instance['InstanceId']}, Instance Type: {instance['InstanceType']}, State: {instance['State']}, Launch Time: {instance['LaunchTime']}")

    # Prepare CSV data
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)

    # Write EC2 instance information
    csv_writer.writerow(['Region', 'Instance ID', 'Instance Type', 'State', 'Launch Time'])
    for instance in ec2_instances:
        csv_writer.writerow([instance['Region'], instance['InstanceId'], instance['InstanceType'], instance['State'], instance['LaunchTime']])

    # Reset the StringIO buffer position to the beginning
    csv_data.seek(0)

    # Get current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Define S3 bucket and file key
    bucket_name = 'script07'
    file_key = f'ec2_instances_{current_datetime}.csv'

    # Save CSV data to S3
    save_to_s3(bucket_name, file_key, csv_data)

    return {
        'statusCode': 200,
        'body': 'EC2 instances CSV file created and saved to S3'
    }
