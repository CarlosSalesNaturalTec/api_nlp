from fastapi import FastAPI, HTTPException
import traceback
import datetime
import pytz

from database import get_db
from models.schemas import ScrapedArticle, NlpAnalysis, AnalysisResult, ErrorLog
from nlp_service import analyze_text

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

    sao_paulo_tz = pytz.timezone("America/Sao_Paulo")
    hora_inicio_utc = datetime.datetime.now(datetime.timezone.utc)
    hora_inicio_br_str = hora_inicio_utc.astimezone(sao_paulo_tz).strftime('%d/%m/%Y %H:%M:%S %Z')

    try:
        # Busca por artigos com status 'pending' para o owner especificado
        query = articles_ref.where('owner', '==', owner).where('status', '==', 'pending')
        articles_snapshot = query.stream()
        print(f"Iniciando análise NLP para o owner: '{owner}'. Data e Hora de início: {hora_inicio_br_str}")

        articles_to_process = []
        for doc in articles_snapshot:
            article_data = doc.to_dict()
            article_data['id'] = doc.id
            # Convertendo timestamps do Firestore para datetime, se necessário
            if 'scraped_at' in article_data and hasattr(article_data['scraped_at'], 'to_datetime'):
                article_data['scraped_at'] = article_data['scraped_at'].to_datetime()
            if 'publish_date' in article_data and article_data['publish_date'] and hasattr(article_data['publish_date'], 'to_datetime'):
                article_data['publish_date'] = article_data['publish_date'].to_datetime()
            articles_to_process.append(ScrapedArticle.model_validate(article_data))

        if not articles_to_process:
            print(f"Nenhum artigo pendente encontrado para o owner '{owner}'.")
            return {"message": f"Nenhum artigo pendente encontrado para o owner '{owner}'."}

        for article in articles_to_process:
            try:
                # 1. Realiza a Análise NLP
                nlp_analysis = analyze_text(article.text)

                # 2. Cria o resultado da análise
                analysis_result = AnalysisResult(
                    article=article,
                    nlp_analysis=nlp_analysis,
                    processed_at=datetime.datetime.now(datetime.timezone.utc)
                )

                # 3. Salva o resultado em 'nlp_analysis_results'
                # Usamos .model_dump() para converter o objeto Pydantic em um dicionário
                results_collection.add(analysis_result.model_dump(by_alias=True, exclude_none=True))

                # 4. Atualiza o status do artigo original para 'processed'
                article_doc_ref = articles_ref.document(article.id)
                article_doc_ref.update({"status": "processed"})
                
                print(f"Análise NLP do artigo '{article.id}' concluída com sucesso.")
                processed_count += 1

            except Exception as e:
                error_detail = traceback.format_exc()
                errors.append(f"Erro ao processar artigo {article.id}: {e}")
                print(f"Erro ao processar artigo {article.id}: {e}")
                
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
        
        hora_fim_utc = datetime.datetime.now(datetime.timezone.utc)
        tempo_total = hora_fim_utc - hora_inicio_utc
        hora_fim_br_str = hora_fim_utc.astimezone(sao_paulo_tz).strftime('%d/%m/%Y %H:%M:%S %Z')

        print(f"Processamento concluído para o owner '{owner}'. Total de artigos processados: {processed_count}. Hora de fim: {hora_fim_br_str}, Tempo total: {tempo_total}.")

        return response

    except Exception as e:
        # Log de erro geral no Firestore
        error_log = ErrorLog(
            error_message=str(e),
            details=traceback.format_exc()
        )
        db.collection('erros_de_execucao_api_nlp').add(error_log.model_dump())
        
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro geral ao processar os artigos: {e}")

# Rota temporária para desenvolvimento/testes
@app.post("/reset-status/{owner}", response_model=dict)
def reset_status_to_pending(owner: str):
    """
    Reseta o status de todos os artigos de um 'owner' para 'pending'.
    Rota para fins de desenvolvimento e teste.
    """
    db = get_db()
    articles_ref = db.collection('scraped_articles')
    updated_count = 0
    
    try:
        query = articles_ref.where('owner', '==', owner)
        articles_snapshot = query.stream()

        for doc in articles_snapshot:
            doc.reference.update({"status": "pending"})
            updated_count += 1
        
        return {
            "message": f"Operação concluída para o owner '{owner}'.",
            "updated_count": updated_count
        }

    except Exception as e:
        error_log = ErrorLog(
            error_message=f"Erro ao resetar status para o owner {owner}: {e}",
            details=traceback.format_exc()
        )
        db.collection('erros_de_execucao_api_nlp').add(error_log.model_dump())
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro ao resetar o status dos artigos: {e}")
