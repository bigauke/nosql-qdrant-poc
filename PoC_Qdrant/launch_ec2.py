import boto3
import os
import time

session = boto3.Session(
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.environ.get("AWS_SESSION_TOKEN"),
    region_name="us-east-1"
)

ec2 = session.client('ec2')
ec2_resource = session.resource('ec2')

print("Procurando VPC default...")
vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])['Vpcs']
vpc_id = vpcs[0]['VpcId']

sg_name = 'Qdrant-SG'
print(f"Criando Security Group {sg_name} na VPC {vpc_id}...")
try:
    sg = ec2.create_security_group(
        GroupName=sg_name,
        Description='SG for Qdrant PoC',
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']
    print(f"SG criado: {sg_id}")
    
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 6333, 'ToPort': 6333, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
    )
except Exception as e:
    print(f"SG já existe ou erro: {e}")
    # Busca o SG existente
    sgs = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
    sg_id = sgs['SecurityGroups'][0]['GroupId']

print("Buscando AMI do Ubuntu 24.04 LTS...")
response = ec2.describe_images(
    Filters=[
        {'Name': 'name', 'Values': ['ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*']},
        {'Name': 'state', 'Values': ['available']}
    ],
    Owners=['099720109477'] # Canonical
)
# Ordena por data de criação para pegar a mais recente
amis = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
ami_id = amis[0]['ImageId']
print(f"AMI encontrada: {ami_id}")

user_data = '''#!/bin/bash
apt-get update -y
apt-get install -y docker.io
systemctl start docker
systemctl enable docker
docker run -d -p 6333:6333 -p 6334:6334 --name qdrant qdrant/qdrant
'''

print("Criando instância EC2...")
instances = ec2_resource.create_instances(
    ImageId=ami_id,
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.micro',
    KeyName='vockey',
    SecurityGroupIds=[sg_id],
    UserData=user_data,
    TagSpecifications=[{
        'ResourceType': 'instance',
        'Tags': [{'Key': 'Name', 'Value': 'Qdrant-PoC'}]
    }]
)

inst = instances[0]
print(f"Instância criada: {inst.id}. Aguardando inicialização (pode levar alguns segundos)...")
inst.wait_until_running()
inst.reload()

print(f"==================================================")
print(f"✅ EC2 Inicializada!")
print(f"IP Público: {inst.public_ip_address}")
print(f"Lembre-se que o Docker com Qdrant pode levar mais ~2 minutos para inicializar internamente via UserData.")
print(f"Você pode monitorar acessando: http://{inst.public_ip_address}:6333")
print(f"==================================================")

# Gravar o IP num arquivo pra gente ler no powershell
with open("ec2_ip.txt", "w") as f:
    f.write(inst.public_ip_address)
