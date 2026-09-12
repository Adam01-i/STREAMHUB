from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.repositories.channel_repository import ChannelRepository
from app.services.content.classifier import FALLBACK_CATEGORY_BY_CONTENT_TYPE, ContentType
from app.services.content.live_now import LiveNowEngine

router = APIRouter(tags=["discovery"])


async def _render_discovery_page(
    request: Request,
    db: AsyncSession,
    content_type: ContentType,
    icon: str,
    page_title: str,
):
    engine = LiveNowEngine(db)
    live_items = await engine.get_now_playing(content_type=content_type, limit=24)
    upcoming_items = await engine.get_upcoming(content_type=content_type, limit=12)

    fallback_channels: list = []
    if not live_items:
        category_id = FALLBACK_CATEGORY_BY_CONTENT_TYPE.get(content_type)
        if category_id:
            channel_repo = ChannelRepository(db)
            fallback_channels, _total = await channel_repo.search(category=category_id, limit=24)

    return templates.TemplateResponse(
        "discovery.html",
        {
            "request": request,
            "page_title": page_title,
            "icon": icon,
            "live_items": live_items,
            "upcoming_items": upcoming_items,
            "fallback_channels": fallback_channels,
        },
    )


@router.get("/football")
async def football_page(request: Request, db: AsyncSession = Depends(get_db)):
    return await _render_discovery_page(request, db, ContentType.FOOTBALL, "⚽", "Football")


@router.get("/movies")
async def movies_page(request: Request, db: AsyncSession = Depends(get_db)):
    return await _render_discovery_page(request, db, ContentType.MOVIE, "🎬", "Films")


@router.get("/series")
async def series_page(request: Request, db: AsyncSession = Depends(get_db)):
    return await _render_discovery_page(request, db, ContentType.SERIES, "📺", "Séries")


@router.get("/live")
async def live_page(request: Request, db: AsyncSession = Depends(get_db)):
    engine = LiveNowEngine(db)
    live_items = await engine.get_now_playing(limit=48)

    channel_repo = ChannelRepository(db)
    live_channels = await channel_repo.list_with_active_stream(limit=48)

    return templates.TemplateResponse(
        "live.html",
        {"request": request, "live_items": live_items, "live_channels": live_channels},
    )
