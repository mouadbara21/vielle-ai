FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies, download model, and purge build tools in a single layer to minimize size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download fr_core_news_md \
    && apt-get purge -y --auto-remove build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["celery", "-A", "workers.celery_app", "worker", "--loglevel=info"]
