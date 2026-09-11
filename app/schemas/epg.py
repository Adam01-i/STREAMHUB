from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProgramRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    channel_id: str
    title: str
    description: str | None = None
    category: str | None = None
    start_time: datetime
    end_time: datetime
    image_url: str | None = None