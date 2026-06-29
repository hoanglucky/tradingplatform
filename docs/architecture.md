# Architecture

## Overview

Trading Framework is a modular, paper-first trading MVP foundation. The web app provides the operator experience, the FastAPI API exposes product-facing contracts, PostgreSQL stores durable state, Redis supports low-latency events and cache data, and each domain service owns one bounded area of trading logic.

Live real-money trading is intentionally out of scope for this scaffold. Exchange adapters are read-only by default, and the provided order endpoint rejects writes.

## Implementation Status

Current scaffold status as of 2026-06-29:

- Monorepo structure has been created.
- Next.js frontend scaffold exists in `apps/web`.
- FastAPI backend scaffold exists in `apps/api`.
- Docker Compose defines PostgreSQL, Redis, API, web, and domain services.
- Each domain service has a minimal FastAPI health/capabilities interface.
- PostgreSQL bootstrap SQL exists in `infra/postgres/init.sql`.
- Redis usage notes exist in `infra/redis/README.md`.
- The exchange adapter service blocks order writes by default.
- SQLAlchemy models and Alembic migrations manage the core PostgreSQL schema.
- The market-data service provides normalized Binance and Oanda candle data.
- Market candles are cached in PostgreSQL with conflict-safe upserts.
- The API exposes a validated market WebSocket backed by Binance public kline streams.

Open architecture work:

- Define durable event schemas.
- Decide whether Redis pub/sub is enough for MVP or if a durable queue is needed.
- Replace MVP identity with authentication and authorization before public or multi-user deployment.

## MVP Identity

The local MVP uses one configured PostgreSQL user resolved through `get_mvp_user`. The dependency performs an idempotent insert by email and is the only identity source intended for watchlist and settings routes until authentication is implemented. `GET /users/me` exposes the resolved local identity for development diagnostics.

The watchlist API resolves that dependency on every request and lazily creates one named watchlist per user. PostgreSQL uniqueness constraints and conflict-safe inserts enforce one watchlist name per user and one occurrence of each symbol per watchlist. API responses join catalog symbol metadata for direct frontend rendering.

MVP user mode is not an authentication system: there are no credentials, sessions, roles, permissions, or tenant boundaries. It must be disabled and replaced with authenticated request identity before public or multi-user deployment.

## Components

| Component | Responsibility |
| --- | --- |
| `apps/web` | Next.js frontend for dashboards, module status, strategy views, backtest results, and paper portfolio screens. |
| `apps/api` | FastAPI backend for authentication-ready API boundaries, orchestration, safety status, and product-facing endpoints. |
| `packages/shared` | Shared TypeScript domain contracts used by frontend packages. |
| `packages/ui` | Shared UI primitives for the web app. |
| `services/market-data` | Selects read-only providers, normalizes candles, exposes `/market/candles`, and caches results in PostgreSQL. |
| `services/indicator-engine` | Computes indicators from normalized market data. |
| `services/strategy-engine` | Evaluates strategies and emits signals for paper trading or backtesting. |
| `services/backtest-engine` | Replays historical data and calculates performance metrics. |
| `services/paper-trading` | Simulates order placement, fills, positions, balances, and PnL. |
| `services/alert-engine` | Routes notifications for signals, failures, and risk events. |
| `services/exchange-adapters` | Provides read-only exchange connectivity until write support is explicitly designed later. |

## Data Flow

1. Exchange adapters fetch read-only market data or account snapshots.
2. Market data normalizes raw exchange payloads and publishes events.
3. Indicator engine consumes market events and publishes indicator updates.
4. Strategy engine consumes market and indicator events, then emits strategy signals.
5. Paper trading consumes signals and simulates orders, fills, positions, and PnL.
6. Backtest engine uses historical candles and strategy definitions to produce repeatable simulation results.
7. Alert engine dispatches notifications for selected signals, risk states, and system failures.
8. API exposes stable product contracts to the Next.js frontend.

## Realtime Market Flow

The Day 21 WebSocket path is intentionally isolated from exchange execution:

1. A client connects to `WS /ws/market` on the API service.
2. The client sends a `subscribe` message with a symbol and supported timeframe.
3. Pydantic validates the message and normalizes the symbol to uppercase.
4. The API acknowledges the active subscription.
5. `MarketStreamHub` creates one Binance public kline connection for each active symbol/timeframe.
6. Binance payloads are validated and normalized into the internal OHLCV candle contract.
7. A bounded queue broadcasts each update to all matching frontend clients.
8. The chart replaces an epoch-matched last candle or appends a strictly newer candle.
9. A symbol/timeframe change closes the frontend socket before opening a new subscription.
10. The API sends heartbeat ids and closes clients that do not return matching pong messages before the stale timeout.
11. Unexpected frontend disconnects retry with bounded exponential backoff; each new socket sends one subscription.
12. The final unsubscribe cancels the upstream task; transient upstream failures trigger bounded exponential-backoff reconnects.

The source uses Binance's market-data-only `data-stream.binance.vision` endpoint. The WebSocket contract has no account, order, or exchange-write capability. Oanda-only symbols require a separate future realtime source.

## Market Data Flow

The market-data request path is:

1. The client calls `GET /market/candles` on port `8101` with symbol, timeframe, start, and end.
2. Provider routing selects Oanda for `XAUUSD`, `SP500`, and `US100`; other symbols currently use Binance.
3. `CandleStorageService` resolves the symbol from PostgreSQL.
4. The candle repository queries the requested symbol/timeframe/range.
5. If cached candles cover the range, they are returned without an external provider call.
6. If cache coverage is incomplete, the selected provider fetches the range.
7. Provider payloads are normalized into the internal `Candle` schema.
8. Candles are deduplicated in memory by timestamp and upserted into PostgreSQL.
9. The service reads the final range from PostgreSQL and returns normalized candles.

### Provider Contract

`MarketDataProvider` defines three async operations:

- `get_symbols()`
- `get_historical_candles(symbol, timeframe, start, end)`
- `get_latest_price(symbol)`

The current implementations are:

- `BinancePublicMarketDataProvider`
- `OandaMarketDataProvider`

Binance uses public market-data endpoints and requires no secret. Oanda candle requests use `OANDA_API_TOKEN` as a Bearer token. Both adapters are read-only.

### Candle Contract

Every provider returns the same internal candle fields:

- `symbol`
- `timeframe`
- timezone-aware `timestamp`
- `open`
- `high`
- `low`
- `close`
- `volume`

OHLC prices must be positive and volume must be zero or greater.

### Candle Deduplication

PostgreSQL enforces one candle per `symbol_id + timeframe + timestamp` through `uq_candles_symbol_timeframe_timestamp`. Upserts update OHLCV values when a provider corrects an existing candle instead of inserting a duplicate row.

## Storage

PostgreSQL is the source of truth for durable entities such as candles, backtest runs, paper orders, positions, strategy definitions, and audit records. Redis is the initial event and cache layer for local development. If the system grows, Redis pub/sub can be replaced or complemented with Kafka, Redpanda, NATS, or another durable event log.

The market-data service reads and writes the shared `symbols` and `candles` tables through `DATABASE_URL`. Alembic migrations remain owned by `apps/api`; local market-data tests apply those migrations before running PostgreSQL integration tests.

## Safety Model

The scaffold uses defense-in-depth defaults:

- `DEFAULT_TRADING_MODE=paper`
- `ENABLE_LIVE_TRADING=false`
- `ENABLE_EXCHANGE_WRITES=false`
- `EXCHANGE_ADAPTER_MODE=read_only`

Exchange write paths must check all safety switches. This repository currently includes no live order placement implementation.

Market-data credentials are scoped to read-only access. `OANDA_API_TOKEN` must not be committed and should be provided through environment configuration or a deployment secret manager.

## Deployment Notes

The Docker Compose setup is intended for local development. A production deployment should add:

- Secrets management instead of `.env` files.
- Database migrations with Alembic.
- TLS termination and authentication.
- Service-level health checks and metrics.
- Centralized logs and traces.
- CI gates for tests, type checks, and container builds.
