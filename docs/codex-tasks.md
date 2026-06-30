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

### 2026-06-30 - Day 30.9.6 realtime candle open continuity repair

Implemented:

- Removed cross-timeframe price mutation from live OHLC.
- Retained consecutive realtime candles per symbol/timeframe.
- Reconciled contiguous candle opens with previous closes without masking real market gaps.

Verified:

- 55 frontend tests, lint, typecheck, and production build pass.

### 2026-06-30 - Days 30.14–30.18 custom timeframe favorites

Implemented:

- Provider-direct and cached aggregate candle paths for safe custom timeframes.
- Week and calendar-month timeframe parsing and aggregation.
- Custom timeframe API validation and chart-layout persistence.
- Grouped timeframe menu, custom entry, and persistent star favorites.
- REST auto-sync for aggregate-only charts.

Verified:

- 93 market-data, 57 API, and 52 frontend tests pass.
- Frontend lint, typecheck, and production build pass.

### 2026-06-30 - Day 30.9.5 automatic chart recovery after browser pause

Implemented:

- Added debounced recovery for visible-tab, window-focus, and browser-online events.
- Automatically refetches historical candles and recreates realtime subscriptions.
- Keeps existing candles rendered while backfill is in progress.
- Applies recovery to every visible timeframe without manual refresh.

Safety:

- Recovery only reads market data; no order or exchange-write behavior changed.

### 2026-06-30 - Day 30.9.4 collapsible chart navigation sidebars

Implemented:

- Converted primary navigation to a collapsible icon rail with active-route state.
- Converted the chart market watchlist to an independently collapsible right rail.
- Persisted both layout preferences through a hydration-safe browser store hook.
- Allowed the chart grid to consume the released horizontal space.

Verified:

- Frontend lint, 46 tests, typecheck, diff check, and production build pass.

### 2026-06-30 - Day 30.9.3 chart workspace control layout polish

Implemented:

- Reordered the top controls as symbol, active timeframe, windows, and actions.
- Added active chart targeting for the shared timeframe buttons.
- Removed redundant realtime price text and moved timezone to the footer.
- Reduced time-axis labels to hour and minute while retaining detailed crosshair ranges.

Verified:

- Frontend lint, 46 tests, typecheck, and production build pass.

### 2026-06-30 - Day 30.12 closed versus partial candle handling

Implemented:

- Added explicit complementary `closed` and `partial` aggregate candle flags.
- Added deterministic timezone-aware lifecycle evaluation with an injectable `as_of`.
- Included the active partial candle by default for chart consumers.
- Added `include_partial=False` for backtest and replay consumers.

Verified:

- `npm run market-data-test` passed all 68 tests.
- Ruff passed for schemas, aggregator, and aggregator tests.

Next task: Day 30.13 provider capability map.

### 2026-06-30 - Day 30.9.2 Oanda trailing candle cache repair

Implemented:

- Restricted Oanda's three-day cache tolerance to the leading range edge.
- Required exact timeframe-duration coverage at the trailing edge.
- Backfilled stale XAUUSD higher-timeframe ranges from Oanda.
- Preserved legitimate market maintenance and weekend gaps.

Verified:

- `npm run market-data-test` passed all 64 tests.
- Live diagnostics show current completed tails for 1m through 4h.

### 2026-06-30 - Day 30.9.1 candle timestamp and timezone alignment

Implemented:

- Kept chart coordinates on UTC provider candle opening timestamps, matching TradingView.
- Retained close timestamps as derived metadata without shifting candle selection labels.
- Added consistent timezone-aware opening-time axis and crosshair formatting to every chart window.
- Added persisted UTC and Asia/Bangkok chart timezone selection.
- Kept provider payloads and PostgreSQL timestamps unchanged.

Verified:

- `npm run web-test` passed lint, 45 tests, typecheck, and production build.

### 2026-06-30 - Day 30.9 right-click chart view reset

Implemented:

- Added a reusable chart viewport reset utility.
- Right-click now fits all loaded candles and restores automatic price scaling.
- Applied the interaction independently to every multi-timeframe chart canvas.
- Kept data loading, realtime connections, and persistence unchanged.

Verified:

- `npm run web-test` passed lint, 40 tests, typecheck, and production build.

### 2026-06-30 - Day 30.8 multi-window realtime synchronization

Implemented:

- Removed the duplicate legacy chart below the selected multi-window layout.
- Rendered exactly 1/2/4/8 chart windows, with a full-height single-window mode.
- Added one reconnecting WebSocket per unique visible timeframe and shared duplicate subscriptions.
- Synchronized active candle prices across all windows while preserving timeframe buckets.
- Added API realtime support for 30m and 2h.

Verified:

- `npm run web-test` passed lint, 38 tests, typecheck, and production build.
- `npm run api-test` passed all 56 tests; Ruff passed.
- Live XAUUSD subscriptions returned candles for 4h, 1h, 5m, and 1m.
- API and web containers are healthy on ports 8000 and 2000.

### 2026-06-30 - Day 30.11 CandleAggregator base utility

Implemented:

- Added a pure candle aggregation utility for fixed UTC buckets.
- Implemented deterministic open, high, low, close, volume, and timestamp aggregation.
- Validated source consistency and exact target/source duration divisibility.
- Covered 1m to 5m, 6m, 7m, and 15m aggregation, normalized timeframe values, and invalid inputs.

Verified:

- `npm run market-data-test` passed all 63 tests.
- Ruff passed for the aggregator and its tests.

Next task: Day 30.12 closed versus partial candle handling.

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

### Day 30.14 - CandleService aggregate fallback

Suggested scope:

- Return an exact cached target timeframe when coverage is sufficient.
- Fetch provider candles directly when the capability registry supports the target.
- Otherwise choose a smaller direct base timeframe and aggregate to the target.
- Upsert normalized target candles without mixing provider market types.

## Recently completed

### Day 30.13 - Provider capability map

Implemented:

- Added an immutable direct candle capability registry sourced from adapter constants.
- Added source metadata and explicit Oanda/Binance intended-use boundaries.
- Added direct support and aggregate-required lookup helpers.

Verified:

- 18 capability cases pass within the 86-test market-data suite.
- Ruff checks pass for capability implementation and tests.

### Day 30.12 - Closed versus partial candle handling

Implemented:

- Added complementary lifecycle flags to aggregated candles.
- Added deterministic `as_of` evaluation and exact bucket-end closure.
- Added chart-default partial inclusion and backtest partial exclusion.

Verified:

- 15 aggregator cases pass within the 68-test market-data suite.
- Container smoke testing confirms chart and backtest output modes.

### Day 30.11 - CandleAggregator base utility

Implemented:

- Added fixed UTC bucket aggregation with deterministic OHLCV output.
- Added normalized source/target validation and exact duration divisibility checks.
- Kept aggregation pure and disconnected from provider, storage, and API routing.

Verified:

- 11 aggregator cases pass within the 63-test market-data suite.
- Ruff checks pass for aggregator implementation and tests.

### Day 30.10 - Timeframe parser and validation

Implemented:

- Added canonical minute/hour/day timeframe parsing and normalization.
- Added duration milliseconds and a bounded 31-day safety limit.
- Added a domain validation error for malformed and unsafe values.
- Kept the utility disconnected from the API pending Day 30.15.

Verified:

- 20 parser cases pass within the 52-test market-data suite.
- Ruff checks pass for parser implementation and tests.

### Day 30.7 - Connect multi-window candles

Implemented:

- Extracted a shared normalized market-candles client.
- Added independent fetch, abort, loading, and error state per enabled review window.
- Reused `CandlestickChart` for every review window and retained the legacy chart.
- Requested direct provider timeframes with no aggregation.

Verified:

- Shared client range, normalization, and error tests pass.
- `npm run web-test` passes lint, 36 tests, typecheck, and production build.
- Direct API smoke tests return data for all four persisted window timeframes.

### Day 30.6 - Persist multi-timeframe layout

Implemented:

- Added JSONB layout persistence and Alembic migration `20260630_0005`.
- Added nested backend validation and active-symbol checks.
- Added shared frontend contracts, runtime validation, invalid fallback, and queued saves.
- Preserved existing user settings fields and behavior.

Verified:

- Backend suite passes 52 tests and Ruff.
- Frontend suite passes 33 tests, lint, typecheck, and production build.
- Live API save/reload returned XAUUSD with four persisted windows.

### Day 30.5 - Review checkbox workflow

Implemented:

- Added per-window Reviewed progress for visible/enabled windows.
- Added Clear review with a familiar reset icon and disabled empty state.
- Cleared hidden as well as visible review checks to avoid stale restored state.
- Kept review workflow local and disconnected from all trading behavior.

Verified:

- Progress visibility and clear-all tests pass.
- `npm run web-test` passes lint, 29 tests, typecheck, and production build.

### Day 30.4 - Extended timeframe presets

Implemented:

- Added review-only 30m and 2h timeframe options.
- Added final default presets for 1/2/4/8 window layouts.
- Added eight distinct defaults for the 8-window layout.
- Added direct OANDA H2 mapping without aggregation.

Verified:

- `npm run web-test` passes lint, 27 tests, typecheck, and production build.
- `npm run market-data-test` passes all 32 tests.
- The existing single-chart timeframe selector remains unchanged.

### Day 30.3 - Multi-timeframe grid UI

Implemented:

- Added a controlled responsive `MultiTimeframeGrid` component.
- Rendered visible windows for 1/2/4/8 layouts with one shared symbol.
- Added per-window timeframe selectors, Reviewed checkboxes, and placeholder chart regions.
- Added ID-scoped window updates and enabled-window filtering helpers.

Verified:

- Per-window isolation and visible-window tests pass.
- `npm run web-test` passes lint, 25 tests, typecheck, and production build.
- The existing single live chart remains rendered below the review grid.

### Day 30.2 - Multi-timeframe layout selector

Implemented:

- Added accessible 1/2/4/8 segmented layout controls and active state.
- Added layout resizing that disables rather than deletes hidden windows.
- Restored preserved hidden state when expanding and appended stable defaults up to eight windows.
- Displayed the one shared symbol without changing the single-chart renderer.

Verified:

- Resize-down and resize-up state-preservation tests pass.
- `npm run web-test` passes lint, 23 tests, typecheck, and production build.

### Day 30.1 - Multi-timeframe workspace model

Implemented:

- Added typed 1/2/4/8 window-count presets and multi-timeframe window/layout contracts.
- Added the default 4h, 1h, 15m, and 5m four-window layout.
- Added independent layout creation and shared-symbol update helpers.
- Prepared chart-owned review state without rendering multi-window UI.

Verified:

- Four focused model/state tests pass.
- `npm run web-test` passes lint, 21 tests, typecheck, and production build.
- Existing single-chart candle and realtime paths remain unchanged.

### Day 30 - Persist frontend settings

Implemented:

- Loaded chart defaults from `GET /settings` before the first candle request.
- Applied stored symbol/timeframe with validated fallbacks.
- Gave valid chart URL symbols priority over the stored default.
- Serialized `PATCH /settings` calls after symbol/timeframe changes.
- Added compact saving/error status without blocking chart usage.

Verified:

- Frontend settings tests cover stored defaults, URL precedence, fallbacks, GET, and PATCH payloads.
- `npm run web-test` passes lint, 17 tests, typecheck, and production build.
- Settings API persistence smoke test preserves values across consecutive reads.

### Day 29 - User settings API and Oanda realtime follow-up

Implemented:

- Added Oanda realtime candle updates for XAUUSD, SP500, and US100 through the existing market WebSocket.
- Added Oanda provider routing, normalized source metadata, current-candle polling, and catalog migration.
- Added one-to-one user settings persistence with `GET /settings` and `PATCH /settings`.
- Validated active symbol, timeframe, indicator slugs, theme, and IANA timezone.

Verified:

- Live WebSocket smoke tests received open Oanda candles for all three symbols.
- `npm run api-test` passes all 48 backend tests.
- `npm run web-test` passes lint, 11 tests, typecheck, and production build.

### Day 28 - Watchlist frontend

Implemented:

- Replaced the dashboard watchlist placeholder with a live client panel.
- Added active unpinned symbol selection, add, remove, and refresh controls.
- Added loading, empty, API error, and pending-mutation states.
- Added latest-price placeholders for each row.
- Linked symbols to the chart with a validated query parameter.
- Added BNBUSDT and XRPUSDT to chart-supported Binance markets.

Verified:

- `npm run web-test` passes lint, 11 tests, typecheck, and production build.
- Dashboard and symbol-query chart routes return HTTP 200.
- Server-rendered chart query selects the requested supported symbol.

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
