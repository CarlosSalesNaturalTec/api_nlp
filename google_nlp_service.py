from google.cloud.language_v1 import LanguageServiceClient, types
from models.schemas import GoogleNlpAnalysis, ModerationResult
import logging

def analyze_text(text: str) -> GoogleNlpAnalysis:
    """
    Analisa o texto de entrada usando a API Google Cloud Natural Language. Levanta uma exceção em caso de erro.
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

        # Moderação de conteúdo
        moderation_response = client.moderate_text(document=document)
        moderation_results = []
        for category in moderation_response.moderation_categories:
            moderation_results.append(
                ModerationResult(
                    category=category.name,
                    confidence=category.confidence
                )
            )

        return GoogleNlpAnalysis(
            sentiment=sentiment,
            entities=entities,
            moderation_results=moderation_results,
        )
    except Exception as e:
        logging.error(f"Erro durante a análise de NLP: {e}")
        # Log do erro detalhado
        logging.exception("Detalhes da exceção:")
        # Re-lança a exceção para que o chamador possa tratá-la.
        raise