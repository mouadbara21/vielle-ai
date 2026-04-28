import os
import hashlib
import logging
from datetime import datetime
from workers.celery_app import celery_app
from crawler.web_crawler import WebCrawler
from scraper.article_scraper import ArticleScraper

logger = logging.getLogger(__name__)

# Database connection for tasks
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL_SYNC", "postgresql://veilleai:veilleai_secret@postgres:5432/veilleai")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


@celery_app.task(name="workers.crawl_tasks.crawl_source")
def crawl_source(source_id: int):
    """Crawl a single source and process its content."""
    from sqlalchemy import text

    db = SessionLocal()
    try:
        # Get source
        result = db.execute(text("SELECT id, url, name, scraper_config FROM sources WHERE id = :id"), {"id": source_id})
        source = result.fetchone()
        if not source:
            logger.error(f"Source {source_id} not found")
            return {"error": "Source not found"}

        source_url = source[1]
        source_name = source[2]

        logger.info(f"Crawling source: {source_name} ({source_url})")

        # Create crawl job
        db.execute(text(
            "INSERT INTO crawl_jobs (source_id, status, started_at, created_at) VALUES (:source_id, 'running', :now, :now)"
        ), {"source_id": source_id, "now": datetime.utcnow()})
        db.commit()

        # Crawl the page or RSS feed
        config = source[3] or {}
        if isinstance(config, str):
            import json
            try:
                config = json.loads(config)
            except:
                config = {}

        if config.get("type") == "rss":
            from crawler.rss_collector import RSSCollector
            collector = RSSCollector()
            pages = collector.collect(source_url, max_items=20)
        else:
            crawler = WebCrawler()
            pages = crawler.crawl(source_url, max_pages=10)

        documents_found = 0
        for page in pages:
            # Extract article content
            scraper = ArticleScraper()
            article = scraper.extract(page["html"], page["url"])

            if not article or not article.get("content"):
                continue

            # Compute content hash for change detection
            content_hash = hashlib.sha256(article["content"].encode()).hexdigest()

            # Check if document already exists
            existing = db.execute(
                text("SELECT id, content_hash FROM documents WHERE url = :url AND source_id = :source_id"),
                {"url": page["url"], "source_id": source_id}
            ).fetchone()

            if existing:
                if existing[1] != content_hash:
                    # Document modified — update and create version
                    db.execute(text(
                        "UPDATE documents SET content = :content, title = :title, content_hash = :hash, "
                        "version = version + 1, updated_at = :now WHERE id = :id"
                    ), {
                        "content": article["content"], "title": article["title"],
                        "hash": content_hash, "now": datetime.utcnow(), "id": existing[0]
                    })
                    # Save version history
                    db.execute(text(
                        "INSERT INTO document_versions (document_id, content, content_hash, version, detected_at) "
                        "SELECT id, content, content_hash, version, :now FROM documents WHERE id = :id"
                    ), {"now": datetime.utcnow(), "id": existing[0]})
                    documents_found += 1

                    # Trigger NLP processing
                    process_document.delay(existing[0])
                continue

            # New document — insert
            db.execute(text(
                "INSERT INTO documents (source_id, url, title, content, content_hash, collected_at, version, created_at, updated_at, tags, entities) "
                "VALUES (:source_id, :url, :title, :content, :hash, :now, 1, :now, :now, '[]', '{}')"
            ), {
                "source_id": source_id, "url": page["url"],
                "title": article["title"], "content": article["content"],
                "hash": content_hash, "now": datetime.utcnow(),
            })
            db.commit()

            # Get new document id
            new_doc = db.execute(
                text("SELECT id FROM documents WHERE url = :url AND source_id = :source_id ORDER BY id DESC LIMIT 1"),
                {"url": page["url"], "source_id": source_id}
            ).fetchone()

            if new_doc:
                documents_found += 1
                # Trigger NLP processing
                process_document.delay(new_doc[0])

        # Update source last_crawled_at
        db.execute(text(
            "UPDATE sources SET last_crawled_at = :now, error_count = 0, status = 'active' WHERE id = :id"
        ), {"now": datetime.utcnow(), "id": source_id})

        # Update crawl job
        db.execute(text(
            "UPDATE crawl_jobs SET status = 'completed', completed_at = :now, documents_found = :count "
            "WHERE source_id = :source_id AND status = 'running'"
        ), {"now": datetime.utcnow(), "count": documents_found, "source_id": source_id})

        db.commit()
        logger.info(f"Crawl completed for {source_name}: {documents_found} documents found")
        return {"source_id": source_id, "documents_found": documents_found}

    except Exception as e:
        logger.error(f"Crawl failed for source {source_id}: {e}")
        db.execute(text(
            "UPDATE sources SET error_count = error_count + 1, status = 'error' WHERE id = :id"
        ), {"id": source_id})
        db.execute(text(
            "UPDATE crawl_jobs SET status = 'failed', completed_at = :now WHERE source_id = :source_id AND status = 'running'"
        ), {"now": datetime.utcnow(), "source_id": source_id})
        db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="workers.crawl_tasks.crawl_scheduled_sources")
def crawl_scheduled_sources(frequency: str):
    """Crawl all sources matching the given frequency."""
    from sqlalchemy import text

    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT id FROM sources WHERE crawl_frequency = :freq AND status = 'active'"),
            {"freq": frequency}
        )
        source_ids = [row[0] for row in result.fetchall()]
        logger.info(f"Scheduled crawl for {len(source_ids)} {frequency} sources")

        for source_id in source_ids:
            crawl_source.delay(source_id)

        return {"scheduled": len(source_ids), "frequency": frequency}
    finally:
        db.close()


@celery_app.task(name="workers.crawl_tasks.process_document")
def process_document(document_id: int):
    """Run NLP pipeline on a document."""
    from workers.nlp_tasks import run_nlp_pipeline
    run_nlp_pipeline.delay(document_id)
