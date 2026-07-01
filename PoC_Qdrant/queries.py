from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta

print("Carregando modelo e conectando ao banco de dados...")
import os
try:
    with open("../ec2_ip.txt", "r") as f:
        host = f.read().strip()
    client = QdrantClient(url=f"http://{host}:6333")
except:
    client = QdrantClient(path="qdrant_db")
model = SentenceTransformer('all-MiniLM-L6-v2')
collection_name = "support_tickets"

def format_result(hits):
    if not hits:
        print("  -> Nenhum resultado encontrado com os filtros informados.")
    for hit in hits:
        print(f"  -> Score de Similaridade: {hit.score:.4f}")
        print(f"     Payload: Produto [{hit.payload['produto']}] | Status [{hit.payload['status']}] | Prioridade [{hit.payload['prioridade']}]")
        print(f"     Texto: {hit.payload['ticket_text']}")
    print("-" * 80)

# ---------------------------------------------------------
# Simulação de um NOVO TICKET chegando no suporte
# ---------------------------------------------------------
novo_problema = "O sistema de relatórios está muito lento hoje, os dados não aparecem."
print(f"\n[NOVO TICKET RECEBIDO]: '{novo_problema}'")
query_vector = model.encode(novo_problema).tolist()

print("\n" + "="*80)
print("Q2. Busca Semântica Simples (Encontrar tickets com sentido similar)")
print("Objetivo: O atendente quer ver se já houve algo parecido independente do produto.")
print("="*80)
hits = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    limit=3
).points
format_result(hits)


print("\n" + "="*80)
print("Q3. Busca Semântica com Filtro Restrito (Must)")
print("Objetivo: O atendente sabe que o problema é na 'Plataforma Web' e quer filtrar.")
print("="*80)
hits = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(key="produto", match=MatchValue(value="Plataforma Web"))
        ]
    ),
    limit=3
).points
format_result(hits)


print("\n" + "="*80)
print("Q4. Busca de Soluções (Apenas tickets 'resolvidos')")
print("Objetivo: Encontrar apenas incidentes que já possuem solução.")
print("="*80)
hits = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(key="status", match=MatchValue(value="resolvido"))
        ]
    ),
    limit=3
).points
format_result(hits)


print("\n" + "="*80)
print("Q5. Busca Semântica com Filtro Composto (Alta Prioridade E App Mobile)")
print("Objetivo: Cruzar múltiplos metadados para afunilar o escopo.")
print("="*80)
hits = client.query_points(
    collection_name=collection_name,
    query=query_vector,
    query_filter=Filter(
        must=[
            FieldCondition(key="prioridade", match=MatchValue(value="alta")),
            FieldCondition(key="produto", match=MatchValue(value="App Mobile"))
        ]
    ),
    limit=3
).points
format_result(hits)


print("\n" + "="*80)
print("Q6. Histórico Contextual de Cliente (Filtro por Range de Data + Match)")
print("Objetivo: Buscar tickets similares relatados pelo cliente CUST-9999 nos últimos 30 dias.")
print("="*80)
# Usamos uma string específica para demonstrar melhor o filtro neste cliente
q6_texto = "Problemas de timeout na API"
q6_vector = model.encode(q6_texto).tolist()

trinta_dias_atras = int((datetime.now() - timedelta(days=30)).timestamp())

hits = client.query_points(
    collection_name=collection_name,
    query=q6_vector,
    query_filter=Filter(
        must=[
            FieldCondition(key="cliente_id", match=MatchValue(value="CUST-9999")),
            FieldCondition(key="data_criacao", range=Range(gte=trinta_dias_atras))
        ]
    ),
    limit=3
).points
format_result(hits)

print("\nValidação da PoC concluída com sucesso!")
