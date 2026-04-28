import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class AlertType(str, enum.Enum):
    NEW_DOCUMENT = "new_document"
    DELETED_DOCUMENT = "deleted_document"
    MODIFIED_DOCUMENT = "modified_document"
    KEYWORD_MATCH = "keyword_match"
    WEAK_SIGNAL = "weak_signal"


class AlertPriority(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class KeywordTrigger(Base):
    __tablename__ = "keyword_triggers"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    query_expression = Column(Text, nullable=False)  # e.g. ("hydrogen" AND "aviation")
    scope = Column(String(50), default="new_documents")  # new_documents, modified, all
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    thematic = relationship("Thematic", back_populates="keyword_triggers")
    alerts = relationship("Alert", back_populates="trigger")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    trigger_id = Column(Integer, ForeignKey("keyword_triggers.id", ondelete="SET NULL"), nullable=True)
    type = Column(SAEnum(AlertType), nullable=False)
    priority = Column(SAEnum(AlertPriority), default=AlertPriority.MEDIUM)
    ai_score = Column(Float, default=0.5)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    is_processed = Column(Boolean, default=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="alerts")
    thematic = relationship("Thematic")
    trigger = relationship("KeywordTrigger", back_populates="alerts")
