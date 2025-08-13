from fastapi import FastAPI, Depends, HTTPException
from google.cloud.firestore_v1.client import Client
from database import get_db
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import requests

load_dotenv()

app = FastAPI()

# Chave de API do Google e ID do Mecanismo de Pesquisa Personalizado
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

@app.get("/")
def read_root():
    return {"message": "api_coletor_google no ar!"}

@app.post("/coletar-dados")
def coletar_dados(db: Client = Depends(get_db)):
    try:
        # Obter termos de pesquisa do Firestore
        termos_ref = db.collection("termos_pesquisa")
        termos_docs = list(termos_ref.stream())

        if not termos_docs:
            raise HTTPException(status_code=404, detail="Nenhum termo de pesquisa encontrado no Firestore.")

        resultados_finais = []
        
        data_pesquisa = datetime.now(timezone.utc)

        # Consultar a API do Google CSE para cada conjunto de termos
        for doc in termos_docs:
            doc_data = doc.to_dict()
            termos = doc_data.get("termos")
            id_busca = doc_data.get("id_busca")

            if termos and isinstance(termos, list):
                query_string = " ".join(termos)
                search_url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    "key": GOOGLE_API_KEY,
                    "cx": CUSTOM_SEARCH_ENGINE_ID,
                    "q": query_string
                }
                response = requests.get(search_url, params=params)
                response.raise_for_status()  # Lança exceção para respostas de erro
                resultados = response.json().get("items", [])

                # Salvar resultados no Firestore
                for resultado in resultados:
                    dados_para_salvar = {
                        "title": resultado.get("title"),
                        "snippet": resultado.get("snippet"),
                        "displayLink": resultado.get("displayLink"),
                        "link": resultado.get("link"),
                        "data_pesquisa": data_pesquisa,
                        "id_busca": id_busca
                    }
                    db.collection("resultados_pesquisa").add(dados_para_salvar)
                resultados_finais.extend(resultados)

        return {"message": "Dados coletados e salvos com sucesso!", "resultados": len(resultados_finais)}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar a API do Google: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro: {e}")