# api_nlp

* Nome da aplicação: api_nlp
* Linguagem: Python+ FastAPI 
* Ambiente de desenvolvimento: Windows
* Ambiente de produção: Google Cloud Run

## Objetivo da aplicação:  
Processar textos utilizando a API Google Cloud Natural Language e retornar análises automatizadas como:

* Classificação de sentimento : positivo, neutro, negativo.
* Detecção de Entidades: pessoas, marcas, locais.
* Moderação de conteúdo: identificação de conteúdo sensível ou impróprio.

## Instruções Detalhadas:
* A aplicação expõe um endpoint `/run-nlp-analysis` que é acionado pelo Google Cloud Scheduler.
* Ao ser acionado, o endpoint inicia uma tarefa em segundo plano que busca por documentos na coleção `monitor_results` do Firestore com `status` igual a `scraper_ok`.
* As análises de NLP são realizadas pelo serviço `google_nlp_service.py`, que utiliza a API da Google para extrair sentimento, entidades e resultados de moderação.
* Os resultados são salvos no mesmo documento na coleção `monitor_results`, e o `status` do documento é atualizado para `nlp_ok`.
* O log de cada execução é armazenado na coleção `system_logs`.

## Estrutura Detalhada da Aplicação

Esta seção detalha a arquitetura e os componentes principais da `api_nlp`.

### Arquivos Principais

-   `main.py`: Ponto de entrada da aplicação FastAPI. É responsável por inicializar a API e definir o endpoint que orquestra o processo de análise de NLP.
-   `google_nlp_service.py`: Módulo que encapsula a lógica de interação com a API Google Cloud Natural Language, realizando a análise de sentimento, extração de entidades e moderação de conteúdo.
-   `database.py`: Contém a lógica para estabelecer e gerenciar a conexão com o banco de dados Firestore.
-   `models/schemas.py`: Arquivo central que define os esquemas de dados da aplicação utilizando Pydantic.
-   `Dockerfile`: Define as instruções para a construção da imagem Docker da aplicação.
-   `requirements.txt`: Lista todas as bibliotecas Python necessárias para o projeto.

### Modelos de Dados (`models/schemas.py`)

A aplicação utiliza os seguintes modelos Pydantic para estruturar os dados:

-   **`ModerationResult`**: Armazena o resultado da análise de moderação de conteúdo.
    -   `category`: `str` - Categoria da moderação (ex: 'Toxic', 'Derogatory').
    -   `confidence`: `float` - Nível de confiança da classificação.

-   **`GoogleNlpAnalysis`**: Armazena os resultados gerados pelo processamento de NLP do Google.
    -   `sentiment`: `str` - Sentimento geral do texto (positivo, negativo, neutro).
    -   `entities`: `List[str]` - Lista de entidades nomeadas.
    -   `moderation_results`: `List[ModerationResult]` - Lista com os resultados da moderação.

-   **`SystemLog`**: Define a estrutura para os logs de execução.
    -   `task`: `str` - Nome da tarefa executada.
    -   `start_time`: `datetime` - Data e hora de início da tarefa.
    -   `end_time`: `Optional[datetime]` - Data e hora de término da tarefa.
    -   `status`: `str` - Status da tarefa (ex: 'running', 'completed', 'failed').
    -   `processed_count`: `int` - Número de itens processados.
    -   `error_message`: `Optional[str]` - Mensagem de erro, caso ocorra.
