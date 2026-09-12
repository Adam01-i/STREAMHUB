from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    app_debug: bool = True
    app_name: str = "StreamHub IPTV"

    database_url: str
    redis_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_access_expire_minutes: int = 30
    jwt_refresh_expire_days: int = 14

    iptv_org_base_url: str
    iptv_org_channels_url: str
    iptv_org_feeds_url: str
    iptv_org_streams_url: str
    iptv_org_logos_url: str
    iptv_org_guides_url: str
    iptv_org_categories_url: str
    iptv_org_languages_url: str
    iptv_org_countries_url: str
    iptv_org_blocklist_url: str

    cors_origins: str = ""

    # Publicité — désactivée par défaut, aucun impact tant que non configurée
    ad_provider: str = "none"  # "none" | "google"
    adsense_client_id: str | None = None
    ad_slot_homepage_top: str | None = None
    ad_slot_between_sections: str | None = None
    ad_slot_channel_detail: str | None = None

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()