from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    url = Column(Text, nullable=False)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    language = Column(String(10), nullable=True)
    published_at = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON, default=list)
    entities = Column(JSON, default=dict)  # {"persons": [], "organizations": [], "locations": []}
    embedding = Column(Vector(384), nullable=True)  # sentence-transformers dimension
    content_hash = Column(String(64), nullable=True, index=True)
    sentiment_score = Column(Float, nullable=True)  # -1.0 to 1.0
    ai_classification = Column(String(255), nullable=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("Source", back_populates="documents")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)
    version = Column(Integer, nullable=False)
    detected_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="versions")
