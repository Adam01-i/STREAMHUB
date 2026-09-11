from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import StreamStatus


class StreamRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_id: str | None = None
    feed_id: int | None = None
    title: str | None = None
    url: str
    referrer: str | None = None
    user_agent: str | None = None
    quality: str | None = None
    label: str | None = None
    status: StreamStatus
    response_time_ms: int | None = None
    last_checked_at: datetime | None = None