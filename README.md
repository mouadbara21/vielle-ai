# VeilleAI - Intelligent Monitoring Platform

VeilleAI is a comprehensive, AI-powered information monitoring platform designed to help organizations collect, process, and analyze unstructured text data (news, articles, reports) efficiently. 

It provides an end-to-end pipeline:
1. **Crawling & Collection**: Automated fetching from websites, APIs, and RSS feeds.
2. **NLP & AI Processing**: Named Entity Recognition (NER), embedding generation, zero-shot classification, and LLM-powered summarization (via Gemini).
3. **Signal Detection**: Trend analysis and novelty scoring.
4. **Alerts & Dashboard**: Custom rule-based alerting and an intuitive frontend dashboard built with Next.js.

## Architecture

- **Frontend**: Next.js (App Router), Tailwind CSS, shadcn/ui.
- **Backend API**: FastAPI (Python), SQLAlchemy, JWT Authentication.
- **AI/Workers**: Celery, Redis, spaCy, Sentence-Transformers, Google Generative AI (Gemini).
- **Database**: PostgreSQL with `pgvector` for vector search.
- **Search Engine**: Elasticsearch for full-text search.
- **Containerization**: Docker & Docker Compose.

## Prerequisites

- **Docker & Docker Compose** installed on your system.
- **Python 3.10+** (if running scripts locally).
- **Node.js 18+** (if running frontend outside Docker).
- **Google Gemini API Key** (for LLM summarization).

## Setup Instructions

### 1. Environment Configuration
Copy the sample environment file and configure your settings:
```bash
cp .env.example .env
```
Ensure you add your `GEMINI_API_KEY` to the `.env` file for the AI pipeline to function properly.

### 2. Start the Stack
Build and start all services using Docker Compose:
```bash
docker-compose up --build -d
```
This will start:
- `postgres` (Port 5432)
- `redis` (Port 6379)
- `elasticsearch` (Port 9200)
- `api` (FastAPI - Port 8000)
- `celery-worker` (AI/Scraping tasks)
- `celery-beat` (Scheduled tasks)
- `frontend` (Next.js - Port 3000)

### 3. Database Setup & Migrations
The database schema should be automatically initialized. If you need to manually apply migrations using Alembic:
```bash
docker-compose exec api alembic upgrade head
```

### 4. Seed Initial Data
Populate the database with a test user, initial thématiques, and sources:
```bash
python scripts/seed_data.py
```
> **Note:** The script uses `python-dotenv` to load database credentials. If you are running it outside of Docker, make sure your Python environment has `sqlalchemy`, `psycopg2-binary`, and `python-dotenv` installed.

### 5. Access the Platform
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
  - Default Admin Credentials (from seed):
    - Email: `admin@veille.ai`
    - Password: `adminpassword`
- **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Key Workflows

1. **Add Sources**: Navigate to the "Sources" page to add URLs or RSS feeds.
2. **Crawl**: The Celery beat scheduler will automatically trigger crawls based on source frequency, or you can manually trigger them from the API.
3. **AI Processing**: Once a document is fetched, the Celery worker will automatically process it (NER, embeddings, summarization).
4. **Alerts**: Define rules in the "Signalements" page to receive alerts when documents match certain keywords or exceed AI scores.

## Troubleshooting

- **Elasticsearch Exits Code 137**: This means Docker lacks sufficient memory. Ensure Docker Desktop has at least 4GB of RAM allocated.
- **Postgres pgvector issues**: Make sure you are using the `pgvector/pgvector:pg16` image as specified in the `docker-compose.yml`.
