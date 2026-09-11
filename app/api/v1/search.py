from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.channel_repository import ChannelRepository
from app.schemas.channel import ChannelListItem

router = APIRouter(tags=["search"])


@router.get("/search", response_model=list[ChannelListItem])
async def search_channels(
    q: str = Query(..., min_length=1, description="Terme de recherche"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> list[ChannelListItem]:
    repo = ChannelRepository(db)
    items, _ = await repo.search(q=q, limit=limit, offset=0)
    return items
