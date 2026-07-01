import paramiko
import os

ip = "34.224.40.221"
key_path = "labsuser.pem"

print("Conectando via SSH...")
key = paramiko.RSAKey.from_private_key_file(key_path)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ip, username="ubuntu", pkey=key)

print("Transferindo arquivos via SFTP...")
sftp = client.open_sftp()
sftp.put("PoC_Qdrant/populate.py", "populate.py")
sftp.put("PoC_Qdrant/queries.py", "queries.py")

print("Executando setup e scripts na EC2...")
commands = """
echo localhost > ec2_ip.txt
venv/bin/python populate.py > populate.log 2>&1
venv/bin/python queries.py > queries.log 2>&1
"""

stdin, stdout, stderr = client.exec_command(commands)
exit_status = stdout.channel.recv_exit_status()
print(f"Comandos finalizados. Status: {exit_status}")

print("Baixando logs...")
try:
    sftp.get("setup.log", "PoC_Qdrant/setup.log")
    sftp.get("populate.log", "PoC_Qdrant/populate.log")
    sftp.get("queries.log", "PoC_Qdrant/queries.log")
    print("Logs salvos na pasta PoC_Qdrant/")
except Exception as e:
    print(f"Erro ao baixar logs: {e}")

sftp.close()
client.close()
print("Finalizado!")
