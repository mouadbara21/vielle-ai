from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class SourceCreate(BaseModel):
    folder_id: int
    name: str
    url: str
    type: str = "web"
    crawl_frequency: str = "daily"
    scraper_config: Optional[Dict[str, Any]] = None


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None
    crawl_frequency: Optional[str] = None
    status: Optional[str] = None
    scraper_config: Optional[Dict[str, Any]] = None


class SourceResponse(BaseModel):
    id: int
    folder_id: int
    name: str
    url: str
    type: str
    crawl_frequency: str
    status: str
    last_crawled_at: Optional[datetime]
    error_count: int
    created_at: datetime

    class Config:
        from_attributes = True
