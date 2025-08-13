from firebase_admin import credentials, initialize_app, firestore, _apps
from dotenv import load_dotenv
import os

load_dotenv()

def get_db():
    # Garante que o Firebase seja inicializado apenas uma vez.
    if not _apps:
        cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
        initialize_app(cred)
    return firestore.client()
