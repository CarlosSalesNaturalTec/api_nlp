# api_nlp

* Nome da aplicação: api_nlp
* Linguagem: Python+ FastAPI 
* Ambiente de desenvolvimento: Windows
* Ambiente de produção: Google Cloud Run

## Objetivo da aplicação:  
Processar textos utilizando técnicas de  NLP e retornar análises automatizadas como:

* Classificação de tipo de menção: reclamação, elogio, notícia, review, dúvida, crítica,  palavras ofensivas, etc.
* Classificação de sentimento : positivo, neutro, negativo.
* Identificação de perfil de autores: influenciadores, detratores 
* Detecção de intenções
* Detecção de Entidades: pessoas, marcas, locais.

## Instruções Detalhadas:
* Utilizando o arquivo @database.py, obter no firestore os textos a serem analisados. A coleção a ser utilizada é a: "scraped_articles". A estrutura dos documentos desta coleção está disponível no arquivo @models/model_scraped_article.json
* Realizar análises, classificações e extração de entidades, conforme citadas no objetivo, tendo a liberdade de incluir outras não citadas e que sejam relevantes ao processo de Social Listening.
* Armazenar os resultados obtidos em uma coleção do firestore, utilizando @database.py 
* Armazenar log de erros gerados por exception em toda a aplicação, especificando o motivo da falha. utilizando @database.py  na coleção: "erros_de_execucao_api_nlp"

Por favor, forneça o código necessário para implementarmos juntos este projeto. 

## Estrutura Detalhada da Aplicação

Esta seção detalha a arquitetura e os componentes principais da `api_nlp`.

### Arquivos Principais

-   `main.py`: Ponto de entrada da aplicação FastAPI. É responsável por inicializar a API e definir os endpoints que orquestram o processo de análise de NLP.
-   `database.py`: Contém a lógica para estabelecer e gerenciar a conexão com o banco de dados Firestore. Expõe a função `get_db()` para ser usada em outras partes da aplicação.
-   `models/schemas.py`: Arquivo central que define os esquemas de dados da aplicação utilizando Pydantic. Garante a validação, tipagem e estrutura dos objetos manipulados pela API.
-   `Dockerfile`: Define as instruções para a construção da imagem Docker da aplicação, permitindo o empacotamento de todas as dependências para um deploy consistente na nuvem
-   `requirements.txt`: Lista todas as bibliotecas Python necessárias para a execução do projeto.

### Modelos de Dados (`models/schemas.py`)

A aplicação utiliza os seguintes modelos Pydantic para estruturar os dados:

-   **`ScrapedArticle`**: Representa a estrutura de um artigo ou texto extraído para análise.
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

-   **`NlpAnalysis`**: Armazena os resultados gerados pelo processamento de NLP.
    -   `mention_type`: `str` - Classificação do tipo de menção (ex: reclamação, elogio).
    -   `sentiment`: `str` - Sentimento geral do texto (ex: positivo, negativo, neutro).
    -   `author_profile`: `str` - Perfil identificado do autor (ex: influenciador, detrator).
    -   `intentions`: `List[str]` - Lista de intenções detectadas no texto.
    -   `entities`: `List[str]` - Lista de entidades nomeadas (pessoas, marcas, etc.).

-   **`AnalysisResult`**: Modelo que agrega o artigo original e sua respectiva análise, representando o documento final a ser salvo no Firestore.
    -   `article`: `ScrapedArticle` - O objeto do artigo original.
    -   `nlp_analysis`: `NlpAnalysis` - O objeto com os resultados da análise.
    -   `processed_at`: `datetime` - Data e hora em que a análise foi concluída.

-   **`ErrorLog`**: Define a estrutura para os logs de erro.
    -   `error_message`: `str` - A mensagem de erro capturada.
    -   `timestamp`: `datetime` - Data e hora em que o erro ocorreu.
    -   `details`: `Optional[str]` - Detalhes adicionais ou stack trace do erro.