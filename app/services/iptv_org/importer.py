from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel, Feed
from app.models.reference import Category, Country, Language
from app.models.stream import Stream
from app.services.iptv_org.client import IptvOrgClient
from app.services.iptv_org.deduplicator import dedupe_by_key
from app.services.iptv_org.normalizer import is_channel_allowed, normalize_channel
from app.services.iptv_org.parser import (
    parse_blocklist,
    parse_categories,
    parse_channels,
    parse_countries,
    parse_feeds,
    parse_languages,
    parse_streams,
)

# imports à ajouter en haut du fichier
import asyncio

import httpx
from sqlalchemy import delete

from app.models.epg import Program
from app.services.iptv_org.xmltv_parser import parse_xmltv

class ImportReport(dict):
    """Petit dict typé pour le rapport de sync (voir SyncRun.report_json)."""


async def import_reference_data(session: AsyncSession, client: IptvOrgClient) -> None:
    countries = parse_countries(await client.get_countries())
    for c in countries:
        existing = await session.get(Country, c.code)
        if existing is None:
            session.add(Country(code=c.code, name=c.name, flag=c.flag))
        else:
            existing.name = c.name
            existing.flag = c.flag

    languages = parse_languages(await client.get_languages())
    for lang in languages:
        existing = await session.get(Language, lang.code)
        if existing is None:
            session.add(Language(code=lang.code, name=lang.name))
        else:
            existing.name = lang.name

    categories = parse_categories(await client.get_categories())
    for cat in categories:
        existing = await session.get(Category, cat.id)
        if existing is None:
            session.add(Category(id=cat.id, name=cat.name, description=cat.description))
        else:
            existing.name = cat.name
            existing.description = cat.description

    await session.commit()


async def import_channels(session: AsyncSession, client: IptvOrgClient) -> dict:
    raw_channels = parse_channels(await client.get_channels())
    blocklist = parse_blocklist(await client.get_blocklist())
    blocked_ids = {entry.channel for entry in blocklist if entry.reason == "dmca"}

    raw_channels, duplicates = dedupe_by_key(raw_channels, key_fn=lambda c: c.id)

    known_country_codes: set[str] = {
        row[0] for row in (await session.execute(select(Country.code))).all()
    }
    known_category_ids: set[str] = {
        row[0] for row in (await session.execute(select(Category.id))).all()
    }
    existing_slugs: set[str] = {
        row[0] for row in (await session.execute(select(Channel.slug))).all()
    }

    imported = 0
    updated = 0
    invalid = 0

    for ext_channel in raw_channels:
        if not is_channel_allowed(ext_channel, blocked_ids):
            invalid += 1
            continue

        data = normalize_channel(ext_channel)
        if data["country_code"] and data["country_code"] not in known_country_codes:
            data["country_code"] = None  # évite une violation de contrainte FK

        category_ids = [cid for cid in data.pop("category_ids") if cid in known_category_ids]

        existing = await session.get(Channel, data["id"])

        if existing is None:
            # Résout les collisions de slug (ex: "AMC.us" et "AMC+.us" -> même base "amc-us")
            base_slug = data["slug"]
            slug = base_slug
            suffix = 2
            while slug in existing_slugs:
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            data["slug"] = slug
            existing_slugs.add(slug)

            channel = Channel(**data)
            if category_ids:
                result = await session.execute(select(Category).where(Category.id.in_(category_ids)))
                channel.categories = list(result.scalars().all())
            session.add(channel)
            imported += 1
        else:
            data.pop("slug", None)  # le slug d'une chaîne existante ne change jamais après création
            for field, value in data.items():
                setattr(existing, field, value)
            if category_ids:
                result = await session.execute(select(Category).where(Category.id.in_(category_ids)))
                existing.categories = list(result.scalars().all())
            updated += 1

    await session.commit()

    return {
        "channels_discovered": len(raw_channels),
        "channels_imported": imported,
        "channels_updated": updated,
        "duplicates_ignored": duplicates,
        "invalid_records": invalid,
    }


async def import_feeds(session: AsyncSession, client: IptvOrgClient) -> int:
    raw_feeds = parse_feeds(await client.get_feeds())
    known_channel_ids: set[str] = {row[0] for row in (await session.execute(select(Channel.id))).all()}

    count = 0
    for ext_feed in raw_feeds:
        if ext_feed.channel not in known_channel_ids:
            continue

        existing_result = await session.execute(
            select(Feed).where(Feed.channel_id == ext_feed.channel, Feed.feed_code == ext_feed.id)
        )
        existing = existing_result.scalar_one_or_none()

        payload = {
            "channel_id": ext_feed.channel,
            "feed_code": ext_feed.id,
            "name": ext_feed.name,
            "alt_names": ext_feed.alt_names,
            "is_main": ext_feed.is_main,
            "broadcast_area": ext_feed.broadcast_area,
            "timezones": ext_feed.timezones,
            "languages": ext_feed.languages,
            "format": ext_feed.format,
        }

        if existing is None:
            session.add(Feed(**payload))
        else:
            for field, value in payload.items():
                setattr(existing, field, value)
        count += 1

    await session.commit()
    return count


async def import_streams(session: AsyncSession, client: IptvOrgClient) -> int:
    raw_streams = parse_streams(await client.get_streams())
    known_channel_ids: set[str] = {row[0] for row in (await session.execute(select(Channel.id))).all()}

    feed_lookup: dict[tuple[str, str], int] = {
        (row.channel_id, row.feed_code): row.id
        for row in (await session.execute(select(Feed.id, Feed.channel_id, Feed.feed_code))).all()
    }

    count = 0
    for ext_stream in raw_streams:
        channel_id = ext_stream.channel if ext_stream.channel in known_channel_ids else None
        feed_id = feed_lookup.get((ext_stream.channel or "", ext_stream.feed or ""))

        existing_result = await session.execute(
            select(Stream).where(Stream.channel_id == channel_id, Stream.url == ext_stream.url)
        )
        existing = existing_result.scalar_one_or_none()

        payload = {
            "channel_id": channel_id,
            "feed_id": feed_id,
            "title": ext_stream.title,
            "url": ext_stream.url,
            "referrer": ext_stream.referrer,
            "user_agent": ext_stream.user_agent,
            "quality": ext_stream.quality,
            "label": ext_stream.label,
        }

        if existing is None:
            session.add(Stream(**payload))
        else:
            for field, value in payload.items():
                setattr(existing, field, value)
        count += 1

    await session.commit()
    return count  # toujours un entier, jamais None

# fonction à ajouter à la fin de importer.py
async def import_epg(session: AsyncSession, client: IptvOrgClient) -> dict:
    """EPG best-effort : n'importe des programmes que pour les chaînes ayant une vraie entrée guides.json."""
    guides_raw = await client.get_guides()
    known_channel_ids: set[str] = {row[0] for row in (await session.execute(select(Channel.id))).all()}

    guide_by_channel: dict[str, str] = {}
    for g in guides_raw:
        channel_id = g.get("channel")
        sources = g.get("sources") or []
        if channel_id and channel_id in known_channel_ids and sources and channel_id not in guide_by_channel:
            guide_by_channel[channel_id] = sources[0]["url"]

    semaphore = asyncio.Semaphore(5)  # ne pas marteler les sites sources

    async def fetch(channel_id: str, url: str) -> tuple[str, str, bytes | None]:
        async with semaphore:
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as http_client:
                    response = await http_client.get(url)
                    response.raise_for_status()
                    return channel_id, url, response.content
            except Exception:
                return channel_id, url, None

    results = await asyncio.gather(*(fetch(cid, url) for cid, url in guide_by_channel.items()))

    imported_channels = 0
    imported_programs = 0
    failed = 0

    for channel_id, guide_url, xml_bytes in results:
        if xml_bytes is None:
            failed += 1
            continue

        try:
            programs = parse_xmltv(xml_bytes, channel_id)
        except Exception:
            failed += 1
            continue

        if not programs:
            continue

        await session.execute(delete(Program).where(Program.channel_id == channel_id))
        for p in programs:
            session.add(Program(channel_id=channel_id, source_site=guide_url, **p))

        imported_channels += 1
        imported_programs += len(programs)

    await session.commit()

    return {
        "epg_channels_with_guide": len(guide_by_channel),
        "epg_channels_imported": imported_channels,
        "epg_programs_imported": imported_programs,
        "epg_failed": failed,
    }