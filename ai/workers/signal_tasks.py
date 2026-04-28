import os
import logging
from datetime import datetime
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL_SYNC", "postgresql://veilleai:veilleai_secret@postgres:5432/veilleai")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(name="workers.signal_tasks.detect_signals_batch")
def detect_signals_batch():
    """Run weak signal detection across all thematics."""
    db = SessionLocal()
    try:
        # Get all thematic IDs
        result = db.execute(text("SELECT id FROM thematics"))
        thematic_ids = [row[0] for row in result.fetchall()]

        signals_found = 0
        for thematic_id in thematic_ids:
            from signals.trend_detector import detect_keyword_trends
            from signals.novelty_detector import detect_novelties

            # Detect keyword trends
            trends = detect_keyword_trends(thematic_id, db)
            for trend in trends:
                import json
                db.execute(text(
                    "INSERT INTO signals (thematic_id, type, title, description, confidence, "
                    "related_document_ids, trend_data, keywords, detected_at) "
                    "VALUES (:thematic_id, 'trend', :title, :description, :confidence, "
                    ":doc_ids, :trend_data, :keywords, :now)"
                ), {
                    "thematic_id": thematic_id,
                    "title": trend["title"],
                    "description": trend["description"],
                    "confidence": trend["confidence"],
                    "doc_ids": json.dumps(trend.get("document_ids", [])),
                    "trend_data": json.dumps(trend.get("trend_data", {})),
                    "keywords": json.dumps(trend.get("keywords", [])),
                    "now": datetime.utcnow(),
                })
                signals_found += 1

            # Detect novelties
            novelties = detect_novelties(thematic_id, db)
            for novelty in novelties:
                import json
                db.execute(text(
                    "INSERT INTO signals (thematic_id, type, title, description, confidence, "
                    "related_document_ids, keywords, detected_at) "
                    "VALUES (:thematic_id, 'novelty', :title, :description, :confidence, "
                    ":doc_ids, :keywords, :now)"
                ), {
                    "thematic_id": thematic_id,
                    "title": novelty["title"],
                    "description": novelty["description"],
                    "confidence": novelty["confidence"],
                    "doc_ids": json.dumps(novelty.get("document_ids", [])),
                    "keywords": json.dumps(novelty.get("keywords", [])),
                    "now": datetime.utcnow(),
                })
                signals_found += 1

        db.commit()
        logger.info(f"Signal detection batch completed: {signals_found} signals found")
        return {"signals_found": signals_found}

    except Exception as e:
        logger.error(f"Signal detection failed: {e}")
        raise
    finally:
        db.close()
