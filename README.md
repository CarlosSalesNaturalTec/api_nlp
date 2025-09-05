# Documentação do Módulo NLP (Natural Language Processing)

Este documento detalha a arquitetura e o funcionamento do micro-serviço de Análise de Linguagem Natural.

## 1. Detalhes Técnicos

Este serviço é uma API FastAPI que enriquece os dados textuais coletados com análises semânticas, funcionando como o cérebro analítico da plataforma.

- **Framework Principal:** [FastAPI](https://fastapi.tiangolo.com/).
- **Provedor de NLP:** [Google Cloud Natural Language API](https://cloud.google.com/natural-language). O serviço `google_nlp_service.py` encapsula as chamadas a esta API para realizar:
    - Análise de Sentimento.
    - Extração de Entidades.
    - Moderação de Conteúdo.
- **Banco de Dados:** Utiliza o SDK `firebase-admin` para interagir com o **Google Firestore**.
- **Execução Assíncrona:** Todas as tarefas de processamento são executadas em background (`BackgroundTasks`) para garantir que a API responda imediatamente.

## 2. Endpoints e Funcionalidades

### 2.1. Análise de Artigos da Web (Processamento em Lote)

- **Endpoint:** `POST /run-nlp-analysis`
- **Acionamento:** Projetado para ser acionado periodicamente por um **Google Cloud Scheduler** (ex: diariamente às 23:00hs).
- **Fluxo:**
    1. Busca por documentos na coleção `monitor_results` com `status: 'scraper_ok'`.
    2. Para cada documento, extrai o conteúdo textual (`scraped_content`).
    3. Envia o texto para a Google NLP API para análise.
    4. Atualiza o documento original no Firestore com os resultados da análise no campo `google_nlp_analysis` e altera o `status` para `nlp_ok` (ou `nlp_error` em caso de falha).
    5. Registra um log de execução na coleção `system_logs`.

### 2.2. Análise de Mensagens do WhatsApp (Processamento Orientado a Eventos)

- **Endpoint:** `POST /process/whatsapp-message`
- **Acionamento:** Projetado para ser acionado por uma **Cloud Function** sempre que uma nova mensagem de WhatsApp é salva no Firestore.
- **Payload da Requisição:**
    ```json
    {
      "group_id": "id_do_grupo_no_firestore",
      "message_id": "id_da_mensagem_no_firestore"
    }
    ```
- **Fluxo:**
    1. Recebe os IDs do grupo e da mensagem.
    2. Inicia uma tarefa em background para processar a mensagem específica.
    3. A tarefa busca o documento em `whatsapp_groups/{group_id}/messages/{message_id}`.
    4. Verifica se a mensagem precisa de processamento (`nlp_status: 'pending'`).
    5. Envia o campo `message_text` para a Google NLP API.
    6. Atualiza o documento original no Firestore com os resultados no campo `nlp_analysis` e altera o `nlp_status` para `ok` (ou `error`).

## 3. Instruções de Uso e Implantação

### 3.1. Configuração do Ambiente Local

1.  **Credenciais de Serviço do Firebase:**
    -   Coloque o arquivo JSON da sua Service Account do Firebase dentro da pasta `config/`.

2.  **Variáveis de Ambiente:**
    -   Copie `.env.example` para `.env` e garanta que a variável `GOOGLE_APPLICATION_CREDENTIALS` aponte para o seu arquivo de credenciais.

3.  **Instalação e Execução:**
    ```bash
    # Navegue até a pasta da API
    cd api_nlp

    # Crie e ative um ambiente virtual
    python -m venv venv
    .\venv\Scripts\activate

    # Instale as dependências
    pip install -r requirements.txt

    # Execute o servidor
    uvicorn main:app --reload
    ```
    A API estará disponível em `http://127.0.0.1:8000`.

### 3.2. Implantação (Google Cloud Run)

O serviço é projetado para ser implantado como um contêiner no Google Cloud Run.

```bash
# Substitua [PROJECT_ID]
gcloud builds submit --tag gcr.io/[PROJECT_ID]/api-nlp ./api_nlp

gcloud run deploy api-nlp \
  --image gcr.io/[PROJECT_ID]/api-nlp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```
**Nota de Produção:** A invocação em produção deve ser feita de forma segura, utilizando contas de serviço com as permissões necessárias.

## 4. Modelo de Dados Enriquecido

Após o processamento, o serviço enriquece os documentos originais no Firestore adicionando um novo campo (`google_nlp_analysis` para artigos da web ou `nlp_analysis` para mensagens do WhatsApp). Este campo contém os resultados estruturados da análise de NLP.

A estrutura do objeto adicionado, baseada no schema `GoogleNlpAnalysis`, é a seguinte:

```json
{
  "sentiment": "positivo",
  "entities": [
    "Congresso Nacional",
    "Reforma Tributária"
  ],
  "moderation_results": [
    {
      "category": "Toxic",
      "confidence": 0.21
    }
  ]
}
```

| Campo                | Descrição                                                                                                |
| :------------------- | :------------------------------------------------------------------------------------------------------- |
| `sentiment`          | A classificação do sentimento geral do texto (`positivo`, `negativo` ou `neutro`).                         |
| `entities`           | Uma lista de nomes de entidades (pessoas, organizações, locais, etc.) extraídas do texto.                |
| `moderation_results` | Uma lista de categorias de moderação de conteúdo identificadas, cada uma com seu nível de confiança. |

## 5. Relação com Outros Módulos

-   **Módulo Scraper (Fonte):** O endpoint `/run-nlp-analysis` é o consumidor direto dos resultados do `scraper_newspaper3k`.
-   **Módulo WhatsApp Ingestion (Fonte):** O endpoint `/process/whatsapp-message` é o consumidor dos dados gerados pelo `whatsapp_ingestion_service`.
-   **Módulo Analytics (Destino):** Os dados estruturados gerados aqui (sentimento, entidades, etc.) de todas as fontes são a base para o módulo de **Analytics**.
