from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert, KeywordTrigger
from app.schemas.alert import AlertResponse, AlertUpdate, KeywordTriggerCreate, KeywordTriggerResponse
from app.core.dependencies import get_current_user, require_analyst, require_admin

router = APIRouter(prefix="/alerts", tags=["Alertes"])


@router.get("/", response_model=List[AlertResponse])
async def list_alerts(
    thematic_id: int = None,
    type: str = None,
    is_read: bool = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les alertes avec filtres optionnels."""
    query = select(Alert).order_by(desc(Alert.ai_score), desc(Alert.created_at)).limit(limit).offset(offset)
    if thematic_id:
        query = query.where(Alert.thematic_id == thematic_id)
    if type:
        query = query.where(Alert.type == type)
    if is_read is not None:
        query = query.where(Alert.is_read == is_read)

    result = await db.execute(query)
    return [AlertResponse.model_validate(a) for a in result.scalars().all()]


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    data: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Marquer une alerte comme lue/traitée."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(alert, field, value)
    await db.flush()
    return AlertResponse.model_validate(alert)


# --- Keyword Triggers ---

@router.get("/triggers", response_model=List[KeywordTriggerResponse])
async def list_triggers(
    thematic_id: int = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les déclencheurs de mots-clés."""
    query = select(KeywordTrigger)
    if thematic_id:
        query = query.where(KeywordTrigger.thematic_id == thematic_id)
    result = await db.execute(query)
    return [KeywordTriggerResponse.model_validate(t) for t in result.scalars().all()]


@router.post("/triggers", response_model=KeywordTriggerResponse, status_code=status.HTTP_201_CREATED)
async def create_trigger(
    data: KeywordTriggerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Créer un nouveau déclencheur de mots-clés."""
    trigger = KeywordTrigger(
        thematic_id=data.thematic_id,
        name=data.name,
        query_expression=data.query_expression,
        scope=data.scope,
        created_by=current_user.id,
    )
    db.add(trigger)
    await db.flush()
    return KeywordTriggerResponse.model_validate(trigger)
