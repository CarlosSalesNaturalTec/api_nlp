# Documentação do Módulo NLP (Natural Language Processing)

Este documento detalha a arquitetura e o funcionamento do micro-serviço de Análise de Linguagem Natural.

## 1. Detalhes Técnicos

Este serviço é uma API FastAPI que enriquece os dados textuais coletados com análises semânticas.

- **Framework Principal:** [FastAPI](https://fastapi.tiangolo.com/).
- **Provedor de NLP:** [Google Cloud Natural Language API](https://cloud.google.com/natural-language). O serviço `google_nlp_service.py` encapsula as chamadas a esta API para realizar:
    - Análise de Sentimento.
    - Extração de Entidades.
    - Moderação de Conteúdo.
- **Banco de Dados:** Utiliza o SDK `firebase-admin` para interagir com o **Google Firestore**.
- **Execução Assíncrona:** Assim como o scraper, o processo de análise de NLP é executado como uma tarefa em background (`BackgroundTasks`) para garantir que a API responda imediatamente.

## 2. Instruções de Uso e Implantação

### 2.1. Configuração do Ambiente Local

1.  **Credenciais de Serviço do Firebase:**
    -   Coloque o arquivo JSON da sua Service Account do Firebase dentro da pasta `config/`.

2.  **Variáveis de Ambiente:**
    -   Copie `.env.example` para `.env` (se aplicável) e garanta que a variável `GOOGLE_APPLICATION_CREDENTIALS` aponte para o seu arquivo de credenciais, seja via `.env` ou configuração do sistema.

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

### 2.2. Implantação (Google Cloud Run)

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
**Nota de Produção:** A invocação em produção deve ser feita de forma segura pelo Google Cloud Scheduler, utilizando uma conta de serviço com as permissões necessárias.

## 3. Relação com Outros Módulos

Este serviço é o segundo "worker" na pipeline de processamento de dados, atuando sobre os resultados do módulo de scraping.

### 3.1. Orquestração (Google Cloud Scheduler)

-   O endpoint `/run-nlp-analysis` é projetado para ser acionado periodicamente por um **Google Cloud Scheduler**, idealmente após a execução do scraper.

### 3.2. Interação com o Firestore

O Firestore serve como a ponte entre os módulos.

-   **`monitor_results` (Leitura e Escrita):**
    -   **Fonte de Dados:** O serviço busca documentos nesta coleção onde o campo `status` é igual a `scraper_ok`.
    -   **Lógica de Processamento:** Para cada documento, ele pega o conteúdo de `scraped_content` e o envia para a Google NLP API.
    -   **Atualização de Status:**
        -   Em caso de sucesso, cria um novo campo no documento chamado `google_nlp_analysis` (contendo os resultados de sentimento, entidades e moderação) e atualiza o `status` para `nlp_ok`.
        -   Em caso de falha, atualiza o `status` para `nlp_error` e registra a mensagem de erro no campo `nlp_error_message`.

-   **`system_logs` (Apenas Escrita):**
    -   Assim como o scraper, ele cria um log de execução no início da tarefa (`status: 'running'`) e o atualiza no final (`status: 'completed'` ou `'failed'`), registrando a quantidade de textos processados.

### 3.3. Módulos Adjacentes

-   **Módulo Scraper (Fonte):** Este serviço é o consumidor direto dos resultados do `scraper_newspaper3k`. Ele só processa os dados que o scraper marcou como `scraper_ok`.
-   **Módulo Analytics (Destino):** Os dados estruturados gerados aqui (sentimento, entidades, etc.) são a base para o módulo de **Analytics**. O frontend e os dashboards consumirão esses dados pré-processados para exibir insights, tendências e alertas.