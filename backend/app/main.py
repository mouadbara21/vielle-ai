from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import init_db
from app.api.v1 import auth, thematics, sources, documents, alerts, articles, dashboard, users

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    await init_db()
    yield
    # Shutdown


app = FastAPI(
    title="VeilleAI API",
    description="Plateforme de Veille Intelligente basée sur l'IA — API REST",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(thematics.router, prefix="/api/v1")
app.include_router(sources.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(articles.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "VeilleAI API",
        "version": "1.0.0",
        "description": "Plateforme de Veille Intelligente",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
