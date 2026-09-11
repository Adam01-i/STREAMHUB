from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Country(Base):
    __tablename__ = "countries"

    code: Mapped[str] = mapped_column(String(2), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    flag: Mapped[str | None] = mapped_column(String(16), nullable=True)


class Language(Base):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)