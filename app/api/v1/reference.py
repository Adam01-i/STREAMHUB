from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.reference_repository import ReferenceRepository
from app.schemas.reference import CategoryWithCount, CountryWithCount, LanguageRead

router = APIRouter(tags=["reference"])


@router.get("/countries", response_model=list[CountryWithCount])
async def list_countries(db: AsyncSession = Depends(get_db)) -> list[CountryWithCount]:
    repo = ReferenceRepository(db)
    pairs = await repo.list_countries_with_counts()
    return [
        CountryWithCount(code=country.code, name=country.name, flag=country.flag, channel_count=count)
        for country, count in pairs
    ]


@router.get("/categories", response_model=list[CategoryWithCount])
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[CategoryWithCount]:
    repo = ReferenceRepository(db)
    pairs = await repo.list_categories_with_counts()
    return [
        CategoryWithCount(id=cat.id, name=cat.name, description=cat.description, channel_count=count)
        for cat, count in pairs
    ]


@router.get("/languages", response_model=list[LanguageRead])
async def list_languages(db: AsyncSession = Depends(get_db)) -> list[LanguageRead]:
    repo = ReferenceRepository(db)
    return await repo.list_languages()
