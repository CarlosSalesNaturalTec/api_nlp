from firebase_admin import credentials, initialize_app, firestore, _apps
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    """
    Initializes and returns a Firestore client.
    Ensures that Firebase is initialized only once.
    """
    if not _apps:
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        if not cred_path:
            raise ValueError("A variável de ambiente GOOGLE_APPLICATION_CREDENTIALS não está definida.")
        
        # Normaliza o caminho para o formato correto do sistema operacional
        cred_path = os.path.normpath(cred_path)

        # Verifica se o arquivo de credenciais existe
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"O arquivo de credenciais não foi encontrado em: {cred_path}")
            
        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
    return firestore.client()

def get_whatsapp_message(db, group_id: str, message_id: str):
    """
    Fetches a specific WhatsApp message document from Firestore.
    """
    try:
        message_ref = db.collection('whatsapp_groups').document(group_id).collection('messages').document(message_id)
        message_doc = message_ref.get()
        if message_doc.exists:
            return message_doc.to_dict()
        return None
    except Exception as e:
        print(f"Erro ao buscar mensagem do WhatsApp ({group_id}/{message_id}): {e}")
        raise

def update_whatsapp_message(db, group_id: str, message_id: str, update_data: dict):
    """
    Updates a specific WhatsApp message document in Firestore.
    """
    try:
        message_ref = db.collection('whatsapp_groups').document(group_id).collection('messages').document(message_id)
        message_ref.update(update_data)
    except Exception as e:
        print(f"Erro ao atualizar mensagem do WhatsApp ({group_id}/{message_id}): {e}")
        raise