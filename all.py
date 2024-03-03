import boto3
import csv
from datetime import datetime

# Initialize the Boto3 clients for EC2, Lambda, ELB, VPC, S3, RDS, EFS, ECS, CloudTrail, and Route 53 services
ec2_client = boto3.client('ec2')
lambda_client = boto3.client('lambda')
elb_client = boto3.client('elbv2')
s3_client = boto3.client('s3')
rds_client = boto3.client('rds')
efs_client = boto3.client('efs')
ecs_client = boto3.client('ecs')
cloudtrail_client = boto3.client('cloudtrail')
route53_client = boto3.client('route53')
waf_client = boto3.client('wafv2')

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
            creation_time_str = "N/A"
            if 'CreateTime' in vpc:
                creation_time_str = vpc['CreateTime'].strftime('%Y-%m-%d %H:%M:%S')
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

    # Fetch and write RDS information
    for region in aws_regions:
        print(f"Fetching RDS instances in {region}...")

        # Initialize the Boto3 client for the RDS service in the current region
        rds_client = boto3.client('rds', region_name=region)
    
        # List all RDS instances in the current region
        response = rds_client.describe_db_instances()
    
        # Extract RDS instance information from the response
        db_instances = response['DBInstances']
        
        for db_instance in db_instances:
            creation_time = db_instance['InstanceCreateTime'].strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'Resource Type': 'RDS Instance',
                'Region': region,
                'Resource Name': db_instance['DBInstanceIdentifier'],
                'Resource ARN': db_instance['DBInstanceArn'],
                'Creation/Last Modified Time': creation_time,
                'Other Information': f"Engine: {db_instance['Engine']}, Status: {db_instance['DBInstanceStatus']}"
            }
            writer.writerow(row)
    
    # Fetch and write EFS information
    for region in aws_regions:
        print(f"Fetching EFS file systems in {region}...")

        # Initialize the Boto3 client for the EFS service in the current region
        efs_client = boto3.client('efs', region_name=region)

        # List all EFS file systems in the current region
        response = efs_client.describe_file_systems()

        # Extract EFS file system information from the response
        file_systems = response['FileSystems']

        for file_system in file_systems:
            creation_time = file_system['CreationTime'].strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'Resource Type': 'EFS File System',
                'Region': region,
                'Resource Name': file_system['Name'],
                'Resource ARN': file_system['FileSystemArn'],
                'Creation/Last Modified Time': creation_time,
                'Other Information': f"Performance Mode: {file_system['PerformanceMode']}, Throughput Mode: {file_system['ThroughputMode']}, LifeCycle State: {file_system['LifeCycleState']}"
            }
            writer.writerow(row)

    # Fetch and write SQS information
    for region in aws_regions:
        print(f"Fetching SQS queues in {region}...")
        # Initialize the Boto3 client for the SQS service in the current region
        sqs_client = boto3.client('sqs', region_name=region)
        # List all SQS queues in the current region
        response = sqs_client.list_queues()
        # Extract SQS queue information from the response
        queues = response.get('QueueUrls', [])
        for queue_url in queues:
            queue_name = queue_url.split('/')[-1]
            # Fetch additional details for the SQS queue
            queue_attributes = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['All']
            )['Attributes']
            arn = queue_attributes.get('QueueArn', '')
            created_timestamp = int(queue_attributes.get('CreatedTimestamp', 0)) / 1000  # Convert milliseconds to seconds
            creation_time = datetime.utcfromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            last_updated_timestamp = int(queue_attributes.get('LastModifiedTimestamp', 0)) / 1000  # Convert milliseconds to seconds
            last_updated = datetime.utcfromtimestamp(last_updated_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            message_retention_period = queue_attributes.get('MessageRetentionPeriod', '')
            visibility_timeout = queue_attributes.get('VisibilityTimeout', '')
            max_message_size = queue_attributes.get('MaximumMessageSize', '')
            delay_seconds = queue_attributes.get('DelaySeconds', '')
            redrive_policy = queue_attributes.get('RedrivePolicy', '')
            row = {
                'Resource Type': 'SQS Queue',
                'Region': region,
                'Resource Name': queue_name,
                'Resource ARN': arn,
                'Creation/Last Modified Time': creation_time,
                'Other Information': f"Last Updated: {last_updated}, Message Retention Period: {message_retention_period} seconds, Visibility Timeout: {visibility_timeout} seconds, Maximum Message Size: {max_message_size} bytes, Delay Seconds: {delay_seconds} seconds, Redrive Policy: {redrive_policy}"
            }
            writer.writerow(row)

    # Fetch and write ECR repositories information
    for region in aws_regions:
        print(f"Fetching ECR repositories in {region}...")
        # Initialize the Boto3 client for the ECR service in the current region
        ecr_client = boto3.client('ecr', region_name=region)
        # List all ECR repositories in the current region
        response = ecr_client.describe_repositories()
        # Extract ECR repository information from the response
        repositories = response.get('repositories', [])
        for repository in repositories:
            repository_name = repository.get('repositoryName', '')
            repository_arn = repository.get('repositoryArn', '')
            creation_time = repository.get('createdAt', '')
            creation_time_str = datetime.strftime(creation_time, '%Y-%m-%d %H:%M:%S')
            row = {
                'Resource Type': 'ECR Repository',
                'Region': region,
                'Resource Name': repository_name,
                'Resource ARN': repository_arn,
                'Creation/Last Modified Time': creation_time_str,
                'Other Information': ''
            }
            writer.writerow(row)

    # Fetch and write ECS information
    for region in aws_regions:
        print(f"Fetching ECS clusters in {region}...")
        # Initialize the Boto3 client for the ECS service in the current region
        ecs_client = boto3.client('ecs', region_name=region)
        # List all ECS clusters in the current region
        response = ecs_client.list_clusters()
        # Extract ECS cluster information from the response
        clusters = response['clusterArns']

        for cluster in clusters:
            cluster_name = cluster.split('/')[-1]  # Extract cluster name from ARN
            row = {
                'Resource Type': 'ECS Cluster',
                'Region': region,
                'Resource Name': cluster_name,
                'Resource ARN': cluster,
                'Creation/Last Modified Time': '',  # ECS clusters do not have a creation time
                'Other Information': ''
            }
            writer.writerow(row)

    # Fetch and write Route 53 information
    print("Fetching Route 53 hosted zones...")
    response = route53_client.list_hosted_zones()

    # Extract Route 53 hosted zone information from the response
    hosted_zones = response['HostedZones']

    for hosted_zone in hosted_zones:
        row = {
            'Resource Type': 'Route 53 Hosted Zone',
            'Region': 'Global',  # Route 53 is a global service
            'Resource Name': hosted_zone['Name'],
            'Resource ARN': hosted_zone['Id'],
            'Creation/Last Modified Time': '',  # No creation date available
            'Other Information': f"Zone ID: {hosted_zone['Id']}, Record Set Count: {hosted_zone['ResourceRecordSetCount']}"
        }
        writer.writerow(row)

    # Fetch and write CloudWatch alarms information
    for region in aws_regions:
        print(f"Fetching CloudWatch alarms in {region}...")
        
        # Initialize the Boto3 client for the CloudWatch service in the current region
        cloudwatch_client = boto3.client('cloudwatch', region_name=region)
        
        # List all CloudWatch alarms in the current region
        response = cloudwatch_client.describe_alarms()
        
        # Extract CloudWatch alarm information from the response
        alarms = response['MetricAlarms']
        for alarm in alarms:
            row = {
                'Resource Type': 'CloudWatch Alarm',
                'Region': region,
                'Resource Name': alarm['AlarmName'],
                'Resource ARN': '',
                'Creation/Last Modified Time': alarm.get('StateUpdatedTimestamp', ''),
                'Other Information': f"Alarm Description: {alarm.get('AlarmDescription', 'N/A')}, Alarm State: {alarm['StateValue']}, Alarm Actions Enabled: {alarm['ActionsEnabled']}, Metric Name: {alarm['MetricName']}, Namespace: {alarm['Namespace']}, Comparison Operator: {alarm['ComparisonOperator']}, Threshold: {alarm['Threshold']}, Evaluation Periods: {alarm['EvaluationPeriods']}, Period: {alarm['Period']}, Dimensions: {alarm.get('Dimensions', 'N/A')}, OK Actions: {alarm.get('OKActions', 'N/A')}, Alarm Actions: {alarm.get('AlarmActions', 'N/A')}, Insufficient Data Actions: {alarm.get('InsufficientDataActions', 'N/A')}"
            }
            writer.writerow(row)
    # Fetch and write DocumentDB clusters information
    for region in aws_regions:
        print(f"Fetching DocumentDB clusters in {region}...")
        # Initialize the Boto3 client for the DocumentDB service in the current region
        docdb_client = boto3.client('docdb', region_name=region)
        # List all DocumentDB clusters in the current region
        response = docdb_client.describe_db_clusters()
        # Extract DocumentDB cluster information from the response
        clusters = response['DBClusters']

        for cluster in clusters:
            creation_time = cluster['ClusterCreateTime'].strftime('%Y-%m-%d %H:%M:%S')
            row = {
                'Resource Type': 'DocumentDB Cluster',
                'Region': region,
                'Resource Name': cluster['DBClusterIdentifier'],
                'Resource ARN': cluster['DBClusterArn'],
                'Creation/Last Modified Time': '',
                'Other Information': f"Engine: {cluster['Engine']}, Status: {cluster['Status']}, Endpoint: {cluster['Endpoint']}"
            }
            writer.writerow(row)

    # Fetch and write AWS Config rules information
    for region in aws_regions:
        print(f"Fetching AWS Config rules in {region}...")

        # Initialize the Boto3 client for the AWS Config service in the current region
        config_client = boto3.client('config', region_name=region)

        # List all AWS Config rules in the current region
        response = config_client.describe_config_rules()

        # Extract AWS Config rules information from the response
        rules = response['ConfigRules']

        for rule in rules:
            row = {
                'Resource Type': 'AWS Config Rule',
                'Region': region,
                'Resource Name': rule['ConfigRuleName'],
                'Resource ARN': rule['ConfigRuleArn'],
                'Creation/Last Modified Time': '',
                'Other Information': f"Description: {rule.get('Description', 'N/A')}, Source: {rule['Source']['Owner']}, Rule Identifier: {rule['Source']['SourceIdentifier']}"
            }
            writer.writerow(row)

    # Fetch and write WAF WebACLs information
    print(f"Fetching WAF WebACLs...")
    # List all WAF WebACLs
    response = waf_client.list_web_acls(Scope='REGIONAL')
    # Extract WAF WebACLs information from the response
    webacls = response.get('WebACLs', [])

    for webacl in webacls:
        row = {
            'Resource Type': 'WAF WebACL',
            'Region': 'Global',
            'Resource Name': webacl['Name'],
            'Resource ARN': webacl['ARN'],
            'Creation/Last Modified Time': '',
            'Other Information': f"" 
        }
        writer.writerow(row) 