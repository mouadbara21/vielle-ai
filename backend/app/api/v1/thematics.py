from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.user import User, UserRole
from app.models.thematic import Thematic
from app.models.source import Partition, Folder, Source
from app.models.alert import Alert
from app.models.document import Document
from app.schemas.thematic import (
    ThematicCreate, ThematicUpdate, ThematicResponse,
    PartitionCreate, PartitionResponse,
    FolderCreate, FolderResponse,
)
from app.core.dependencies import get_current_user, require_admin, require_analyst

router = APIRouter(prefix="/thematics", tags=["Thématiques"])


@router.get("/", response_model=List[ThematicResponse])
async def list_thematics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister toutes les thématiques."""
    result = await db.execute(select(Thematic).order_by(Thematic.name))
    thematics = result.scalars().all()

    response = []
    for t in thematics:
        # Count related entities
        src_count = await db.execute(
            select(func.count(Source.id))
            .join(Folder, Source.folder_id == Folder.id)
            .join(Partition, Folder.partition_id == Partition.id)
            .where(Partition.thematic_id == t.id)
        )
        doc_count = await db.execute(
            select(func.count(Document.id))
            .join(Source, Document.source_id == Source.id)
            .join(Folder, Source.folder_id == Folder.id)
            .join(Partition, Folder.partition_id == Partition.id)
            .where(Partition.thematic_id == t.id)
        )
        alert_count = await db.execute(
            select(func.count(Alert.id)).where(Alert.thematic_id == t.id)
        )

        resp = ThematicResponse(
            id=t.id, name=t.name, color=t.color, description=t.description,
            access_portal=t.access_portal.value if t.access_portal else "public",
            access_admin=t.access_admin.value if t.access_admin else "private",
            created_at=t.created_at,
            source_count=src_count.scalar() or 0,
            document_count=doc_count.scalar() or 0,
            alert_count=alert_count.scalar() or 0,
        )
        response.append(resp)

    return response


@router.post("/", response_model=ThematicResponse, status_code=status.HTTP_201_CREATED)
async def create_thematic(
    data: ThematicCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Créer une nouvelle thématique (Admin uniquement)."""
    thematic = Thematic(
        name=data.name,
        color=data.color,
        description=data.description,
        access_portal=data.access_portal,
        access_admin=data.access_admin,
        created_by=current_user.id,
    )
    db.add(thematic)
    await db.flush()

    # Create default hierarchy
    default_partition = Partition(thematic_id=thematic.id, name="Général", order_index=0)
    db.add(default_partition)
    await db.flush()

    default_folder = Folder(partition_id=default_partition.id, name="Tous les flux", order_index=0)
    db.add(default_folder)
    await db.flush()

    return ThematicResponse(
        id=thematic.id, name=thematic.name, color=thematic.color,
        description=thematic.description,
        access_portal=data.access_portal, access_admin=data.access_admin,
        created_at=thematic.created_at,
    )


@router.get("/{thematic_id}", response_model=ThematicResponse)
async def get_thematic(
    thematic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtenir une thématique par ID."""
    result = await db.execute(select(Thematic).where(Thematic.id == thematic_id))
    thematic = result.scalar_one_or_none()
    if not thematic:
        raise HTTPException(status_code=404, detail="Thématique non trouvée")

    return ThematicResponse(
        id=thematic.id, name=thematic.name, color=thematic.color,
        description=thematic.description,
        access_portal=thematic.access_portal.value if thematic.access_portal else "public",
        access_admin=thematic.access_admin.value if thematic.access_admin else "private",
        created_at=thematic.created_at,
    )


@router.put("/{thematic_id}", response_model=ThematicResponse)
async def update_thematic(
    thematic_id: int,
    data: ThematicUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Mettre à jour une thématique (Admin uniquement)."""
    result = await db.execute(select(Thematic).where(Thematic.id == thematic_id))
    thematic = result.scalar_one_or_none()
    if not thematic:
        raise HTTPException(status_code=404, detail="Thématique non trouvée")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(thematic, field, value)

    await db.flush()

    return ThematicResponse(
        id=thematic.id, name=thematic.name, color=thematic.color,
        description=thematic.description,
        access_portal=thematic.access_portal.value if hasattr(thematic.access_portal, 'value') else str(thematic.access_portal),
        access_admin=thematic.access_admin.value if hasattr(thematic.access_admin, 'value') else str(thematic.access_admin),
        created_at=thematic.created_at,
    )


@router.delete("/{thematic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thematic(
    thematic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Supprimer une thématique (Admin uniquement)."""
    result = await db.execute(select(Thematic).where(Thematic.id == thematic_id))
    thematic = result.scalar_one_or_none()
    if not thematic:
        raise HTTPException(status_code=404, detail="Thématique non trouvée")
    await db.delete(thematic)


# --- Partitions ---

@router.get("/{thematic_id}/partitions", response_model=List[PartitionResponse])
async def list_partitions(
    thematic_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les partitions d'une thématique."""
    result = await db.execute(
        select(Partition).where(Partition.thematic_id == thematic_id).order_by(Partition.order_index)
    )
    return [PartitionResponse.model_validate(p) for p in result.scalars().all()]


@router.post("/{thematic_id}/partitions", response_model=PartitionResponse, status_code=status.HTTP_201_CREATED)
async def create_partition(
    thematic_id: int,
    data: PartitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Créer une partition dans une thématique."""
    partition = Partition(thematic_id=thematic_id, name=data.name, order_index=data.order_index)
    db.add(partition)
    await db.flush()
    return PartitionResponse.model_validate(partition)


# --- Folders ---

@router.post("/partitions/{partition_id}/folders", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    partition_id: int,
    data: FolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Créer un dossier dans une partition."""
    folder = Folder(partition_id=partition_id, name=data.name, parent_folder_id=data.parent_folder_id, order_index=data.order_index)
    db.add(folder)
    await db.flush()
    return FolderResponse.model_validate(folder)


@router.get("/all/folders", response_model=List[dict])
async def list_all_folders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister tous les dossiers de toutes les thématiques."""
    query = (
        select(
            Folder.id, 
            Folder.name.label("folder_name"), 
            Thematic.name.label("thematic_name")
        )
        .join(Partition, Folder.partition_id == Partition.id)
        .join(Thematic, Partition.thematic_id == Thematic.id)
        .order_by(Thematic.name, Folder.name)
    )
    result = await db.execute(query)
    folders = result.all()
    
    return [
        {
            "id": f.id, 
            "label": f"{f.thematic_name} / {f.folder_name}"
        } 
        for f in folders
    ]
