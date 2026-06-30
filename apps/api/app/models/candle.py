from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.symbol import Symbol


class Candle(UuidPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "timestamp", name="uq_candles_symbol_timeframe_timestamp"),
        Index("ix_candles_symbol_timeframe_timestamp", "symbol_id", "timeframe", "timestamp"),
    )

    symbol_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("symbols.id", ondelete="CASCADE"),
        nullable=False,
    )
    timeframe: Mapped[str] = mapped_column(String(16), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    open: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    high: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    low: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    close: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    volume: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False)
    partial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    source_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_source_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    missing_source_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    symbol: Mapped["Symbol"] = relationship(back_populates="candles")
