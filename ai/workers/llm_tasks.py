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


@celery_app.task(name="workers.llm_tasks.summarize_document")
def summarize_document(document_id: int):
    """Generate AI summary for a document using Gemini."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id, content, title FROM documents WHERE id = :id"), {"id": document_id})
        doc = result.fetchone()
        if not doc or not doc[1]:
            return {"error": "Document not found or empty"}

        content = doc[1]
        title = doc[2] or ""

        from llm.summarizer import generate_summary
        summary = generate_summary(title, content)

        if summary:
            db.execute(text(
                "UPDATE documents SET summary = :summary, updated_at = :now WHERE id = :id"
            ), {"summary": summary, "now": datetime.utcnow(), "id": document_id})
            db.commit()

        logger.info(f"Summary generated for document {document_id}")
        return {"document_id": document_id, "summary_length": len(summary) if summary else 0}

    except Exception as e:
        logger.error(f"Summarization failed for document {document_id}: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name="workers.llm_tasks.generate_watch_note")
def generate_watch_note(thematic_id: int, document_ids: list):
    """Generate a watch note (note de veille) from multiple documents."""
    db = SessionLocal()
    try:
        # Fetch document summaries
        placeholders = ",".join([str(did) for did in document_ids])
        result = db.execute(text(
            f"SELECT title, summary, content FROM documents WHERE id IN ({placeholders})"
        ))
        docs = result.fetchall()

        combined_text = "\n\n".join([
            f"## {doc[0]}\n{doc[1] or doc[2][:500]}" for doc in docs
        ])

        from llm.summarizer import generate_watch_note
        note = generate_watch_note(combined_text)

        logger.info(f"Watch note generated for thematic {thematic_id}")
        return {"thematic_id": thematic_id, "note": note}

    except Exception as e:
        logger.error(f"Watch note generation failed: {e}")
        raise
    finally:
        db.close()
