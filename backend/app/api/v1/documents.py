from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    source_id: int = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les documents collectés."""
    query = select(Document).order_by(desc(Document.collected_at)).limit(limit).offset(offset)
    if source_id:
        query = query.where(Document.source_id == source_id)
    result = await db.execute(query)
    return [DocumentListResponse.model_validate(d) for d in result.scalars().all()]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les détails complets d'un document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    return DocumentResponse.model_validate(doc)


@router.post("/{document_id}/summarize")
async def summarize_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Demander un résumé IA pour un document."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document non trouvé")

    # TODO: Enqueue Celery LLM task
    # from ai.workers.llm_tasks import summarize_document_task
    # summarize_document_task.delay(document_id)

    return {"message": "Résumé en cours de génération", "document_id": document_id}
