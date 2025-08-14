from google.cloud import language_v1
from models.schemas import NlpAnalysis
import logging

def analyze_text(text: str) -> NlpAnalysis:
    """
    Analyzes the input text using Google Cloud Natural Language API.
    """
    try:
        client = language_v1.LanguageServiceClient()
        document = language_v1.types.Document(
            content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
        )

        # Sentiment analysis
        sentiment_response = client.analyze_sentiment(document=document)
        sentiment_score = sentiment_response.document_sentiment.score
        if sentiment_score > 0.25:
            sentiment = "positivo"
        elif sentiment_score < -0.25:
            sentiment = "negativo"
        else:
            sentiment = "neutro"

        # Entity analysis
        entities_response = client.analyze_entities(document=document)
        entities = [entity.name for entity in entities_response.entities]

        # Content classification
        classification_response = client.classify_text(document=document)
        categories = [category.name for category in classification_response.categories]
        # For now, we'll just join the categories. This might need refinement.
        mention_type = ", ".join(categories) if categories else "não classificado"

        return NlpAnalysis(
            mention_type=mention_type,
            sentiment=sentiment,            
            entities=entities,
        )
    except Exception as e:
        logging.error(f"Error during NLP analysis: {e}")
        # In case of an error, we still need to return an NlpAnalysis object.
        # We can return one with default/error values.
        return NlpAnalysis(
            mention_type="erro na análise",
            sentiment="erro na análise",
            entities=[],
        )

