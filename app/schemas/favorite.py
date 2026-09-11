from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FavoriteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    channel_id: str
    created_at: datetime