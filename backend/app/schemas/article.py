from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ArticleCreate(BaseModel):
    thematic_id: int
    alert_id: Optional[int] = None
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    language: str = "fr"
    tags: List[str] = []
    visibility: str = "public"


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    visibility: Optional[str] = None


class ArticleResponse(BaseModel):
    id: int
    thematic_id: int
    alert_id: Optional[int]
    title: str
    content: Optional[str]
    summary: Optional[str]
    status: str
    language: str
    author_id: Optional[int]
    tags: List[str] = []
    visibility: str
    created_at: datetime
    published_at: Optional[datetime]

    class Config:
        from_attributes = True
