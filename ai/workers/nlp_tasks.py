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


@celery_app.task(name="workers.nlp_tasks.run_nlp_pipeline")
def run_nlp_pipeline(document_id: int):
    """Run full NLP pipeline on a document: NER, classification, sentiment, embeddings."""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT id, content, title FROM documents WHERE id = :id"), {"id": document_id})
        doc = result.fetchone()
        if not doc or not doc[1]:
            return {"error": "Document not found or empty"}

        content = doc[1]
        title = doc[2] or ""
        full_text = f"{title}\n{content}"

        # 1. Language detection
        from nlp.language_detector import detect_language
        language = detect_language(full_text)

        # 2. NER extraction
        from nlp.ner_extractor import extract_entities
        entities = extract_entities(full_text, language)

        # 3. Sentiment analysis
        from nlp.sentiment import analyze_sentiment
        sentiment_score = analyze_sentiment(full_text)

        # 4. Generate embedding
        from nlp.embedder import generate_embedding
        embedding = generate_embedding(full_text)

        # 5. Classification (based on thematic centroids)
        from nlp.classifier import classify_document
        classification = classify_document(embedding, db)

        # Update document with NLP results
        import json
        db.execute(text(
            "UPDATE documents SET language = :lang, entities = :entities, "
            "sentiment_score = :sentiment, embedding = :embedding, "
            "ai_classification = :classification, updated_at = :now "
            "WHERE id = :id"
        ), {
            "lang": language,
            "entities": json.dumps(entities),
            "sentiment": sentiment_score,
            "embedding": str(embedding),
            "classification": classification,
            "now": datetime.utcnow(),
            "id": document_id,
        })
        db.commit()

        # 6. Check keyword triggers and generate alerts
        from alerts.alert_generator import check_and_generate_alerts
        check_and_generate_alerts(document_id, content, entities, sentiment_score, db)

        logger.info(f"NLP pipeline completed for document {document_id}")
        return {
            "document_id": document_id,
            "language": language,
            "entities_count": sum(len(v) for v in entities.values()),
            "sentiment": sentiment_score,
            "classification": classification,
        }

    except Exception as e:
        logger.error(f"NLP pipeline failed for document {document_id}: {e}")
        raise
    finally:
        db.close()
