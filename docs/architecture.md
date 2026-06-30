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
- The API exposes a validated market WebSocket backed by Binance streams and Oanda read-only candle updates.

Open architecture work:

- Define durable event schemas.
- Decide whether Redis pub/sub is enough for MVP or if a durable queue is needed.
- Replace MVP identity with authentication and authorization before public or multi-user deployment.

## MVP Identity

The local MVP uses one configured PostgreSQL user resolved through `get_mvp_user`. The dependency performs an idempotent insert by email and is the only identity source intended for watchlist and settings routes until authentication is implemented. `GET /users/me` exposes the resolved local identity for development diagnostics.

The watchlist API resolves that dependency on every request and lazily creates one named watchlist per user. PostgreSQL uniqueness constraints and conflict-safe inserts enforce one watchlist name per user and one occurrence of each symbol per watchlist. API responses join catalog symbol metadata for direct frontend rendering.

The dashboard and chart watchlist panels call the API directly from the browser, refresh after mutations, and only offer active unpinned symbols. A symbol link passes the market through the chart query string; the chart validates supported symbols before initializing state. Binance and Oanda chart symbols both receive realtime WebSocket candle updates.

User settings are also owned by the MVP user through a one-to-one `user_settings` row. `GET /settings` lazily creates defaults and `PATCH /settings` validates and persists symbol, timeframe, indicators, theme, and IANA timezone preferences.

The chart waits for its initial settings read before requesting candles. The stored symbol initializes the workspace; a valid symbol query from the watchlist takes precedence and is persisted. The legacy default timeframe remains compatible in settings, while visible chart timeframes come from the persisted multi-timeframe layout. Subsequent selection writes use a serialized client queue so rapid changes cannot be overwritten by an older request finishing later.

The chart owns one multi-timeframe review model with one shared symbol, 1/2/4/8 window-count presets, and independent timeframe/enabled/review state per window. The selected count is the complete chart surface: no additional legacy chart is rendered below it.

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
5. `MarketStreamHub` routes Binance symbols to public kline streams and `XAUUSD`, `SP500`, and `US100` to Oanda.
6. Oanda fetches the current read-only candle every `OANDA_REALTIME_POLL_SECONDS`; both provider payloads normalize into the same OHLCV contract.
7. A bounded queue broadcasts each update to all matching frontend clients.
8. The chart replaces an epoch-matched last candle or appends a strictly newer candle.
9. The multi-window workspace opens one connection per unique visible timeframe; duplicate timeframe windows share the same update.
10. The API sends heartbeat ids and closes clients that do not return matching pong messages before the stale timeout.
11. Unexpected frontend disconnects retry independently with bounded exponential backoff; each new socket sends one subscription.
12. The final unsubscribe cancels the upstream task; transient upstream failures trigger bounded exponential-backoff reconnects.

The Binance source uses the market-data-only `data-stream.binance.vision` endpoint. The Oanda account pricing stream currently returns `403` for the configured practice account, so realtime Oanda candles use the account-independent instrument endpoint that the token can read. The WebSocket contract has no account mutation, order, or exchange-write capability.

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

For long chart ranges, adapters paginate before storage: Oanda splits requests below its 5000-candle limit and Binance advances through 1000-kline pages. The chart exposes fixed 1-day, 1-week, and 1-month windows; Oanda markets default to one month.

Cache coverage uses one timeframe duration at the requested trailing edge, ensuring stale higher-timeframe rows cannot suppress a provider refresh. Oanda receives a wider tolerance only at the leading edge so requests beginning during the weekend can still reuse the first candle after market open. Daily maintenance breaks and weekend closures remain legitimate gaps in returned Oanda series.

The multi-timeframe review UI supports 1m, 5m, 15m, 30m, 1h, 2h, 4h, and 1d presets. These remain direct provider timeframe requests; Oanda maps 2h to H2. Custom resampling and candle aggregation are deferred to Day 30.10 and later.

Reviewed checkboxes are manual workflow state. Progress is calculated only from visible enabled windows, while Clear review resets the whole layout. Neither action publishes a signal, invokes a strategy, or creates a paper order.

Multi-timeframe layouts persist in nullable JSONB on the one-to-one user settings row. Backend Pydantic schemas enforce the nested contract, while the frontend validates untrusted saved JSON again and falls back to a fresh four-window layout when necessary. Layout mutations share the serialized settings write queue used by chart preferences.

Each enabled review window loads its own recent 120-candle range through the normalized frontend candles client. Window components isolate candle, loading, error, and abort state, then render the existing `CandlestickChart`. A workspace-level realtime manager subscribes once per unique visible timeframe and routes normalized candles to matching windows. The latest received quote synchronizes the active candle close/high/low across all visible charts while each chart retains its own bucket timestamp and historical series. Provider-native 30m and 2h streams map to Oanda M30 and H2; this stage does not aggregate or synthesize historical candles.

Each `CandlestickChart` owns its viewport controls. Right-clicking a loaded canvas suppresses the browser context menu, fits the loaded time range, and restores automatic right-price-axis scaling for that chart only. This reset changes presentation state without fetching data, reconnecting streams, or modifying settings.

Provider candle timestamps remain timezone-aware UTC opening instants in transport, storage, and Lightweight Charts coordinates. Time-axis ticks and crosshair labels format that opening instant using the persisted IANA chart timezone, currently selectable between UTC and Asia/Bangkok. A closing instant may be derived by adding the timeframe duration, but it does not shift the candle coordinate; this matches TradingView's convention where a 5m candle opened at 14:55 is selected as 14:55 rather than 15:00.

Custom timeframe work begins with pure parser and aggregation utilities in the market-data service. The parser canonicalizes positive integer minute/hour/day strings and exposes duration milliseconds without knowing providers, storage, or HTTP. `CandleAggregator` sorts source candles and groups them into Unix-epoch-aligned UTC buckets, producing deterministic OHLCV values with the bucket start as the timestamp. It requires one symbol, one source timeframe, and an exact target/source duration multiple.

Aggregated output uses an `AggregatedCandle` contract with complementary `closed` and `partial` flags. Bucket state is deterministic against a timezone-aware evaluation instant: a bucket is closed when its UTC end is at or before that instant. Chart consumers can retain the active partial candle, while backtest/replay consumers call the same utility with partial output excluded. Provider capability routing, API acceptance, persistence, and cache integration remain separate later stages, so existing `/market/candles` behavior is unchanged.

Direct timeframe support is described by an immutable capability registry built from each adapter's own constants. Oanda is the primary read-only CFD/FX candle source, while Binance public is a read-only spot-crypto development source. Every entry carries provider, venue, market type, data type, intended use, direct timeframes, and safety state. Capability lookup can distinguish a direct interval from a valid custom interval that needs aggregation without making an upstream request.

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
