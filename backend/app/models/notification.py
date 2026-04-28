import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, JSON, Boolean, Text
from app.database import Base


class RecipientType(str, enum.Enum):
    EMAIL = "email"
    RSS = "rss"
    WEBHOOK = "webhook"
    XML = "xml"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class CrawlJobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    type = Column(SAEnum(RecipientType), nullable=False)
    address = Column(String(500), nullable=False)  # email, URL, etc.
    frequency = Column(String(50), default="daily")
    format = Column(String(50), default="html")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("recipients.id", ondelete="CASCADE"), nullable=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="SET NULL"), nullable=True)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True)
    channel = Column(SAEnum(RecipientType), nullable=False)
    status = Column(SAEnum(NotificationStatus), default=NotificationStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CrawlJob(Base):
    __tablename__ = "crawl_jobs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    status = Column(SAEnum(CrawlJobStatus), default=CrawlJobStatus.PENDING)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    documents_found = Column(Integer, default=0)
    errors = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
