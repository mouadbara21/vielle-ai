import os
from celery import Celery
from celery.schedules import crontab

# Celery configuration
celery_app = Celery(
    "veilleai",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1"),
    backend=os.getenv("REDIS_URL", "redis://redis:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Paris",
    enable_utc=True,
    task_routes={
        "workers.crawl_tasks.*": {"queue": "default"},
        "workers.nlp_tasks.*": {"queue": "default"},
        "workers.llm_tasks.*": {"queue": "low"},
        "workers.signal_tasks.*": {"queue": "low"},
        "workers.diffusion_tasks.*": {"queue": "high"},
    },
    beat_schedule={
        # Crawl all active sources every hour
        "crawl-hourly-sources": {
            "task": "workers.crawl_tasks.crawl_scheduled_sources",
            "schedule": crontab(minute=0),  # Every hour
            "args": ("hourly",),
        },
        # Crawl daily sources at 6 AM
        "crawl-daily-sources": {
            "task": "workers.crawl_tasks.crawl_scheduled_sources",
            "schedule": crontab(hour=6, minute=0),
            "args": ("daily",),
        },
        # Detect signals every 4 hours
        "detect-signals": {
            "task": "workers.signal_tasks.detect_signals_batch",
            "schedule": crontab(minute=0, hour="*/4"),
        },
    },
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["workers"])
