from datetime import date

from pydantic import BaseModel, field_validator


class ExternalCountry(BaseModel):
    name: str
    code: str
    languages: list[str] = []
    flag: str | None = None


class ExternalLanguage(BaseModel):
    name: str
    code: str


class ExternalCategory(BaseModel):
    id: str
    name: str
    description: str | None = None


class ExternalChannel(BaseModel):
    id: str
    name: str
    alt_names: list[str] = []
    network: str | None = None
    owners: list[str] = []
    country: str | None = None
    categories: list[str] = []
    is_nsfw: bool = False
    launched: date | None = None
    closed: date | None = None
    replaced_by: str | None = None
    website: str | None = None

    @field_validator("launched", "closed", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: object) -> object:
        return v or None


class ExternalFeed(BaseModel):
    channel: str
    id: str
    name: str
    alt_names: list[str] = []
    is_main: bool = False
    broadcast_area: list[str] = []
    timezones: list[str] = []
    languages: list[str] = []
    format: str | None = None


class ExternalStream(BaseModel):
    channel: str | None = None
    feed: str | None = None
    title: str | None = None
    url: str
    referrer: str | None = None
    user_agent: str | None = None
    quality: str | None = None
    label: str | None = None


class ExternalBlocklistEntry(BaseModel):
    channel: str
    reason: str
    ref: str | None = None


def parse_countries(raw: list[dict]) -> list[ExternalCountry]:
    return [ExternalCountry.model_validate(item) for item in raw]


def parse_languages(raw: list[dict]) -> list[ExternalLanguage]:
    return [ExternalLanguage.model_validate(item) for item in raw]


def parse_categories(raw: list[dict]) -> list[ExternalCategory]:
    return [ExternalCategory.model_validate(item) for item in raw]


def parse_channels(raw: list[dict]) -> list[ExternalChannel]:
    return [ExternalChannel.model_validate(item) for item in raw]


def parse_feeds(raw: list[dict]) -> list[ExternalFeed]:
    return [ExternalFeed.model_validate(item) for item in raw]


def parse_streams(raw: list[dict]) -> list[ExternalStream]:
    return [ExternalStream.model_validate(item) for item in raw]


def parse_blocklist(raw: list[dict]) -> list[ExternalBlocklistEntry]:
    return [ExternalBlocklistEntry.model_validate(item) for item in raw]
