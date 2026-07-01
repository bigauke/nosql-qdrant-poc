$IP = "34.224.40.221"

Write-Host "Aguardando SSH ficar online..."
Start-Sleep -Seconds 10

Write-Host "Copiando scripts para EC2..."
scp -i labsuser.pem -o StrictHostKeyChecking=no .\PoC_Qdrant\populate.py .\PoC_Qdrant\queries.py ubuntu@${IP}:~

Write-Host "Executando setup e scripts remotamente na EC2..."
ssh -i labsuser.pem -o StrictHostKeyChecking=no ubuntu@$IP "
    sudo apt update
    sudo apt install -y python3-pip python3-venv
    python3 -m venv venv
    source venv/bin/activate
    pip install qdrant-client sentence-transformers faker
    echo localhost > ec2_ip.txt
    
    echo '>>> Rodando populate.py...'
    python populate.py > populate.log 2>&1
    
    echo '>>> Rodando queries.py...'
    python queries.py > queries.log 2>&1
"

Write-Host "Baixando logs de execução..."
scp -i labsuser.pem -o StrictHostKeyChecking=no ubuntu@${IP}:~/populate.log .\PoC_Qdrant\
scp -i labsuser.pem -o StrictHostKeyChecking=no ubuntu@${IP}:~/queries.log .\PoC_Qdrant\

Write-Host "Pronto!"
