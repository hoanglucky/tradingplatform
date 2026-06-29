from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    default_symbol: Mapped[str] = mapped_column(
        String(40), default="BTCUSDT", server_default="BTCUSDT", nullable=False
    )
    default_timeframe: Mapped[str] = mapped_column(
        String(16), default="15m", server_default="15m", nullable=False
    )
    selected_indicators: Mapped[list[str]] = mapped_column(
        JSONB, default=list, server_default=text("'[]'::jsonb"), nullable=False
    )
    theme: Mapped[str] = mapped_column(
        String(16), default="system", server_default="system", nullable=False
    )
    timezone: Mapped[str] = mapped_column(
        String(64), default="UTC", server_default="UTC", nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="settings")
