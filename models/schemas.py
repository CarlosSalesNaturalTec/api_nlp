from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ScrapedArticle(BaseModel):
    id: str
    title: str
    url: str
    authors: List[str]
    text: str
    scraped_by: str
    top_image: Optional[str] = None
    scraped_at: datetime
    domain: str
    publish_date: Optional[datetime] = None
    owner: str
    status: str

class ModerationResult(BaseModel):
    category: str
    confidence: float

class GoogleNlpAnalysis(BaseModel):
    sentiment: str
    entities: List[str]
    moderation_results: List[ModerationResult]

class AnalysisResult(BaseModel):
    article: ScrapedArticle
    google_nlp_analysis: GoogleNlpAnalysis
    processed_at: datetime = Field(default_factory=datetime.now)

class ErrorLog(BaseModel):
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[str] = None
