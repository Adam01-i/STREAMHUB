import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    uuid: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime