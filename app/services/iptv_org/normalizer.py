import re
import unicodedata

from app.services.iptv_org.parser import ExternalChannel


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def build_channel_slug(channel: ExternalChannel) -> str:
    base = slugify(channel.name)
    country_suffix = f"-{channel.country.lower()}" if channel.country else ""
    return f"{base}{country_suffix}"


def is_channel_allowed(channel: ExternalChannel, blocked_ids: set[str]) -> bool:
    """Filtre légal/éthique : exclut chaînes fermées, NSFW et bloquées (DMCA)."""
    if channel.closed is not None:
        return False
    if channel.is_nsfw:
        return False
    if channel.id in blocked_ids:
        return False
    return True


def normalize_channel(channel: ExternalChannel) -> dict:
    return {
        "id": channel.id,
        "name": channel.name,
        "slug": build_channel_slug(channel),
        "alt_names": channel.alt_names,
        "network": channel.network,
        "owners": channel.owners,
        "country_code": channel.country,
        "website": channel.website,
        "is_nsfw": channel.is_nsfw,
        "launched": channel.launched,
        "closed": channel.closed,
        "replaced_by": channel.replaced_by,
        "category_ids": channel.categories,
    }
