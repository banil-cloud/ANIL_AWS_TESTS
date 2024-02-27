import boto3

# Define a list of AWS regions
aws_regions = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'eu-west-1', 'eu-west-2', 'eu-central-1', 'ap-northeast-1', 'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1', 'sa-east-1']

# Iterate over each region
for region in aws_regions:
    print(f"Fetching load balancers in {region}...")
    
    # Initialize the Boto3 client for the Elastic Load Balancing service in the current region
    elb_client = boto3.client('elbv2', region_name=region)
    
    # List all load balancers in the current region
    response = elb_client.describe_load_balancers()
    
    # Extract load balancer information from the response
    load_balancers = response['LoadBalancers']
    
    # Print load balancer information
    for lb in load_balancers:
        print("Load Balancer Name:", lb['LoadBalancerName'])
        
        # Check if 'DNSName' key exists before accessing it
        if 'DNSName' in lb:
            print("DNS Name:", lb['DNSName'])
        else:
            print("DNS Name: Not found")  # Print a message if 'DNSName' key is not present
        
        print("Load Balancer ARN:", lb['LoadBalancerArn'])
        print("Load Balancer Type:", lb['Type'])
        print("VPC ID:", lb['VpcId'])
        print("Availability Zones:", lb['AvailabilityZones'])
        
        # Check if 'SecurityGroups' key exists before accessing it
        if 'SecurityGroups' in lb:
            print("Security Groups:", lb['SecurityGroups'])
        else:
            print("Security Groups: Not found")  # Print a message if 'SecurityGroups' key is not present
        
        # Check if 'Subnets' key exists before accessing it
        if 'Subnets' in lb:
            print("Subnets:", lb['Subnets'])
        else:
            print("Subnets: Not found")  # Print a message if 'Subnets' key is not present
        
        # Check if 'State' key exists before accessing it
        if 'State' in lb:
            print("State:", lb['State'])
        else:
            print("State: Not found")  # Print a message if 'State' key is not present
        
        # Check if 'Scheme' key exists before accessing it
        if 'Scheme' in lb:
            print("Scheme:", lb['Scheme'])
        else:
            print("Scheme: Not found")  # Print a message if 'Scheme' key is not present
        
        print("---------------------------------------------")
