from fastapi import FastAPI, HTTPException, Body
from typing import List
import traceback
import datetime

from database import get_db
from models.schemas import ScrapedArticle, NlpAnalysis, AnalysisResult, ErrorLog

app = FastAPI(
    title="API NLP",
    description="API para processamento de linguagem natural de artigos.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API NLP!"}

@app.post("/analyze/{owner}", response_model=dict)
def analyze_articles_by_owner(owner: str):
    """
    Busca artigos pendentes de um 'owner' específico, realiza a análise de NLP,
    salva os resultados e atualiza o status do artigo.
    """
    db = get_db()
    articles_ref = db.collection('scraped_articles')
    results_collection = db.collection('nlp_analysis_results')
    
    processed_count = 0
    errors = []

    try:
        # Busca por artigos com status 'pending' para o owner especificado
        query = articles_ref.where('owner', '==', owner).where('status', '==', 'pending')
        articles_snapshot = query.stream()

        articles_to_process = []
        for doc in articles_snapshot:
            article_data = doc.to_dict()
            article_data['id'] = doc.id
            articles_to_process.append(ScrapedArticle.model_validate(article_data))

        if not articles_to_process:
            return {"message": f"Nenhum artigo pendente encontrado para o owner '{owner}'."}

        for article in articles_to_process:
            try:
                # 1. Simulação da Análise NLP
                # (Aqui entrará a lógica real de NLP)
                nlp_analysis = NlpAnalysis(
                    mention_type="notícia",
                    sentiment="neutro",
                    author_profile="indefinido",
                    intentions=["informar"],
                    entities=["OMC", "Donald Trump", "Brasil", "China"]
                )

                # 2. Cria o resultado da análise
                analysis_result = AnalysisResult(
                    article=article,
                    nlp_analysis=nlp_analysis,
                    processed_at=datetime.datetime.now(datetime.timezone.utc)
                )

                # 3. Salva o resultado em 'nlp_analysis_results'
                results_collection.add(analysis_result.model_dump(exclude_none=True))

                # 4. Atualiza o status do artigo original para 'processed'
                article_doc_ref = articles_ref.document(article.id)
                article_doc_ref.update({"status": "processed"})
                
                processed_count += 1

            except Exception as e:
                error_detail = traceback.format_exc()
                errors.append(f"Erro ao processar artigo {article.id}: {e}")
                # Log de erro individual no Firestore
                error_log = ErrorLog(
                    error_message=f"Falha no processamento do artigo ID: {article.id} - {e}",
                    details=error_detail
                )
                db.collection('erros_de_execucao_api_nlp').add(error_log.model_dump())

        response = {
            "message": f"Processamento concluído para o owner '{owner}'.",
            "processed_count": processed_count,
        }
        if errors:
            response["errors"] = errors
        
        return response

    except Exception as e:
        # Log de erro geral no Firestore
        error_log = ErrorLog(
            error_message=str(e),
            details=traceback.format_exc()
        )
        db.collection('erros_de_execucao_api_nlp').add(error_log.model_dump())
        
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro geral ao processar os artigos: {e}")

