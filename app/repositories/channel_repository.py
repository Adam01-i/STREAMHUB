from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel


class ChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, channel_id: str) -> Channel | None:
        result = await self.session.execute(select(Channel).where(Channel.id == channel_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Channel | None:
        result = await self.session.execute(select(Channel).where(Channel.slug == slug))
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 50, offset: int = 0) -> list[Channel]:
        result = await self.session.execute(
            select(Channel).where(Channel.is_active.is_(True)).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def upsert(self, channel: Channel) -> Channel:
        merged = await self.session.merge(channel)
        return merged