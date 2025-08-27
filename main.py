from fastapi import FastAPI, BackgroundTasks, HTTPException
import traceback
import datetime
from database import get_db
from google_nlp_service import analyze_text
from models.schemas import SystemLog

app = FastAPI(
    title="API NLP",
    description="API para processamento de linguagem natural de artigos.",
    version="0.2.0"
)

def run_nlp_analysis_task():
    """
    Busca artigos com status 'scraper_ok', realiza a análise de NLP,
    salva os resultados e atualiza o status do artigo.
    Registra o processo na coleção system_logs.
    """
    db = get_db()
    system_logs_ref = db.collection('system_logs')
    monitor_results_ref = db.collection('monitor_results')
    
    start_time = datetime.datetime.now(datetime.timezone.utc)
    log_entry = SystemLog(
        task="Análise NLP",
        start_time=start_time,
        status="running"
    )
    log_doc = system_logs_ref.add(log_entry.model_dump())[1]

    processed_count = 0
    try:
        query = monitor_results_ref.where('status', '==', 'scraper_ok')
        articles_snapshot = query.stream()

        for doc in articles_snapshot:
            article_id = doc.id
            try:
                article_data = doc.to_dict()
                
                text_to_analyze = article_data.get("scraped_content", "") or article_data.get("scraped_title", "")

                if not text_to_analyze:
                    continue

                google_nlp_analysis = analyze_text(text_to_analyze)

                update_data = {
                    "google_nlp_analysis": google_nlp_analysis.model_dump(),
                    "status": "nlp_ok",
                    "last_processed_at": datetime.datetime.now(datetime.timezone.utc)
                }
                monitor_results_ref.document(article_id).update(update_data)
                
                processed_count += 1
            except Exception as e:
                error_message = f"Erro ao processar o artigo {article_id}: {e}"
                print(error_message)
                # Atualiza o status do artigo para 'nlp_error' e registra a mensagem de erro
                update_data = {
                    "status": "nlp_error",
                    "nlp_error_message": str(e),
                    "last_processed_at": datetime.datetime.now(datetime.timezone.utc)
                }
                monitor_results_ref.document(article_id).update(update_data)

        end_time = datetime.datetime.now(datetime.timezone.utc)
        log_entry.end_time = end_time
        log_entry.status = "completed"
        log_entry.processed_count = processed_count
        log_doc.update(log_entry.model_dump())

    except Exception as e:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        error_message = f"Erro geral na tarefa de análise NLP: {e}"
        log_entry.end_time = end_time
        log_entry.status = "failed"
        log_entry.error_message = error_message
        log_entry.processed_count = processed_count
        log_doc.update(log_entry.model_dump())
        print(error_message)
        traceback.print_exc()

@app.post("/run-nlp-analysis", status_code=202)
async def run_nlp_analysis(background_tasks: BackgroundTasks):
    """
    Aciona a tarefa de análise de NLP em segundo plano.
    """
    background_tasks.add_task(run_nlp_analysis_task)
    return {"message": "A tarefa de análise de NLP foi iniciada em segundo plano."}

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API NLP!"}
