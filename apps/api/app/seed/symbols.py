from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.symbols import SymbolRepository


class SymbolSeed(TypedDict):
    exchange: str
    symbol: str
    base_asset: str
    quote_asset: str
    is_active: bool


@dataclass(frozen=True)
class SeedResult:
    created: int
    updated: int
    skipped: int


DEFAULT_SYMBOLS: tuple[SymbolSeed, ...] = (
    {
        "exchange": "binance",
        "symbol": "BTCUSDT",
        "base_asset": "BTC",
        "quote_asset": "USDT",
        "is_active": True,
    },
    {
        "exchange": "binance",
        "symbol": "ETHUSDT",
        "base_asset": "ETH",
        "quote_asset": "USDT",
        "is_active": True,
    },
    {
        "exchange": "binance",
        "symbol": "SOLUSDT",
        "base_asset": "SOL",
        "quote_asset": "USDT",
        "is_active": True,
    },
    {
        "exchange": "binance",
        "symbol": "BNBUSDT",
        "base_asset": "BNB",
        "quote_asset": "USDT",
        "is_active": True,
    },
    {
        "exchange": "binance",
        "symbol": "XRPUSDT",
        "base_asset": "XRP",
        "quote_asset": "USDT",
        "is_active": True,
    },
    {
        "exchange": "oanda",
        "symbol": "XAUUSD",
        "base_asset": "XAU",
        "quote_asset": "USD",
        "is_active": True,
    },
    {
        "exchange": "oanda",
        "symbol": "SP500",
        "base_asset": "SP500",
        "quote_asset": "USD",
        "is_active": True,
    },
    {
        "exchange": "oanda",
        "symbol": "US100",
        "base_asset": "US100",
        "quote_asset": "USD",
        "is_active": True,
    },
)


async def seed_symbols(session: AsyncSession) -> SeedResult:
    repo = SymbolRepository(session)
    created = 0
    updated = 0
    skipped = 0

    for symbol_data in DEFAULT_SYMBOLS:
        existing = await repo.get_by_symbol(
            symbol_data["exchange"], symbol_data["symbol"]
        )
        if existing is None:
            await repo.create(**symbol_data)
            created += 1
            continue

        changes = {
            key: value
            for key, value in symbol_data.items()
            if key not in {"exchange", "symbol"} and getattr(existing, key) != value
        }
        if changes:
            await repo.update(existing.id, **changes)
            updated += 1
        else:
            skipped += 1

    return SeedResult(created=created, updated=updated, skipped=skipped)
