from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel, channel_categories
from app.models.reference import Category, Country, Language


class ReferenceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_countries_with_counts(self) -> list[tuple[Country, int]]:
        stmt = (
            select(Country, func.count(Channel.id))
            .join(
                Channel,
                (Channel.country_code == Country.code) & (Channel.is_active.is_(True)),
                isouter=True,
            )
            .group_by(Country.code)
            .order_by(Country.name)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_categories_with_counts(self) -> list[tuple[Category, int]]:
        stmt = (
            select(Category, func.count(channel_categories.c.channel_id))
            .join(channel_categories, channel_categories.c.category_id == Category.id, isouter=True)
            .group_by(Category.id)
            .order_by(Category.name)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_languages(self) -> list[Language]:
        result = await self.session.execute(select(Language).order_by(Language.name))
        return list(result.scalars().all())
