import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings

settings = get_settings()

_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class IptvOrgClient:
    """Client pour les fichiers JSON statiques publiés par iptv-org."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True)

    async def aclose(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get_json(self, url: str) -> list[dict]:
        response = await self._client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_channels(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_channels_url)

    async def get_feeds(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_feeds_url)

    async def get_streams(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_streams_url)

    async def get_logos(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_logos_url)

    async def get_guides(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_guides_url)

    async def get_categories(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_categories_url)

    async def get_languages(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_languages_url)

    async def get_countries(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_countries_url)

    async def get_blocklist(self) -> list[dict]:
        return await self._get_json(settings.iptv_org_blocklist_url)
