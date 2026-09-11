from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.templates import templates
from app.models.channel import Channel
from app.models.stream import Stream
from app.repositories.channel_repository import ChannelRepository
from app.repositories.reference_repository import ReferenceRepository
from app.repositories.stream_repository import StreamRepository

router = APIRouter(tags=["web"])


@router.get("/")
async def home(request: Request, db: AsyncSession = Depends(get_db)):
    ref_repo = ReferenceRepository(db)
    countries = await ref_repo.list_countries_with_counts()
    categories = await ref_repo.list_categories_with_counts()

    sn_stmt = (
        select(Channel)
        .join(Stream, Stream.channel_id == Channel.id)
        .where(Channel.country_code == "SN", Channel.is_active.is_(True))
        .distinct()
        .limit(8)
    )
    senegal_channels = (await db.execute(sn_stmt)).scalars().unique().all()

    live_stmt = (
        select(Channel)
        .join(Stream, Stream.channel_id == Channel.id)
        .where(Channel.is_active.is_(True))
        .distinct()
        .limit(12)
    )
    live_channels = (await db.execute(live_stmt)).scalars().unique().all()

    top_countries = sorted(countries, key=lambda pair: pair[1], reverse=True)[:12]

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "senegal_channels": senegal_channels,
            "live_channels": live_channels,
            "top_countries": top_countries,
            "categories": categories[:10],
        },
    )


@router.get("/channels")
async def channels_page(
    request: Request,
    country: str | None = Query(None),
    category: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
):
    limit = 24
    offset = (page - 1) * limit

    repo = ChannelRepository(db)
    items, total = await repo.search(country=country, category=category, q=q, limit=limit, offset=offset)

    ref_repo = ReferenceRepository(db)
    countries = await ref_repo.list_countries_with_counts()
    categories = await ref_repo.list_categories_with_counts()

    total_pages = max(1, (total + limit - 1) // limit)

    return templates.TemplateResponse(
        "channels.html",
        {
            "request": request,
            "channels": items,
            "countries": sorted(countries, key=lambda p: p[0].name),
            "categories": sorted(categories, key=lambda p: p[0].name),
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "selected_country": country or "",
            "selected_category": category or "",
            "q": q or "",
        },
    )


@router.get("/channel/{channel_id}")
async def channel_detail_page(request: Request, channel_id: str, db: AsyncSession = Depends(get_db)):
    channel_repo = ChannelRepository(db)
    stream_repo = StreamRepository(db)

    channel = await channel_repo.get_by_id(channel_id)
    if channel is None:
        return templates.TemplateResponse(
            "not_found.html", {"request": request, "channel_id": channel_id}, status_code=404
        )

    streams = await stream_repo.list_for_channel(channel_id)

    similar_stmt = (
        select(Channel)
        .where(
            Channel.country_code == channel.country_code,
            Channel.id != channel.id,
            Channel.is_active.is_(True),
        )
        .limit(8)
    )
    similar_channels = (await db.execute(similar_stmt)).scalars().all()

    return templates.TemplateResponse(
        "channel_detail.html",
        {
            "request": request,
            "channel": channel,
            "streams": streams,
            "similar_channels": similar_channels,
        },
    )
