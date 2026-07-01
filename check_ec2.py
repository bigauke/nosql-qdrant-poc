import paramiko
import os

ip = "34.224.40.221"
key_path = "labsuser.pem"

print(f"Conectando na AWS ({ip}) para verificação...")
key = paramiko.RSAKey.from_private_key_file(key_path)
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ip, username="ubuntu", pkey=key)

commands = [
    "echo '======================================'",
    "echo 'ARQUIVOS NO DIRETORIO DO SERVIDOR:'",
    "echo '======================================'",
    "ls -la",
    "echo '\\n======================================'",
    "echo 'STATUS DO QDRANT NO DOCKER:'",
    "echo '======================================'",
    "docker ps",
    "echo '\\n======================================'",
    "echo 'LOG DA EXECUCAO DAS QUERIES:'",
    "echo '======================================'",
    "cat PoC_Qdrant/queries.log"
]

for cmd in commands:
    stdin, stdout, stderr = client.exec_command(cmd)
    output = stdout.read().decode('utf-8').strip()
    if output:
        print(output)
    err = stderr.read().decode('utf-8').strip()
    if err:
        print(f"Erro: {err}")

client.close()
print("\nVerificação concluída!")
