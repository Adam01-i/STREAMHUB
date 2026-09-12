from datetime import datetime, timedelta, timezone

import pytest

from app.core.database import AsyncSessionLocal
from app.models.channel import Channel
from app.models.epg import Program
from app.models.reference import Country
from app.models.stream import Stream
from app.services.content.classifier import ContentType
from app.services.content.live_now import LiveNowEngine


@pytest.mark.asyncio
async def test_get_now_playing_returns_active_program() -> None:
    fixed_now = datetime(2026, 9, 12, 19, 0, tzinfo=timezone.utc)

    async with AsyncSessionLocal() as session:
        country = await session.get(Country, "FR")
        if country is None:
            country = Country(code="FR", name="France")
            session.add(country)
            await session.flush()

        channel = Channel(id="TestLive.fr", name="Test Live", slug="test-live-fr", country_code="FR")
        session.add(channel)
        await session.flush()

        session.add(Stream(channel_id=channel.id, url="http://example.com/live.m3u8"))

        program = Program(
            channel_id=channel.id,
            title="France vs Italie",
            description="Match amical",
            start_time=fixed_now - timedelta(minutes=30),
            end_time=fixed_now + timedelta(minutes=30),
        )
        session.add(program)
        await session.commit()

        engine = LiveNowEngine(session, now=fixed_now)
        items = await engine.get_now_playing(content_type=ContentType.FOOTBALL, limit=10)

        assert any(item.channel.id == "TestLive.fr" for item in items)

        # Nettoyage
        await session.delete(program)
        await session.execute(
            Stream.__table__.delete().where(Stream.channel_id == "TestLive.fr")
        )
        await session.delete(channel)
        await session.commit()
