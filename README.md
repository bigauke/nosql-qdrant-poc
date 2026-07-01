# 🚀 PoC: Banco de Dados Vetorial com Qdrant na AWS

Projeto desenvolvido para a disciplina de **Repositório de Dados e NoSQL** (Especialização em Engenharia de Dados e Big Data - USP).

## 📌 Objetivo
Desenhar, implementar e validar uma arquitetura de banco de dados NoSQL orientada a **Busca Semântica** para um sistema de Suporte ao Cliente. A solução permite cruzar a "intenção" da frase escrita pelo cliente com regras rígidas de negócios utilizando *Payload Filtering*.

O banco de dados escolhido foi o **Qdrant**, um *Vector Database* de alto desempenho.

---

## 🏗️ 1. Arquitetura e Modelagem de Dados (Qdrant)

Os bancos vetoriais armazenam "embeddings" (arrays numéricos densos). Para suportar as regras de negócios, modelamos o banco com um esquema rico de metadados associado a cada vetor.

**Estrutura do Ponto (Registro):**
*   **ID:** UUID
*   **Vector:** Array de 384 dimensões (Gerado via LLM `all-MiniLM-L6-v2` / `SentenceTransformers`)
*   **Payload (Metadados):**
    *   `ticket_text` (String): Descrição textual completa.
    *   `produto` (String): Categoria (`App Mobile`, `Plataforma Web`, `API`).
    *   `status` (String): Estado atual (`aberto`, `em_andamento`, `resolvido`).
    *   `prioridade` (String): Severidade (`alta`, `media`, `baixa`).
    *   `cliente_id` (String): ID do cliente (para *multi-tenancy*).
    *   `data_criacao` (Int Timestamp): Para filtros de Range temporal.

---

## 🔍 2. Padrões de Acesso (Queries Implementadas)

Os arquivos `populate.py` e `queries.py` demonstram a arquitetura em ação através de 6 cenários (presentes no código):

1.  **Ingestão Massiva (Q1):** Geração de base sintética via *Faker* e inserção no Qdrant.
2.  **Busca Semântica Simples (Q2):** O algoritmo encontra a intenção do cliente independente de palavras-chave.
3.  **Busca Semântica + Filtro Restrito (Q3):** Buscar similaridade filtrando apenas casos de um `produto` específico.
4.  **Busca de Base de Conhecimento (Q4):** Encontrar incidentes parecidos, cruzando apenas com chamados `resolvidos`.
5.  **Filtros Compostos (Q5):** Cruzamento de dados de negócio simultâneos (`prioridade = alta` AND `produto = App Mobile`).
6.  **Filtro Histórico Contextual (Q6):** Restringir a busca a tickets do mesmo `cliente_id` criados nos últimos 30 dias usando `Range(gte=timestamp)`.

---

## ☁️ 3. Deploy na AWS (EC2)

Para simular um ambiente de produção real, a PoC foi implantada em uma máquina **AWS EC2 (`us-east-1`)**.

*   **Setup:** Automatizado via SSH/Paramiko.
*   **Stack:** Python 3, Qdrant Client v1.18, PyTorch (CPU-only para otimização de recursos da EC2 gratuita).
*   **Execução Remota:** Os dados foram populados na nuvem e o log gerado localmente pelo Qdrant.

### Log Final de Execução (Validação)
Abaixo, um trecho da consulta de Histórico Contextual rodando com sucesso no servidor da AWS:

```text
================================================================================
Q6. Histórico Contextual de Cliente (Filtro por Range de Data + Match)
Objetivo: Buscar tickets similares relatados pelo cliente CUST-9999 nos últimos 30 dias.
================================================================================
  -> Score de Similaridade: 0.6189
     Payload: Produto [API] | Status [resolvido] | Prioridade [alta]
     Texto: Problema: Lentidão na API. Descrição: A API de produtos está com lentidão excessiva e retornando timeouts.
--------------------------------------------------------------------------------
Validação da PoC concluída com sucesso!
```

---

## 💻 4. Como Executar (Ambiente Local)

Caso queira rodar o projeto localmente:

1. Instale as dependências:
   ```bash
   pip install qdrant-client sentence-transformers faker torch
   ```
2. Popule o banco:
   ```bash
   python PoC_Qdrant/populate.py
   ```
3. Execute as consultas:
   ```bash
   python PoC_Qdrant/queries.py
   ```
