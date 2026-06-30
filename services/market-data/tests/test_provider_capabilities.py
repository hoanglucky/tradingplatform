from __future__ import annotations

import pytest

from app.adapters.binance import BINANCE_INTERVALS
from app.adapters.oanda import OANDA_TIMEFRAMES
from app.provider_capabilities import (
    PROVIDER_CAPABILITIES,
    ProviderCapabilityError,
    get_provider_capability,
    provider_requires_aggregation,
    provider_supports_direct_timeframe,
)


def test_oanda_capability_exposes_primary_read_only_metadata() -> None:
    capability = get_provider_capability(" OANDA ")

    assert capability.provider == "oanda"
    assert capability.venue == "oanda"
    assert capability.market_type == "cfd_fx"
    assert capability.data_type == "ohlcv_candles"
    assert capability.intended_use == "primary_market_data"
    assert capability.read_only is True
    assert capability.direct_timeframes == frozenset(OANDA_TIMEFRAMES)


def test_binance_capability_is_limited_to_crypto_development() -> None:
    capability = get_provider_capability("binance")

    assert capability.market_type == "spot_crypto"
    assert capability.intended_use == "crypto_development"
    assert capability.read_only is True
    assert capability.direct_timeframes == frozenset(BINANCE_INTERVALS)


@pytest.mark.parametrize(
    ("provider", "timeframe"),
    [
        ("oanda", "1m"),
        ("oanda", " 2H "),
        ("oanda", "1d"),
        ("binance", "3m"),
        ("binance", "12h"),
        ("binance", "1M"),
    ],
)
def test_detects_direct_provider_timeframes(provider: str, timeframe: str) -> None:
    assert provider_supports_direct_timeframe(provider, timeframe) is True
    assert provider_requires_aggregation(provider, timeframe) is False


@pytest.mark.parametrize("timeframe", ["6m", "7m", "45m", "3h"])
def test_oanda_custom_timeframes_require_aggregation(timeframe: str) -> None:
    assert provider_supports_direct_timeframe("oanda", timeframe) is False
    assert provider_requires_aggregation("oanda", timeframe) is True


@pytest.mark.parametrize("timeframe", ["", "0m", "abc", "1x"])
def test_invalid_timeframes_are_not_direct(timeframe: str) -> None:
    assert provider_supports_direct_timeframe("oanda", timeframe) is False


def test_unknown_provider_fails_clearly() -> None:
    with pytest.raises(ProviderCapabilityError, match="Unknown market data provider"):
        get_provider_capability("unknown")


def test_capability_registry_is_read_only() -> None:
    with pytest.raises(TypeError):
        PROVIDER_CAPABILITIES["oanda"] = get_provider_capability("oanda")  # type: ignore[index]
