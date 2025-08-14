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
* Utilizando o @database.py, obter no firestore os textos a serem analisados. A coleção a ser utilizada é a: "scraped_articles". A estrutura dos documentos desta coleção está disponível no arquivo @model_scraped_article.json
* Realizar análises, classificações e extração de entidades, conforme citadas no objetivo, tendo a liberdade de incluir outras não citadas e que sejam relevantes ao processo de Social Listening.
* Armazenar os resultados obtidos em uma coleção do firestore, utilizando @database.py 
* Armazenar log de erros gerados por exception em toda a aplicação, especificando o motivo da falha. utilizando @database.py  na coleção: ‘erros_de_execucao_api_nlp’

Por favor, forneça o código necessário para implementarmos juntos este projeto. 
