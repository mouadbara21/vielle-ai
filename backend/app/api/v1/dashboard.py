from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User
from app.models.thematic import Thematic
from app.models.source import Source, Partition, Folder
from app.models.document import Document
from app.models.alert import Alert
from app.models.article import Article
from app.models.signal import Signal
from app.models.notification import CrawlJob
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Tableau de bord"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les statistiques KPI du tableau de bord."""
    thematics_count = (await db.execute(select(func.count(Thematic.id)))).scalar() or 0
    sources_count = (await db.execute(select(func.count(Source.id)))).scalar() or 0
    documents_count = (await db.execute(select(func.count(Document.id)))).scalar() or 0
    alerts_count = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
    alerts_unread = (await db.execute(select(func.count(Alert.id)).where(Alert.is_read == False))).scalar() or 0
    articles_count = (await db.execute(select(func.count(Article.id)))).scalar() or 0
    articles_published = (await db.execute(select(func.count(Article.id)).where(Article.status == "published"))).scalar() or 0
    signals_count = (await db.execute(select(func.count(Signal.id)))).scalar() or 0

    # Source status distribution
    sources_active = (await db.execute(select(func.count(Source.id)).where(Source.status == "active"))).scalar() or 0
    sources_error = (await db.execute(select(func.count(Source.id)).where(Source.status == "error"))).scalar() or 0
    sources_paused = (await db.execute(select(func.count(Source.id)).where(Source.status == "paused"))).scalar() or 0

    # Recent alerts by type
    from sqlalchemy import case
    alert_types = await db.execute(
        select(Alert.type, func.count(Alert.id)).group_by(Alert.type)
    )
    alert_by_type = {row[0].value if hasattr(row[0], 'value') else str(row[0]): row[1] for row in alert_types.all()}

    return {
        "thematics": thematics_count,
        "sources": {
            "total": sources_count,
            "active": sources_active,
            "error": sources_error,
            "paused": sources_paused,
        },
        "documents": documents_count,
        "alerts": {
            "total": alerts_count,
            "unread": alerts_unread,
            "by_type": alert_by_type,
        },
        "articles": {
            "total": articles_count,
            "published": articles_published,
        },
        "signals": signals_count,
    }


@router.get("/recent-alerts")
async def get_recent_alerts(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les alertes récentes pour le tableau de bord."""
    from sqlalchemy import desc
    from app.schemas.alert import AlertResponse

    result = await db.execute(
        select(Alert).order_by(desc(Alert.created_at)).limit(limit)
    )
    return [AlertResponse.model_validate(a) for a in result.scalars().all()]


@router.get("/recent-documents")
async def get_recent_documents(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les documents récemment collectés."""
    from sqlalchemy import desc
    from app.schemas.document import DocumentListResponse

    result = await db.execute(
        select(Document).order_by(desc(Document.collected_at)).limit(limit)
    )
    return [DocumentListResponse.model_validate(d) for d in result.scalars().all()]
