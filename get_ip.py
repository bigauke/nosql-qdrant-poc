import boto3
import os

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    region_name="us-east-1"
)

ec2 = session.client('ec2')
response = ec2.describe_instances(Filters=[
    {'Name': 'instance-state-name', 'Values': ['running']},
    {'Name': 'tag:Name', 'Values': ['Qdrant-PoC']}
])

for r in response.get('Reservations', []):
    for i in r.get('Instances', []):
        ip = i.get('PublicIpAddress')
        if ip:
            with open("ec2_ip.txt", "w") as f:
                f.write(ip)
            print(f"IP Salvo: {ip}")
            exit(0)
