from fastapi import FastAPI, BackgroundTasks, HTTPException
import traceback
import datetime
from database import get_db, get_whatsapp_message, update_whatsapp_message
from google_nlp_service import analyze_text
from models.schemas import SystemLog, WhatsAppMessagePayload

app = FastAPI(
    title="API NLP",
    description="API para processamento de linguagem natural de artigos e mensagens.",
    version="0.3.0"
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
        task="Análise NLP - Web Scraping",
        start_time=start_time,
        status="running"
    )
    log_doc_ref = system_logs_ref.document()
    log_doc_ref.set(log_entry.model_dump())

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
        log_doc_ref.update(log_entry.model_dump())

    except Exception as e:
        end_time = datetime.datetime.now(datetime.timezone.utc)
        error_message = f"Erro geral na tarefa de análise NLP: {e}"
        log_entry.end_time = end_time
        log_entry.status = "failed"
        log_entry.error_message = error_message
        log_entry.processed_count = processed_count
        log_doc_ref.update(log_entry.model_dump())
        print(error_message)
        traceback.print_exc()

def process_whatsapp_message_task(payload: WhatsAppMessagePayload):
    """
    Busca uma mensagem do WhatsApp, realiza a análise de NLP,
    e atualiza o documento no Firestore.
    """
    db = get_db()
    group_id = payload.group_id
    message_id = payload.message_id

    try:
        message_data = get_whatsapp_message(db, group_id, message_id)

        if not message_data:
            print(f"Mensagem {group_id}/{message_id} não encontrada.")
            return

        if message_data.get("nlp_status") != "pending":
            print(f"Mensagem {group_id}/{message_id} já foi processada ou não requer processamento.")
            return
        
        text_to_analyze = message_data.get("message_text")
        if not text_to_analyze:
            update_data = {"nlp_status": "not_applicable"}
            update_whatsapp_message(db, group_id, message_id, update_data)
            return

        nlp_analysis_result = analyze_text(text_to_analyze)

        update_data = {
            "nlp_analysis": nlp_analysis_result.model_dump(),
            "nlp_status": "ok"
        }
        update_whatsapp_message(db, group_id, message_id, update_data)

    except Exception as e:
        error_message = f"Erro ao processar mensagem do WhatsApp {group_id}/{message_id}: {e}"
        print(error_message)
        traceback.print_exc()
        try:
            update_data = {
                "nlp_status": "error",
                "nlp_error_message": str(e)
            }
            update_whatsapp_message(db, group_id, message_id, update_data)
        except Exception as update_e:
            print(f"Falha ao registrar o erro no Firestore para a mensagem {group_id}/{message_id}: {update_e}")


@app.post("/run-nlp-analysis", status_code=202, tags=["Web Scraping Analysis"])
async def run_nlp_analysis(background_tasks: BackgroundTasks):
    """
    Aciona a tarefa de análise de NLP para artigos da web em segundo plano.
    """
    background_tasks.add_task(run_nlp_analysis_task)
    return {"message": "A tarefa de análise de NLP para artigos da web foi iniciada em segundo plano."}

@app.post("/process/whatsapp-message", status_code=202, tags=["WhatsApp Message Analysis"])
async def process_whatsapp_message(payload: WhatsAppMessagePayload, background_tasks: BackgroundTasks):
    """
    Recebe o ID de uma mensagem do WhatsApp e aciona a tarefa de análise de NLP em segundo plano.
    """
    background_tasks.add_task(process_whatsapp_message_task, payload)
    return {"message": "A tarefa de análise da mensagem do WhatsApp foi iniciada em segundo plano."}


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bem-vindo à API NLP!"}