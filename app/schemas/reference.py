from pydantic import BaseModel, ConfigDict


class CountryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    flag: str | None = None


class CountryWithCount(CountryRead):
    channel_count: int


class LanguageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str | None = None


class CategoryWithCount(CategoryRead):
    channel_count: int