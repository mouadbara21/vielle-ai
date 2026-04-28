from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.core.dependencies import get_current_user, require_admin, require_analyst

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("/", response_model=List[SourceResponse])
async def list_sources(
    folder_id: int = None,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les sources, optionnellement filtrées par dossier."""
    query = select(Source)
    if folder_id:
        query = query.where(Source.folder_id == folder_id)
    if status_filter:
        query = query.where(Source.status == status_filter)
    query = query.order_by(Source.name)

    result = await db.execute(query)
    return [SourceResponse.model_validate(s) for s in result.scalars().all()]


@router.post("/", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    data: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Ajouter une nouvelle source à surveiller."""
    source = Source(
        folder_id=data.folder_id,
        name=data.name,
        url=data.url,
        type=data.type,
        crawl_frequency=data.crawl_frequency,
        scraper_config=data.scraper_config,
    )
    db.add(source)
    await db.flush()
    return SourceResponse.model_validate(source)


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les détails d'une source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")
    return SourceResponse.model_validate(source)


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    data: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Mettre à jour une source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(source, field, value)
    await db.flush()
    return SourceResponse.model_validate(source)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Supprimer une source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")
    await db.delete(source)


@router.post("/{source_id}/crawl", status_code=status.HTTP_202_ACCEPTED)
async def trigger_crawl(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Déclencher un crawl manuel pour une source."""
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source non trouvée")

    # TODO: Enqueue Celery crawl task
    # from ai.workers.crawl_tasks import crawl_source
    # crawl_source.delay(source_id)

    return {"message": f"Crawl déclenché pour la source '{source.name}'", "source_id": source_id}
