import boto3
import csv
from datetime import datetime, timedelta

# Initialize the Boto3 client for the EC2 service
ec2_client = boto3.client('ec2')

# Fetch all AWS regions
response = ec2_client.describe_regions()
aws_regions = [region['RegionName'] for region in response['Regions']]

# Open CSV file in write mode
with open('ec2_instances_info.csv', 'w', newline='') as csvfile:
    # Define field names
    fieldnames = ['Region', 'Instance ID', 'Instance Type', 'State', 'Private IP Address', 'Public IP Address', 'Creation Date']
    # Initialize CSV writer
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write header
    writer.writeheader()
    
    # Iterate over each region
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
                creation_date = instance['LaunchTime']
                age = datetime.now(creation_date.tzinfo) - creation_date
                
                # Check if the instance is older than 2 days
                if age > timedelta(days=4):
                    creation_date_str = creation_date.strftime('%Y-%m-%d %H:%M:%S')
                    row = {
                        'Region': region,
                        'Instance ID': instance['InstanceId'],
                        'Instance Type': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'Private IP Address': instance.get('PrivateIpAddress', 'N/A'),
                        'Public IP Address': instance.get('PublicIpAddress', 'N/A'),
                        'Creation Date': creation_date_str
                    }
                    # Write row to CSV file
                    writer.writerow(row)
