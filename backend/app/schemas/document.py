from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    source_id: int
    url: str
    title: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    language: Optional[str]
    tags: List[str] = []
    entities: Dict[str, Any] = {}
    sentiment_score: Optional[float]
    ai_classification: Optional[str]
    version: int
    collected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    id: int
    source_id: int
    url: str
    title: Optional[str]
    summary: Optional[str]
    sentiment_score: Optional[float]
    ai_classification: Optional[str]
    collected_at: datetime

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    query: str
    thematic_id: Optional[int] = None
    limit: int = 20
