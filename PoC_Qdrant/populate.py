import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configura Faker para dados locais (pt_BR)
fake = Faker('pt_BR')

# Inicializa o modelo de embeddings (leve e rápido para a PoC)
model = SentenceTransformer('all-MiniLM-L6-v2')

import os
try:
    with open("../ec2_ip.txt", "r") as f:
        host = f.read().strip()
    print(f"Conectando ao Qdrant na AWS (IP: {host})...")
    client = QdrantClient(url=f"http://{host}:6333")
except:
    print("Conectando ao Qdrant local...")
    client = QdrantClient(path="qdrant_db")

collection_name = "support_tickets"

# Recria a coleção caso já exista (para garantir testes limpos)
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)

# Criação do Repositório (Coleção) definindo o tamanho do vetor
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Listas de apoio para dados aleatórios
produtos = ['App Mobile', 'Plataforma Web', 'API']
prioridades = ['baixa', 'media', 'alta']
status_opcoes = ['aberto', 'em_andamento', 'resolvido']

# Cenários de suporte comuns
cenarios = [
    ("Erro ao fazer login no sistema", "O usuário não consegue logar, o sistema retorna erro 500."),
    ("Lentidão na geração de relatórios", "Os relatórios de vendas estão demorando mais de 5 minutos para carregar."),
    ("Pagamento recusado repetidamente", "O cliente tentou usar 3 cartões diferentes e todos foram recusados pelo gateway."),
    ("App fechando sozinho (Crash)", "Ao abrir a tela de configurações, o aplicativo fecha inesperadamente."),
    ("Dúvida sobre integração de API", "O cliente não sabe como gerar o token OAuth2 para acessar a API."),
    ("Bug no cálculo de frete", "O valor do frete está aparecendo como negativo no carrinho de compras."),
    ("Esquecimento de senha", "Usuário relata que o e-mail de redefinição de senha não está chegando na caixa de entrada."),
    ("Falha na sincronização de dados", "Os dados salvos no modo offline não estão subindo para a nuvem quando a internet volta."),
    ("Erro 404 em página de produto", "Ao clicar no produto em destaque, o sistema retorna página não encontrada."),
    ("Problema de layout na tela", "Os botões estão sobrepostos dificultando o clique em dispositivos de tela pequena.")
]

num_tickets = 25
tickets = []

for _ in range(num_tickets):
    cenario = random.choice(cenarios)
    ticket_text = f"Problema: {cenario[0]}. Descrição: {cenario[1]}"
    
    ticket = {
        "id": str(uuid.uuid4()),
        "ticket_text": ticket_text,
        "status": random.choice(status_opcoes),
        "produto": random.choice(produtos),
        "prioridade": random.choice(prioridades),
        "cliente_id": f"CUST-{random.randint(1000, 1050)}",
        "data_criacao": int((datetime.now() - timedelta(days=random.randint(0, 60))).timestamp())
    }
    tickets.append(ticket)

# Adiciona registros controlados para testarmos a Query 6 corretamente
special_client = "CUST-9999"
tickets.append({
    "id": str(uuid.uuid4()),
    "ticket_text": "Problema: Lentidão na API. Descrição: A API de produtos está com lentidão excessiva e retornando timeouts.",
    "status": "resolvido",
    "produto": "API",
    "prioridade": "alta",
    "cliente_id": special_client,
    "data_criacao": int((datetime.now() - timedelta(days=5)).timestamp())
})
tickets.append({
    "id": str(uuid.uuid4()),
    "ticket_text": "Problema: Dúvida sobre integração de API. Descrição: Cliente pedindo ajuda com fluxo OAuth2.",
    "status": "em_andamento",
    "produto": "API",
    "prioridade": "media",
    "cliente_id": special_client,
    "data_criacao": int((datetime.now() - timedelta(days=10)).timestamp())
})

print(f"Gerando embeddings e populando o Qdrant com {len(tickets)} tickets...")

# Prepara os pontos para a Q1 (Inserção/Update)
points = []
for t in tickets:
    # Gera o embedding usando a string do problema
    vector = model.encode(t['ticket_text']).tolist()
    
    point = PointStruct(
        id=t['id'],
        vector=vector,
        payload={
            "ticket_text": t['ticket_text'],
            "status": t['status'],
            "produto": t['produto'],
            "prioridade": t['prioridade'],
            "cliente_id": t['cliente_id'],
            "data_criacao": t['data_criacao']
        }
    )
    points.append(point)

# Executa Q1. Inserção
client.upsert(
    collection_name=collection_name,
    points=points
)

print("✅ Dados inseridos com sucesso!")
print(f"Total de tickets persistidos na coleção '{collection_name}': {client.count(collection_name).count}")
