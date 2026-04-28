from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.user import User
from app.models.article import Article, ArticleStatus
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from app.core.dependencies import get_current_user, require_analyst

router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get("/", response_model=List[ArticleResponse])
async def list_articles(
    thematic_id: int = None,
    status_filter: str = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les articles."""
    query = select(Article).order_by(desc(Article.created_at)).limit(limit).offset(offset)
    if thematic_id:
        query = query.where(Article.thematic_id == thematic_id)
    if status_filter:
        query = query.where(Article.status == status_filter)
    result = await db.execute(query)
    return [ArticleResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Créer un nouvel article."""
    article = Article(
        thematic_id=data.thematic_id,
        alert_id=data.alert_id,
        title=data.title,
        content=data.content,
        summary=data.summary,
        language=data.language,
        tags=data.tags,
        visibility=data.visibility,
        author_id=current_user.id,
        status=ArticleStatus.DRAFT,
    )
    db.add(article)
    await db.flush()
    return ArticleResponse.model_validate(article)


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir les détails d'un article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return ArticleResponse.model_validate(article)


@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Mettre à jour un article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")

    update_data = data.model_dump(exclude_unset=True)

    # Handle publish
    if update_data.get("status") == "published" and article.status != ArticleStatus.PUBLISHED:
        update_data["published_at"] = datetime.utcnow()

    for field, value in update_data.items():
        setattr(article, field, value)

    await db.flush()
    return ArticleResponse.model_validate(article)


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_analyst),
):
    """Supprimer un article."""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    await db.delete(article)
