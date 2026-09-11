import uuid as uuid_module
from datetime import date, datetime

from sqlalchemy import ARRAY, Boolean, Date, DateTime, ForeignKey, String, Table, Column, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import SourceStatus

channel_categories = Table(
    "channel_categories",
    Base.metadata,
    Column("channel_id", String(128), ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", String(64), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)  # id iptv-org, ex: "RTS1.sn"
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), unique=True, default=uuid_module.uuid4)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    alt_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    network: Mapped[str | None] = mapped_column(String(255), nullable=True)
    owners: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    country_code: Mapped[str | None] = mapped_column(ForeignKey("countries.code"), nullable=True, index=True)

    logo_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    website: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    is_nsfw: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    source_status: Mapped[SourceStatus] = mapped_column(default=SourceStatus.ACTIVE)

    launched: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed: Mapped[date | None] = mapped_column(Date, nullable=True)
    replaced_by: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    country: Mapped["Country"] = relationship(lazy="joined")
    categories: Mapped[list["Category"]] = relationship(secondary=channel_categories, lazy="selectin")
    feeds: Mapped[list["Feed"]] = relationship(back_populates="channel", cascade="all, delete-orphan")
    streams: Mapped[list["Stream"]] = relationship(back_populates="channel", cascade="all, delete-orphan")


class Feed(Base):
    __tablename__ = "feeds"
    __table_args__ = (
        # un feed_code est unique par chaîne
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    feed_code: Mapped[str] = mapped_column(String(128), nullable=False)  # "id" côté iptv-org

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alt_names: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False)

    broadcast_area: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    timezones: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    languages: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    format: Mapped[str | None] = mapped_column(String(32), nullable=True)

    channel: Mapped["Channel"] = relationship(back_populates="feeds")
    streams: Mapped[list["Stream"]] = relationship(back_populates="feed")