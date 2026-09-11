from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import ReportStatus, ReportType


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[str | None] = mapped_column(ForeignKey("channels.id", ondelete="SET NULL"), nullable=True)
    stream_id: Mapped[int | None] = mapped_column(ForeignKey("streams.id", ondelete="SET NULL"), nullable=True)

    type: Mapped[ReportType] = mapped_column(nullable=False)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(default=ReportStatus.OPEN)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())