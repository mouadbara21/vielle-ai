from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ThematicCreate(BaseModel):
    name: str
    color: str = "#3B82F6"
    description: Optional[str] = None
    access_portal: str = "public"
    access_admin: str = "private"


class ThematicUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None
    access_portal: Optional[str] = None
    access_admin: Optional[str] = None


class ThematicResponse(BaseModel):
    id: int
    name: str
    color: str
    description: Optional[str]
    access_portal: str
    access_admin: str
    created_at: datetime
    source_count: int = 0
    document_count: int = 0
    alert_count: int = 0

    class Config:
        from_attributes = True


class PartitionCreate(BaseModel):
    thematic_id: int
    name: str
    order_index: int = 0


class PartitionResponse(BaseModel):
    id: int
    thematic_id: int
    name: str
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True


class FolderCreate(BaseModel):
    partition_id: int
    name: str
    parent_folder_id: Optional[int] = None
    order_index: int = 0


class FolderResponse(BaseModel):
    id: int
    partition_id: int
    parent_folder_id: Optional[int]
    name: str
    order_index: int
    created_at: datetime

    class Config:
        from_attributes = True
