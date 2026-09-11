from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stream import Stream


class StreamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_channel(self, channel_id: str) -> list[Stream]:
        result = await self.session.execute(
            select(Stream).where(Stream.channel_id == channel_id, Stream.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def best_for_channel(self, channel_id: str) -> Stream | None:
        result = await self.session.execute(
            select(Stream)
            .where(Stream.channel_id == channel_id, Stream.is_active.is_(True))
            .order_by(Stream.status.asc(), Stream.failure_count.asc())
            .limit(1)
        )
        return result.scalar_one_or_none()