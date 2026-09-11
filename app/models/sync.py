from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import SyncStatus


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[SyncStatus] = mapped_column(default=SyncStatus.RUNNING)

    channels_imported: Mapped[int] = mapped_column(Integer, default=0)
    channels_updated: Mapped[int] = mapped_column(Integer, default=0)
    streams_imported: Mapped[int] = mapped_column(Integer, default=0)

    report_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)