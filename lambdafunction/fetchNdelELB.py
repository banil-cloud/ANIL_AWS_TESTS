import boto3
import csv
from datetime import datetime, timedelta
from io import StringIO

def fetch_old_elbs():
    # Initialize Boto3 client for ELB
    elb_client = boto3.client('elbv2')

    # Get current time in UTC timezone
    current_time = datetime.utcnow()

    # Fetch all ELBs
    response = elb_client.describe_load_balancers()
    elbs = response['LoadBalancers']

    old_elbs = []

    # Iterate through each ELB
    for elb in elbs:
        elb_name = elb['LoadBalancerName']
        creation_time = elb['CreatedTime'].replace(tzinfo=None)  # Convert to naive datetime

        # Calculate the difference in days
        age_of_elb = (current_time - creation_time).days

        # If the ELB is older than two weeks (14 days), add it to the list
        if age_of_elb >= 0:
            old_elbs.append(elb)

    return old_elbs

def delete_old_elbs(old_elbs):
    # Initialize Boto3 client for ELB
    elb_client = boto3.client('elbv2')

    # Delete old ELBs
    for elb in old_elbs:
        elb_name = elb['LoadBalancerName']
        elb_client.delete_load_balancer(LoadBalancerArn=elb['LoadBalancerArn'])
        print(f"Deleted old ELB: {elb_name}")

def save_to_s3(bucket_name, file_key, csv_data):
    # Initialize Boto3 client for S3
    s3_client = boto3.client('s3')

    # Upload the CSV data to S3
    s3_client.put_object(Body=csv_data.getvalue(), Bucket=bucket_name, Key=file_key)

def lambda_handler(event, context):
    # Fetch old ELBs
    old_elbs = fetch_old_elbs()

    # Print details of old ELBs
    print("Old Elastic Load Balancers:")
    for elb in old_elbs:
        print(elb['LoadBalancerName'])

    # Delete old ELBs
    delete_old_elbs(old_elbs)

    # Prepare CSV data for S3
    csv_data = StringIO()
    csv_writer = csv.writer(csv_data)
    
    # Write old ELB details to CSV
    csv_writer.writerow(['Old ELB Name', 'Creation Time'])
    for elb in old_elbs:
        csv_writer.writerow([elb['LoadBalancerName'], elb['CreatedTime'].strftime("%Y-%m-%d %H:%M:%S")])

    # Reset the StringIO buffer position to the beginning
    csv_data.seek(0)

    # Get current date and time
    current_datetime = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

    # Define S3 bucket and file key for CSV
    bucket_name = 'script07'
    file_key = f'old_elbs_{current_datetime}.csv'

    # Save CSV data to S3
    save_to_s3(bucket_name, file_key, csv_data)

    return {
        'statusCode': 200,
        'body': 'Old ELBs deleted and CSV file saved to S3'
    }
