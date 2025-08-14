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
* Utilizando o arquivo `database.py`, a aplicação obtém do Firestore os textos a serem analisados. A coleção utilizada é a: "scraped_articles", buscando por documentos com `status` igual a `pending` para um `owner` específico.
* As análises de NLP são realizadas pelo serviço `google_nlp_service.py`, que utiliza a API da Google.
* Os resultados são armazenados na coleção "nlp_analysis_results" no Firestore.
* Logs de erro gerados por exceções são armazenados na coleção "erros_de_execucao_api_nlp".

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

-   **`ScrapedArticle`**: Representa a estrutura de um artigo ou texto extraído para análise.
    -   `id`: `str` - ID do documento no Firestore.
    -   `title`: `str` - Título do artigo.
    -   `url`: `str` - URL de origem do artigo.
    -   `authors`: `List[str]` - Lista de autores.
    -   `text`: `str` - Conteúdo textual completo do artigo.
    -   `scraped_by`: `str` - Ferramenta ou processo que realizou a extração.
    -   `top_image`: `Optional[str]` - URL da imagem principal do artigo.
    -   `scraped_at`: `datetime` - Data e hora da extração.
    -   `domain`: `str` - Domínio do site de origem.
    -   `publish_date`: `Optional[datetime]` - Data de publicação do artigo.
    -   `owner`: `str` - Cliente ou entidade responsável pela análise do artigo.
    -   `status`: `str` - Status do processamento do artigo (ex: 'pending', 'processed').

-   **`ModerationResult`**: Armazena o resultado da análise de moderação de conteúdo.
    -   `category`: `str` - Categoria da moderação (ex: 'Toxic', 'Derogatory').
    -   `confidence`: `float` - Nível de confiança da classificação.

-   **`GoogleNlpAnalysis`**: Armazena os resultados gerados pelo processamento de NLP do Google.
    -   `sentiment`: `str` - Sentimento geral do texto (positivo, negativo, neutro).
    -   `entities`: `List[str]` - Lista de entidades nomeadas.
    -   `moderation_results`: `List[ModerationResult]` - Lista com os resultados da moderação.

-   **`AnalysisResult`**: Modelo que agrega o artigo original e sua respectiva análise, representando o documento final a ser salvo no Firestore.
    -   `article`: `ScrapedArticle` - O objeto do artigo original.
    -   `google_nlp_analysis`: `GoogleNlpAnalysis` - O objeto com os resultados da análise do Google.
    -   `processed_at`: `datetime` - Data e hora em que a análise foi concluída.

-   **`ErrorLog`**: Define a estrutura para os logs de erro.
    -   `error_message`: `str` - A mensagem de erro capturada.
    -   `timestamp`: `datetime` - Data e hora em que o erro ocorreu.
    -   `details`: `Optional[str]` - Detalhes adicionais ou stack trace do erro.