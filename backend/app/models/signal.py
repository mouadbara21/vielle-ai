import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum as SAEnum, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class SignalType(str, enum.Enum):
    TREND = "trend"
    NOVELTY = "novelty"
    ANOMALY = "anomaly"
    EMERGENCE = "emergence"


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    thematic_id = Column(Integer, ForeignKey("thematics.id", ondelete="CASCADE"), nullable=True)
    type = Column(SAEnum(SignalType), nullable=False)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)
    related_document_ids = Column(JSON, default=list)
    trend_data = Column(JSON, nullable=True)  # time-series data for visualization
    keywords = Column(JSON, default=list)
    detected_at = Column(DateTime, default=datetime.utcnow)

    thematic = relationship("Thematic", back_populates="signals")
