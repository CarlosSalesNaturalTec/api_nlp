from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ScrapedArticle(BaseModel):
    title: str
    url: str
    authors: List[str]
    text: str
    scraped_by: str
    top_image: Optional[str] = None
    scraped_at: datetime
    domain: str
    publish_date: Optional[datetime] = None

class NlpAnalysis(BaseModel):
    mention_type: str
    sentiment: str
    author_profile: str
    intentions: List[str]
    entities: List[str]

class AnalysisResult(BaseModel):
    article: ScrapedArticle
    nlp_analysis: NlpAnalysis
    processed_at: datetime = Field(default_factory=datetime.now)

class ErrorLog(BaseModel):
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[str] = None
