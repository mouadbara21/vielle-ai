import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.database import Base


class AccessLevel(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    GROUP = "group"


class Thematic(Base):
    __tablename__ = "thematics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    color = Column(String(7), default="#3B82F6")  # hex color
    description = Column(Text, nullable=True)
    access_portal = Column(SAEnum(AccessLevel), default=AccessLevel.PUBLIC)
    access_admin = Column(SAEnum(AccessLevel), default=AccessLevel.PRIVATE)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    partitions = relationship("Partition", back_populates="thematic", cascade="all, delete-orphan")
    keyword_triggers = relationship("KeywordTrigger", back_populates="thematic", cascade="all, delete-orphan")
    articles = relationship("Article", back_populates="thematic")
    signals = relationship("Signal", back_populates="thematic")


class ThematicUser(Base):
    __tablename__ = "thematic_users"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_level = Column(String(50), default="read")
