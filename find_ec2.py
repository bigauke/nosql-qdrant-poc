import boto3
import os

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    region_name="us-east-1"
)

ec2 = session.client('ec2')
response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])

instances = []
for r in response.get('Reservations', []):
    for i in r.get('Instances', []):
        instances.append(i)

if instances:
    inst = instances[0]
    print(f"IP: {inst.get('PublicIpAddress')}")
    print(f"InstanceId: {inst.get('InstanceId')}")
    sg = inst.get('SecurityGroups', [{}])[0].get('GroupId')
    print(f"SecurityGroup: {sg}")
    
    # Try to open port 6333 and 22 if not open
    if sg:
        try:
            ec2.authorize_security_group_ingress(
                GroupId=sg,
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 6333,
                        'ToPort': 6333,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]
            )
            print("Porta 6333 e 22 liberadas no SG.")
        except Exception as e:
            print(f"Erro ao liberar porta ou ja estava liberada: {e}")
else:
    print("Nenhuma instancia rodando em us-east-1.")
