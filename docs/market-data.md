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

## Market Candles API

Day 13 adds:

```txt
GET /market/candles
```

Query parameters:

- `symbol`
- `timeframe`
- `start`
- `end`

Example:

```bash
curl "http://localhost:8101/market/candles?symbol=BTCUSDT&timeframe=1m&start=2024-06-19T08:00:00Z&end=2024-06-19T09:00:00Z"
```

Provider routing:

- `XAUUSD`, `SP500`, and `US100` use Oanda.
- Other symbols currently use Binance.

Oanda requests return `503` when `OANDA_API_TOKEN` is not configured. Provider validation errors return `400`, while upstream provider failures return `502`.

Start the market-data service locally:

```bash
docker compose --profile services up --build market-data
```

The service is exposed at `http://localhost:8101`.

## Candle Storage

Day 14 adds PostgreSQL candle caching behind `GET /market/candles`.

Flow:

1. Resolve the requested symbol from the `symbols` table.
2. Read cached candles for symbol, timeframe, and requested range.
3. Return the cached rows without calling a provider when the range is covered.
4. Fetch the requested range from Binance or Oanda when cache coverage is incomplete.
5. Upsert provider candles using `symbol_id + timeframe + timestamp`.
6. Return the normalized rows from PostgreSQL.

The database unique constraint prevents duplicate candles. Existing candle values are updated when a provider returns a corrected candle for the same timestamp.

Run migrations and market-data tests:

```bash
npm run market-data-test
```

This command now builds the API and market-data images, applies Alembic migrations, and runs both unit and PostgreSQL integration tests for market data.
