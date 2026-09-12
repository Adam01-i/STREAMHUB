from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.reference import Category
from app.models.stream import Stream


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

    async def list_with_active_stream(self, *, country: str | None = None, limit: int = 12) -> list[Channel]:
        stmt = select(Channel).join(Stream, Stream.channel_id == Channel.id).where(Channel.is_active.is_(True))
        if country:
            stmt = stmt.where(Channel.country_code == country.upper())
        stmt = stmt.distinct().limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def search(
        self,
        *,
        country: str | None = None,
        category: str | None = None,
        q: str | None = None,
        limit: int = 24,
        offset: int = 0,
    ) -> tuple[list[Channel], int]:
        stmt = select(Channel).where(Channel.is_active.is_(True))
        count_stmt = select(func.count(func.distinct(Channel.id))).select_from(Channel).where(
            Channel.is_active.is_(True)
        )

        if country:
            stmt = stmt.where(Channel.country_code == country.upper())
            count_stmt = count_stmt.where(Channel.country_code == country.upper())

        if category:
            stmt = stmt.join(Channel.categories).where(Category.id == category)
            count_stmt = count_stmt.join(Channel.categories).where(Category.id == category)

        if q:
            pattern = f"%{q}%"
            stmt = stmt.where(Channel.name.ilike(pattern))
            count_stmt = count_stmt.where(Channel.name.ilike(pattern))

        stmt = stmt.order_by(Channel.name).limit(limit).offset(offset)

        total = (await self.session.execute(count_stmt)).scalar_one()
        items = (await self.session.execute(stmt)).scalars().unique().all()
        return list(items), total

    async def upsert(self, channel: Channel) -> Channel:
        merged = await self.session.merge(channel)
        return merged