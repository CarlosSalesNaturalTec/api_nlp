from google.cloud.language_v1 import LanguageServiceClient, types
from models.schemas import NlpAnalysis
import logging

def analyze_text(text: str) -> NlpAnalysis:
    """
    Analisa o texto de entrada usando a API Google Cloud Natural Language.
    """
    try:
        client = LanguageServiceClient()
        document = types.Document(
            content=text, type_=types.Document.Type.PLAIN_TEXT, language="pt"
        )

        # Análise de sentimento
        sentiment_response = client.analyze_sentiment(document=document)
        sentiment_score = sentiment_response.document_sentiment.score
        if sentiment_score > 0.25:
            sentiment = "positivo"
        elif sentiment_score < -0.25:
            sentiment = "negativo"
        else:
            sentiment = "neutro"

        # Análise de entidades
        entities_response = client.analyze_entities(document=document)
        entities = [entity.name for entity in entities_response.entities]

        # A classificação de conteúdo não está funcionando de forma confiável para o português, então pulamos.
        mention_type = "não classificado"

        return NlpAnalysis(
            mention_type=mention_type,
            sentiment=sentiment,            
            entities=entities,
        )
    except Exception as e:
        logging.error(f"Erro durante a análise de NLP: {e}")
        # Em caso de erro, ainda é necessário retornar um objeto NlpAnalysis.
        # Podemos retornar um com valores padrão/de erro.
        return NlpAnalysis(
            mention_type="erro na análise",
            sentiment="erro na análise",
            entities=[],
        )

