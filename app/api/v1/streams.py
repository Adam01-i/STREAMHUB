from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.stream_repository import StreamRepository
from app.schemas.stream import StreamRead

router = APIRouter(prefix="/streams", tags=["streams"])


@router.get("", response_model=list[StreamRead])
async def list_streams(
    channel_id: str = Query(..., description="Identifiant de la chaîne"),
    db: AsyncSession = Depends(get_db),
) -> list[StreamRead]:
    repo = StreamRepository(db)
    return await repo.list_for_channel(channel_id)


@router.get("/best", response_model=StreamRead)
async def best_stream(
    channel_id: str = Query(..., description="Identifiant de la chaîne"),
    db: AsyncSession = Depends(get_db),
) -> StreamRead:
    repo = StreamRepository(db)
    stream = await repo.best_for_channel(channel_id)
    if stream is None:
        raise HTTPException(status_code=404, detail="Aucun flux disponible pour cette chaîne")
    return stream
