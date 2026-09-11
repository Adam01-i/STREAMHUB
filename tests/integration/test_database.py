import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.channel import Channel
from app.models.reference import Country
from app.repositories.channel_repository import ChannelRepository


@pytest.mark.asyncio
async def test_insert_and_fetch_channel() -> None:
    async with AsyncSessionLocal() as session:
        country = await session.get(Country, "SN")
        if country is None:
            country = Country(code="SN", name="Senegal", flag="🇸🇳")
            session.add(country)
            await session.flush()

        channel = Channel(
            id="TestChannel.sn",
            name="Test Channel",
            slug="test-channel-sn",
            country_code="SN",
        )
        session.add(channel)
        await session.commit()

        repo = ChannelRepository(session)
        fetched = await repo.get_by_id("TestChannel.sn")
        assert fetched is not None
        assert fetched.name == "Test Channel"

        await session.execute(select(Channel).where(Channel.id == "TestChannel.sn"))
        await session.delete(fetched)
        await session.delete(country)
        await session.commit()