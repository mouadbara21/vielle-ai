import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SAEnum, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class SourceType(str, enum.Enum):
    WEB = "web"
    RSS = "rss"
    SOCIAL = "social"
    FILE = "file"
    API = "api"


class CrawlFrequency(str, enum.Enum):
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MANUAL = "manual"


class SourceStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    BLOCKED = "blocked"


class Partition(Base):
    __tablename__ = "partitions"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    thematic = relationship("Thematic", back_populates="partitions")
    folders = relationship("Folder", back_populates="partition", cascade="all, delete-orphan")


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    partition_id = Column(Integer, ForeignKey("partitions.id", ondelete="CASCADE"), nullable=False)
    parent_folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    partition = relationship("Partition", back_populates="folders")
    parent = relationship("Folder", remote_side="Folder.id", backref="subfolders")
    sources = relationship("Source", back_populates="folder", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(Integer, ForeignKey("folders.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    type = Column(SAEnum(SourceType), default=SourceType.WEB)
    crawl_frequency = Column(SAEnum(CrawlFrequency), default=CrawlFrequency.DAILY)
    status = Column(SAEnum(SourceStatus), default=SourceStatus.ACTIVE)
    scraper_config = Column(JSON, nullable=True)  # CSS selectors, exclusion zones
    last_crawled_at = Column(DateTime, nullable=True)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    folder = relationship("Folder", back_populates="sources")
    documents = relationship("Document", back_populates="source", cascade="all, delete-orphan")
