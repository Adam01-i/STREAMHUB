from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.channel_repository import ChannelRepository
from app.schemas.channel import ChannelListItem, ChannelRead

router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", response_model=list[ChannelListItem])
async def list_channels(
    response: Response,
    country: str | None = Query(None, description="Code pays ISO 3166-1 alpha-2, ex: SN"),
    category: str | None = Query(None, description="Identifiant de catégorie, ex: news"),
    q: str | None = Query(None, description="Recherche sur le nom de la chaîne"),
    limit: int = Query(24, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ChannelListItem]:
    repo = ChannelRepository(db)
    items, total = await repo.search(country=country, category=category, q=q, limit=limit, offset=offset)
    response.headers["X-Total-Count"] = str(total)
    return items


@router.get("/{channel_id}", response_model=ChannelRead)
async def get_channel(channel_id: str, db: AsyncSession = Depends(get_db)) -> ChannelRead:
    repo = ChannelRepository(db)
    channel = await repo.get_by_id(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Chaîne introuvable")
    return channel
