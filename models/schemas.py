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

class SystemLog(BaseModel):
    task: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    processed_count: int = 0
    error_message: Optional[str] = None

class WhatsAppMessagePayload(BaseModel):
    group_id: str
    message_id: str