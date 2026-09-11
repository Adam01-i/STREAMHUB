import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SourceStatus
from app.schemas.reference import CategoryRead, CountryRead


class FeedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    feed_code: str
    name: str
    is_main: bool
    broadcast_area: list[str]
    timezones: list[str]
    languages: list[str]
    format: str | None = None


class ChannelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    uuid: uuid.UUID
    name: str
    slug: str
    alt_names: list[str]
    network: str | None = None
    logo_url: str | None = None
    website: str | None = None
    is_nsfw: bool
    is_active: bool
    source_status: SourceStatus
    launched: date | None = None
    closed: date | None = None
    country: CountryRead | None = None
    categories: list[CategoryRead] = []
    created_at: datetime
    updated_at: datetime


class ChannelListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    slug: str
    logo_url: str | None = None
    country: CountryRead | None = None
    categories: list[CategoryRead] = []