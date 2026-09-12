from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.epg import Program
from app.models.stream import Stream
from app.services.content.classifier import ContentType, classify_program_text


@dataclass
class LiveNowItem:
    channel: Channel
    program: Program
    content_type: ContentType
    is_live: bool


class LiveNowEngine:
    """Détermine ce qui est réellement diffusé maintenant ou bientôt, à partir des vrais
    programmes EPG importés (table `programs`). Ne fabrique jamais d'événement : si `programs`
    est vide pour une chaîne, cette chaîne n'apparaît simplement pas ici.
    """

    def __init__(self, session: AsyncSession, now: datetime | None = None) -> None:
        self.session = session
        self.now = now or datetime.now(timezone.utc)

    async def _query(self, *, start_after: bool, horizon_minutes: int | None, limit_rows: int):
        stmt = (
            select(Program, Channel)
            .join(Channel, Channel.id == Program.channel_id)
            .join(Stream, Stream.channel_id == Channel.id)
            .where(Channel.is_active.is_(True))
        )
        if start_after:
            horizon = self.now + timedelta(minutes=horizon_minutes or 0)
            stmt = stmt.where(Program.start_time > self.now, Program.start_time <= horizon)
            stmt = stmt.order_by(Program.start_time.asc())
        else:
            stmt = stmt.where(Program.start_time <= self.now, Program.end_time >= self.now)
            stmt = stmt.order_by(Program.start_time.desc())

        stmt = stmt.distinct().limit(limit_rows)
        result = await self.session.execute(stmt)
        return result.unique().all()

    async def get_now_playing(
        self, content_type: ContentType | None = None, limit: int = 12
    ) -> list[LiveNowItem]:
        rows = await self._query(start_after=False, horizon_minutes=None, limit_rows=200)
        items: list[LiveNowItem] = []
        for program, channel in rows:
            classified, _score = classify_program_text(program.title, program.description, program.category)
            if content_type is not None and classified != content_type:
                continue
            items.append(LiveNowItem(channel=channel, program=program, content_type=classified, is_live=True))
            if len(items) >= limit:
                break
        return items

    async def get_upcoming(
        self, content_type: ContentType | None = None, limit: int = 12, within_minutes: int = 180
    ) -> list[LiveNowItem]:
        rows = await self._query(start_after=True, horizon_minutes=within_minutes, limit_rows=200)
        items: list[LiveNowItem] = []
        for program, channel in rows:
            classified, _score = classify_program_text(program.title, program.description, program.category)
            if content_type is not None and classified != content_type:
                continue
            items.append(LiveNowItem(channel=channel, program=program, content_type=classified, is_live=False))
            if len(items) >= limit:
                break
        return items
