import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ArticleVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    GROUP = "group"


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    alert_id = Column(Integer, ForeignKey("alerts.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(SAEnum(ArticleStatus), default=ArticleStatus.DRAFT)
    language = Column(String(10), default="fr")
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tags = Column(JSON, default=list)
    visibility = Column(SAEnum(ArticleVisibility), default=ArticleVisibility.PUBLIC)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    thematic = relationship("Thematic", back_populates="articles")
