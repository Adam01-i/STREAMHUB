from functools import lru_cache

from app.core.config import get_settings
from app.services.ads.base import AdProvider
from app.services.ads.providers import GoogleAdSenseProvider, NullAdProvider


@lru_cache
def get_ad_provider() -> AdProvider:
    settings = get_settings()

    if settings.ad_provider == "google" and settings.adsense_client_id:
        slot_ids = {
            "homepage_top": settings.ad_slot_homepage_top or "",
            "between_sections": settings.ad_slot_between_sections or "",
            "channel_detail": settings.ad_slot_channel_detail or "",
        }
        return GoogleAdSenseProvider(client_id=settings.adsense_client_id, slot_ids=slot_ids)

    return NullAdProvider()
