from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class KeywordTriggerCreate(BaseModel):
    thematic_id: int
    name: str
    query_expression: str
    scope: str = "new_documents"


class KeywordTriggerResponse(BaseModel):
    id: int
    thematic_id: int
    name: str
    query_expression: str
    scope: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    document_id: Optional[int]
    thematic_id: int
    trigger_id: Optional[int]
    type: str
    priority: str
    ai_score: float
    title: Optional[str]
    description: Optional[str]
    is_read: bool
    is_processed: bool
    details: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_processed: Optional[bool] = None
