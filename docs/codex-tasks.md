# Codex Tasks

Use this file to track task-level handoff notes for Codex sessions.

## Global rules

- One main task per session.
- Keep the MVP paper-first.
- Do not implement real-money live trading.
- Exchange integration must remain read-only unless a later task explicitly changes the safety design.
- Add tests or a clear verification path.
- Update docs after meaningful changes.
- Do not hardcode secrets.

## Completed

### 2026-06-18 - Day 1 foundation

Implemented:

- Monorepo scaffold
- Next.js web app
- FastAPI API app
- Docker Compose stack
- PostgreSQL and Redis local infrastructure
- Shared TypeScript packages
- Modular service stubs
- README, `.env.example`, Makefile, architecture docs

Verified:

- `npm run lint`
- `npm run typecheck`
- `npm --workspace apps/web run build`
- `npm --workspace apps/web run dev`
- HTTP 200 checks for `/`, `/markets`, and `/settings`
- `docker compose config --quiet` after creating `.env` from `.env.example`

Not verified:

- Backend pytest on host due missing Python `pip`/`venv`.

### 2026-06-18 - Day 2 backend skeleton hardening

Implemented:

- Aligned API folders with planned structure:
  - `app/api/routes`
  - `app/api/router.py`
  - `app/core/logging.py`
- Added structured logging setup.
- Added `/health/ready` for PostgreSQL and Redis readiness checks.
- Added API endpoint documentation in `docs/api.md`.
- Added tests for health, readiness, and safety defaults.

Verified:

- `npm run lint`
- `npm run typecheck`
- `python3 -m compileall -q apps/api/app`

Pending verification:

- Host Python pytest remains unavailable because host Python lacks `pip`/`venv`.

## Next task candidate

### 2026-06-18 - Day 3 frontend skeleton hardening

Implemented:

- Stable dashboard layout with sidebar and topbar.
- API health/readiness display.
- Safety status display with exchange writes blocked.
- Empty dashboard states for chart/watchlist/signal areas.
- Placeholder App Router pages for MVP sections.
- Shared frontend contracts for health and readiness.

Verified:

- `npm run lint`
- `npm run typecheck`
- `npm --workspace apps/web run build`

### 2026-06-18 - Day 4 Docker Compose setup hardening

Implemented:

- Added `.dockerignore` files for root, API, and service build contexts.
- Added API and web health checks to `docker-compose.yml`.
- Made web depend on API service health.
- Moved domain service stubs behind the Compose `services` profile.
- Updated the API Dockerfile to include tests and set `PYTHONPATH=/app`.
- Added `docs/docker.md` with Compose usage, health checks, verification commands, and Docker credential troubleshooting.
- Updated README and task docs.

Verified:

- `docker compose config --quiet`
- `docker pull python:3.12-slim`
- PostgreSQL and Redis containers started during `docker compose run --build --rm api pytest`
- `docker compose build api`
- `docker compose run --rm api pytest` passed with 4 tests

Pending verification:

- None for Day 4 core stack.

## Next task candidate

### 2026-06-18 - Day 6 database foundation

Implemented:

- Added SQLAlchemy async engine/session utilities.
- Added shared SQLAlchemy declarative base.
- Added Alembic configuration and async migration environment.
- Added first empty migration.
- Added Docker-backed migration commands.
- Added database documentation.

Verified:

- `npm run db:upgrade`
- `npm run db:current`
- `npm run api-test`
- Backend `/health` through Docker Compose

### 2026-06-19 - Day 7 core database models

Implemented:

- Added SQLAlchemy models for users, symbols, candles, watchlists, and watchlist items.
- Added Alembic migration `20260619_0002_core_tables`.
- Added model metadata tests.
- Updated database documentation.

Verified:

- `npm run lint:api`
- `npm run db:upgrade`
- `npm run db:current`
- `npm run api-test`
- PostgreSQL `\\dt` shows core tables.
- PostgreSQL `\\di` shows candle index and unique constraints.
- `npm run web-test`

## Next task candidate

### Day 28 - Watchlist frontend

Suggested scope:

- Add a dashboard watchlist panel backed by `GET /watchlist`.
- Add symbol selection, add action, and remove controls.
- Show loading, empty, and error states and refresh after mutations.

## Recently completed

### Day 27 - Watchlist API

Implemented:

- Added GET, add-item, and delete-item watchlist endpoints.
- Reused the Day 26 MVP user dependency for ownership.
- Added lazy conflict-safe default watchlist creation.
- Added active symbol validation and uppercase normalization.
- Added conflict-safe item insertion with duplicate `409` responses.
- Added joined symbol metadata in list responses.

Verified:

- `npm run lint:api` passes.
- `npm run api-test` passes all 33 backend tests.
- Live CRUD smoke test returns GET 200, add 201, duplicate 409, and delete 204.

### Day 26 - Mock user mode

Implemented:

- Added configurable single-user MVP identity settings.
- Added conflict-safe, idempotent PostgreSQL user creation.
- Added reusable `get_mvp_user` dependency for watchlist and settings routes.
- Added `GET /users/me` with explicit `mvp_local` mode.
- Added a disabled-mode failure path instead of pretending authentication exists.

Verified:

- `npm run lint:api` passes.
- `npm run api-test` passes all 27 backend tests.
- `npm run web-test` passes.
- Two live `/users/me` requests return HTTP 200 and the same UUID.

### Day 25 - Realtime tests

Implemented:

- Added independent tests for updating an existing candle and appending a new candle.
- Added stale older-candle and duplicate-timestamp regression coverage.
- Added empty-chart initialization coverage.
- Confirmed merge operations do not mutate historical input candles.
- Retained validation, reconnect-backoff, and heartbeat-pong coverage.

Verified:

- Nine frontend market-stream tests pass.
- `npm run web-test` passes lint, tests, typecheck, and production build.

### Day 24 - Reconnect and heartbeat

Implemented:

- Added frontend reconnect with bounded exponential backoff.
- Added one-subscription-per-socket guards and idempotent backend subscriptions.
- Added application heartbeat and matching pong contracts.
- Added stale-client close and subscription cleanup.
- Added clear realtime, connecting, retrying, upstream reconnecting, unavailable, and historical-only UI states.
- Added configurable frontend retry and backend heartbeat/stale intervals.

Verified:

- Six frontend market-stream tests pass.
- `npm run web-test` passes lint, tests, typecheck, and production build.
- `npm run lint:api` passes.
- `npm run api-test` passes all 23 backend tests.
- Live smoke test receives a Binance candle, heartbeat, and sends pong successfully.

### Day 23 - Frontend WebSocket subscription

Implemented:

- Connected Binance chart selections to `WS /ws/market` after historical loading.
- Added strict realtime candle normalization and OHLCV validation.
- Updated matching epochs and appended only strictly newer candles.
- Added stale-message guards and socket cleanup for selection, refresh, and unmount.
- Kept Oanda-only selections on historical HTTP data.
- Kept the Lightweight Charts instance stable while realtime data changes.

Verified:

- Four frontend market-stream tests pass.
- `npm run web-test` passes lint, tests, typecheck, and production build.
- Web, API, and market-data health requests return HTTP 200.
- Live WebSocket smoke test receives a real Binance BTCUSDT candle.

### Day 22 - Real market stream service

Implemented:

- Added a read-only Binance public kline WebSocket source.
- Added strict Binance payload normalization into the internal candle schema.
- Added one shared upstream task per active symbol/timeframe.
- Added bounded per-client queues and broadcast fan-out.
- Added disconnect cleanup, reconnect status events, and exponential backoff.
- Replaced Day 21 mock events with `source=binance`, `mock=false` updates.

Verified:

- `npm run lint:api`
- `npm run api-test` with 20 passing tests.
- Live Docker WebSocket smoke test received a real BTCUSDT candle from Binance.

### Day 21 - Backend WebSocket endpoint

Implemented:

- Added `WS /ws/market` to the FastAPI router.
- Added validated subscribe, acknowledgement, candle, and error schemas.
- Added uppercase symbol normalization and six supported timeframes.
- Added configurable periodic mock OHLCV updates.
- Supported resubscription and invalid-message recovery on an open connection.

Verified:

- `npm run lint:api`
- `npm run api-test` with 14 passing tests.
- Live Docker WebSocket handshake returned an acknowledgement and mock candle.

### Day 20 - Chart UI polish

Implemented:

- Added a manual candle refresh action with disabled and loading states.
- Added latest-close, period-change, live-status, and last-updated feedback.
- Kept current candles visible while a manual refresh is in progress.
- Improved chart controls for tablet and mobile widths.
- Added a Lucide refresh icon with accessible label and tooltip.

Verified:

- `npm run web-test`
- Production build includes `/dashboard/chart`.

### Day 19 - Connect chart to backend

Implemented:

- Connected `ChartWorkspace` to `GET /market/candles`.
- Refetched data when symbol or timeframe changes.
- Added 120-bar timeframe-aligned request ranges.
- Added AbortController cleanup for stale requests.
- Added API candle validation and numeric normalization.
- Connected loading, error, candles, latest close, and percentage change to backend state.

Verified:

- `npm run web-test`
- Market-data BTCUSDT 15m request returned HTTP 200 with real candles.

### Day 18 - Symbol and timeframe selectors

Implemented:

- Added client-side `ChartWorkspace` state.
- Added symbol selector with Binance and Oanda mock markets.
- Added segmented timeframe selector for 1m, 5m, 15m, 1h, 4h, and 1d.
- Defaulted to BTCUSDT and 15m.
- Regenerated mock candles, latest price, percentage change, and headings when state changes.

Verified:

- `npm run web-test`
- `GET /dashboard/chart` returned HTTP 200.
- Initial HTML contained BTCUSDT, 15m, and symbol options.

### Day 17 - CandlestickChart component

Implemented:

- Added reusable `CandlestickChart` component.
- Added candles, symbol, timeframe, height, loading, and error props.
- Added sorted ISO timestamp conversion for Lightweight Charts.
- Added loading, error, and empty states.
- Preserved auto resize and cleanup behavior.
- Moved mock candle data into the chart page.

Verified:

- `npm run web-test`
- Next.js build included `/dashboard/chart`.

### Day 16 - Install chart library

Implemented:

- Installed `lightweight-charts` 5.2.0 in `apps/web`.
- Added `/dashboard/chart` and sidebar navigation.
- Added a stable responsive chart workspace.
- Rendered mock BTCUSDT candlesticks with no API connection.
- Added TradingView attribution.

Verified:

- `npm run web-test`
- `GET /dashboard/chart` returned HTTP 200.
- Server HTML included BTCUSDT, mock status, and TradingView attribution.

### Day 15 - Market data docs

Implemented:

- Documented the complete provider, normalization, cache, and response flow.
- Documented Binance and Oanda selection and configuration.
- Documented the internal Candle schema.
- Documented `/market/candles` requests, responses, errors, and examples.
- Documented PostgreSQL upsert and deduplication behavior.

Verified:

- `docs/architecture.md` updated.
- `docs/api.md` updated.

### Day 14 - Candle storage

Implemented:

- Added PostgreSQL session support to the market-data service.
- Added candle repository queries and PostgreSQL upsert.
- Added `CandleStorageService` for cache/provider orchestration.
- Updated `/market/candles` to return cache data and persist provider results.
- Added cache, deduplication, unknown-symbol, and PostgreSQL integration tests.
- Updated market-data tests to apply Alembic migrations first.

Verified:

- `python3 -m compileall -q services/market-data/app services/market-data/tests`
- `npm run market-data-test`

### Day 13 - Market candles API

Implemented:

- Added `GET /market/candles` to the market-data service.
- Added symbol, timeframe, start, and end query parameters.
- Added provider routing for Binance and Oanda.
- Added clean HTTP error mapping for validation, configuration, and upstream failures.
- Exposed the market-data service on port `8101`.
- Added mocked endpoint tests.

Verified:

- `python3 -m compileall -q services/market-data/app services/market-data/tests`
- `npm run market-data-test`

### Day 12 - Binance and Oanda market-data adapters

Implemented:

- Added `BinancePublicMarketDataProvider`.
- Added `OandaMarketDataProvider`.
- Added public `exchangeInfo`, `klines`, and `ticker/price` requests.
- Added Oanda read-only candle requests using `OANDA_API_TOKEN`.
- Converted Binance kline rows into internal `Candle` schemas.
- Converted Oanda candle rows into internal `Candle` schemas.
- Added validation for symbol, timeframe, and time range.
- Added adapter error wrapping for Binance and Oanda API and HTTP errors.
- Added mocked HTTP tests for both adapters.
- Added `docs/market-data.md`.

Verified:

- `python3 -m compileall -q services/market-data/app services/market-data/tests`
- `npm run market-data-test`

### Day 11 - MarketDataProvider interface

Implemented:

- Added market-data `Candle`, `MarketSymbol`, and `LatestPrice` schemas.
- Added `MarketDataProvider` protocol with `get_symbols`, `get_historical_candles`, and `get_latest_price`.
- Added market-data schema validation tests.
- Added `make market-data-test` and `npm run market-data-test`.
- Updated shared TypeScript `Candle` type to use `timestamp`.

Verified:

- `python3 -m compileall -q services/market-data/app services/market-data/tests`
- `npm run market-data-test`

### Day 10 - Seed initial symbols

Implemented:

- Added idempotent default symbol seed logic.
- Added CLI command `python -m app.cli.seed_symbols`.
- Added `make seed` and `npm run seed`.
- Added backend seed tests.
- Seed data includes BTCUSDT, ETHUSDT, SOLUSDT, BNBUSDT, XRPUSDT, XAUUSD, SP500, and US100.

Verified:

- `python3 -m compileall -q apps/api/app apps/api/tests`
- `npm run lint:api`
- `npm run api-test`
- `npm run seed`
- `GET /symbols?active_only=true` returned the seeded symbols.

### Day 9 - Symbol API

Implemented:

- Added Pydantic schemas for symbol create/update/read.
- Added `/symbols` FastAPI routes for list, create, read, update, and delete.
- Added duplicate symbol handling with `409 Conflict`.
- Added OpenAPI coverage test for symbol paths.
- Updated API test command to run with `APP_ENV=test` and avoid asyncpg event-loop reuse in pytest.

Verified:

- `python3 -m compileall -q apps/api/app apps/api/tests`
- `npm run lint:api`
- `npm run api-test`

### Day 8 - Repository layer

Implemented:

- Added repositories for users, symbols, candles, watchlists, and watchlist items.
- Added shared async CRUD behavior in `BaseRepository`.
- Added symbol repository tests.
- Updated backend test command to apply Alembic migrations before pytest.

Verified:

- `python3 -m compileall -q apps/api/app apps/api/tests`
- `npm run lint:api`
- `npm run api-test`
- `npm run web-test`
 
### 2026-06-18 - Day 5 developer commands polish

Implemented:

- Added `make up`.
- Added `make api-test`.
- Added `make web-test`.
- Updated `make test` to run both API and web checks.
- Updated `make lint` and `make format` to use the API Docker image for backend Python tooling.
- Added npm fallback commands for environments without `make`.
- Updated README command usage.

Verified:

- `make` commands cannot be executed in this environment because `make` is not installed.
- `npm run api-test`
- `npm run web-test`
- `npm run lint:api`
- `npm test`
