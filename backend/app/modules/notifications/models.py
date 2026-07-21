from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Notification(Base):
    """Notification in-app du panel, livrée par polling puis SSE (ADR-0016,
    qui remplace le polling de l'ADR-0010)."""

    __tablename__ = "notification"
    __table_args__ = (Index("ix_notification_user_id_created_at", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(255))
    resource: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[int | None] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
