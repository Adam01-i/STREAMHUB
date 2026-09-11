from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_id: str
    started_at: datetime
    duration_seconds: int | None = None