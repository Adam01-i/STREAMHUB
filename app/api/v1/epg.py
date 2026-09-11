from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.epg import Program
from app.schemas.epg import ProgramRead

router = APIRouter(prefix="/epg", tags=["epg"])


@router.get("/{channel_id}", response_model=list[ProgramRead])
async def get_channel_epg(channel_id: str, db: AsyncSession = Depends(get_db)) -> list[ProgramRead]:
    result = await db.execute(
        select(Program).where(Program.channel_id == channel_id).order_by(Program.start_time)
    )
    return list(result.scalars().all())
