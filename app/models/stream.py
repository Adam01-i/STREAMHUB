from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import StreamStatus


class Stream(Base):
    __tablename__ = "streams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[str | None] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), nullable=True, index=True
    )
    feed_id: Mapped[int | None] = mapped_column(ForeignKey("feeds.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality: Mapped[str | None] = mapped_column(String(32), nullable=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[StreamStatus] = mapped_column(default=StreamStatus.UNKNOWN, index=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    channel: Mapped["Channel"] = relationship(back_populates="streams")
    feed: Mapped["Feed"] = relationship(back_populates="streams")