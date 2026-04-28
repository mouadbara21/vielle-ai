from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "VeilleAI"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://veilleai:veilleai_secret@postgres:5432/veilleai"
    DATABASE_URL_SYNC: str = "postgresql://veilleai:veilleai_secret@postgres:5432/veilleai"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"

    # JWT
    SECRET_KEY: str = "changeme-super-secret-key-minimum-32-chars!!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini AI
    GEMINI_API_KEY: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
