from fastapi import FastAPI, HTTPException
from typing import List
import traceback

from database import get_db
from models.schemas import ScrapedArticle, ErrorLog

app = FastAPI(
    title="API NLP",
    description="API para processamento de linguagem natural de artigos.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API NLP!"}

@app.post("/process-articles/", response_model=List[ScrapedArticle])
def process_articles():
    """
    Busca artigos da coleção 'scraped_articles' no Firestore,
    realiza o processamento de NLP e armazena os resultados.
    """
    db = get_db()
    articles_ref = db.collection('scraped_articles')
    
    try:
        articles_snapshot = articles_ref.stream()
        articles = [ScrapedArticle.model_validate(doc.to_dict()) for doc in articles_snapshot]
        
        if not articles:
            raise HTTPException(status_code=404, detail="Nenhum artigo encontrado para processamento.")

        # TODO: Adicionar a lógica de processamento de NLP aqui.
        
        return articles

    except Exception as e:
        # Log de erro no Firestore
        error_log = ErrorLog(
            error_message=str(e),
            details=traceback.format_exc()
        )
        db.collection('erros_de_execucao_api_nlp').add(error_log.model_dump())
        
        # Lança uma exceção HTTP
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao processar os artigos: {e}")

