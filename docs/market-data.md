# Market Data

## Overview

The market-data service normalizes external public market data into internal schemas.

Current contracts live in `services/market-data/app`:

- `schemas.py`
- `providers.py`
- `adapters/binance.py`
- `adapters/oanda.py`

## Provider Interface

`MarketDataProvider` defines:

- `get_symbols()`
- `get_historical_candles(symbol, timeframe, start, end)`
- `get_latest_price(symbol)`

## Candle Schema

Normalized candles use:

- `symbol`
- `timeframe`
- `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

Timestamps must be timezone-aware. OHLC prices must be positive. Volume must be zero or greater.

## Binance Public Adapter

Day 12 adds `BinancePublicMarketDataProvider`.

Supported public endpoints:

- `GET /api/v3/exchangeInfo`
- `GET /api/v3/klines`
- `GET /api/v3/ticker/price`

The adapter uses only Binance public market-data endpoints. It does not use API keys, signed requests, account endpoints, order endpoints, or live trading behavior.

## Oanda Read-Only Adapter

Day 12 also adds `OandaMarketDataProvider` for read-only candle data.

Environment variables:

```env
OANDA_API_TOKEN=
OANDA_ACCOUNT_ID=
OANDA_ENVIRONMENT=practice
```

`OANDA_API_TOKEN` is required for Oanda HTTP requests. `OANDA_ENVIRONMENT` can be `practice` or `live`; use `practice` for development. `OANDA_ACCOUNT_ID` is optional for candle requests, but enables account instrument discovery.

Supported read-only endpoint:

- `GET /v3/instruments/{instrument}/candles`

Optional instrument discovery endpoint when `OANDA_ACCOUNT_ID` is configured:

- `GET /v3/accounts/{accountID}/instruments`

Symbol mapping currently includes:

- `XAUUSD` -> `XAU_USD`
- `SP500` -> `SPX500_USD`
- `US100` -> `NAS100_USD`

The adapter sends the token as an `Authorization: Bearer ...` header, per Oanda v20 authentication. It does not place, modify, or close orders.

## Tests

Run market-data tests:

```bash
npm run market-data-test
```

The Binance and Oanda adapter tests use mocked HTTP responses and do not call external APIs over the network.
