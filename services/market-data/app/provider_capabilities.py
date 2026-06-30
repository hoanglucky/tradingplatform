from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping

from app.adapters.binance import BINANCE_INTERVALS
from app.adapters.oanda import OANDA_TIMEFRAMES
from app.timeframes import TimeframeValidationError, normalize_timeframe

ProviderName = Literal["oanda", "binance"]
MarketType = Literal["cfd_fx", "spot_crypto"]
DataType = Literal["ohlcv_candles"]
IntendedUse = Literal["primary_market_data", "crypto_development"]


class ProviderCapabilityError(LookupError):
    pass


@dataclass(frozen=True, slots=True)
class ProviderCapability:
    provider: ProviderName
    venue: str
    market_type: MarketType
    data_type: DataType
    intended_use: IntendedUse
    direct_timeframes: frozenset[str]
    read_only: bool = True

    def supports_direct_timeframe(self, timeframe: str) -> bool:
        if not isinstance(timeframe, str):
            return False
        candidate = timeframe.strip()
        if candidate in self.direct_timeframes:
            return True
        try:
            normalized = normalize_timeframe(candidate)
        except TimeframeValidationError:
            return False
        return normalized in self.direct_timeframes


_PROVIDER_CAPABILITIES: dict[ProviderName, ProviderCapability] = {
    "oanda": ProviderCapability(
        provider="oanda",
        venue="oanda",
        market_type="cfd_fx",
        data_type="ohlcv_candles",
        intended_use="primary_market_data",
        direct_timeframes=frozenset(OANDA_TIMEFRAMES),
    ),
    "binance": ProviderCapability(
        provider="binance",
        venue="binance",
        market_type="spot_crypto",
        data_type="ohlcv_candles",
        intended_use="crypto_development",
        direct_timeframes=frozenset(BINANCE_INTERVALS),
    ),
}

PROVIDER_CAPABILITIES: Mapping[ProviderName, ProviderCapability] = MappingProxyType(
    _PROVIDER_CAPABILITIES
)


def get_provider_capability(provider: str) -> ProviderCapability:
    normalized = provider.strip().lower() if isinstance(provider, str) else ""
    try:
        return _PROVIDER_CAPABILITIES[normalized]  # type: ignore[index]
    except KeyError as error:
        raise ProviderCapabilityError(
            f"Unknown market data provider: {provider!r}."
        ) from error


def provider_supports_direct_timeframe(provider: str, timeframe: str) -> bool:
    return get_provider_capability(provider).supports_direct_timeframe(timeframe)


def provider_requires_aggregation(provider: str, timeframe: str) -> bool:
    return not provider_supports_direct_timeframe(provider, timeframe)
