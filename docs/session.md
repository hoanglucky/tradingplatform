# Session Log

## 2026-06-18 - Monorepo foundation

### User request

Create a production-ready monorepo called `trading-framework` for a web trading MVP with:

- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- Docker Compose
- Modular services for market data, indicators, strategies, backtesting, paper trading, alerts, and exchange adapters

Hard constraints:

- Do not implement real-money live trading.
- Exchange integration must be read-only unless explicitly enabled later.
- Keep architecture modular.
- Add README, `.env.example`, `docs/architecture.md`, and Makefile dev commands.

### Work completed

- Created the monorepo folder structure under `trading-framework/`.
- Added root workspace files:
  - `package.json`
  - `package-lock.json`
  - `.gitignore`
  - `.env.example`
  - `Makefile`
  - `docker-compose.yml`
  - `README.md`
- Added `apps/web` Next.js app:
  - App Router skeleton
  - TypeScript config
  - ESLint flat config
  - Dashboard-like first screen showing module and safety status
  - Shared package imports from `packages/shared` and `packages/ui`
- Added `apps/api` FastAPI app:
  - `/health`
  - `/safety`
  - `/modules`
  - CORS setup
  - Pydantic settings
  - Basic tests for health and safety defaults
- Added shared packages:
  - `packages/shared` for TypeScript domain contracts
  - `packages/ui` for basic `Panel` and `Badge` primitives
- Added modular service scaffolds:
  - `services/market-data`
  - `services/indicator-engine`
  - `services/strategy-engine`
  - `services/backtest-engine`
  - `services/paper-trading`
  - `services/alert-engine`
  - `services/exchange-adapters`
- Each service has:
  - `Dockerfile`
  - `requirements.txt`
  - FastAPI `app/main.py`
  - `/health`
  - `/capabilities`
- Added safety guard in `services/exchange-adapters`:
  - `POST /orders` returns `403` when writes are disabled.
  - Live order placement is intentionally not implemented.
- Added infrastructure files:
  - `infra/postgres/init.sql`
  - `infra/redis/README.md`
- Added architecture documentation:
  - `docs/architecture.md`

### Safety defaults implemented

The scaffold defaults to paper/read-only mode:

- `DEFAULT_TRADING_MODE=paper`
- `ENABLE_LIVE_TRADING=false`
- `ENABLE_EXCHANGE_WRITES=false`
- `EXCHANGE_ADAPTER_MODE=read_only`

Exchange writes require all safety switches to be explicitly changed in a future implementation. Current code still does not implement live trading.

### Verification performed

- `npm install` completed and generated `package-lock.json`.
- `npm run lint` passed.
- `npm run typecheck` passed.
- `npm --workspace apps/web run build` passed.
- `docker compose config --quiet` passed after temporarily creating `.env` from `.env.example`.

### Verification not completed

- Backend pytest was not run locally because host Python does not have `pip` or `venv` available.
- Suggested future verification path:

```bash
cd trading-framework
make setup
docker compose run --rm api pytest
```

### Known issues / review notes

- `npm audit` reports 2 moderate advisories through Next.js transitive `postcss`.
- Next.js was upgraded to current `16.2.9`.
- npm's suggested audit fix is a breaking downgrade to Next 9, so it was not applied.
- `docs/framework.md` existed but was empty before this documentation update.
- `docs/session.md` existed but was empty before this documentation update.

### Current status

Day 1 project foundation is implemented and ready for review.

Next recommended task: Day 2 backend skeleton hardening.

## 2026-06-18 - Day 2 backend skeleton hardening

### User request

Continue implementing Day 2 from the development plan.

### Work completed

- Added backend API package structure:
  - `apps/api/app/api/__init__.py`
  - `apps/api/app/api/router.py`
  - `apps/api/app/api/routes/__init__.py`
  - `apps/api/app/api/routes/health.py`
  - `apps/api/app/api/routes/modules.py`
  - `apps/api/app/api/routes/safety.py`
- Added `apps/api/app/core/logging.py`.
- Added `apps/api/app/schemas/health.py`.
- Updated `apps/api/app/main.py` to use the central API router.
- Removed old `apps/api/app/routers/*` route files to avoid duplicate route ownership.
- Added `/health/ready` readiness endpoint for PostgreSQL and Redis checks.
- Expanded API tests for:
  - `/health`
  - `/health/ready` ready state
  - `/health/ready` degraded state
  - `/safety` defaults
- Added `docs/api.md`.
- Updated `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Safety notes

- No live trading was implemented.
- No exchange write path was added.
- `/safety` still reports paper/read-only defaults.

### Verification performed

- `npm run lint` passed.
- `npm run typecheck` passed.
- `python3 -m compileall -q apps/api/app` passed.
- `docker compose config --quiet` passed with `.env` generated from `.env.example`.
- `npm audit --audit-level=moderate` still reports the known Next.js transitive `postcss` advisory. npm's suggested fix downgrades Next.js to 9.3.3, so it was reviewed and not applied.

### Verification not completed

Backend pytest was attempted with Docker:

```bash
docker compose run --rm api pytest
```

It did not reach pytest because Docker Desktop/BuildKit failed while resolving `python:3.12-slim`:

```txt
failed to solve: error getting credentials
```

This should be retried after Docker credential/pull access is fixed.

## 2026-06-18 - Day 3 frontend skeleton hardening

### User request

Continue reviewing docs and implement the next planned work.

### Work completed

- Reviewed `docs/session.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.
- Confirmed Day 3 was the next task candidate.
- Reworked `apps/web` from a hero-style scaffold into an operational dashboard shell.
- Added typed frontend API helper:
  - `apps/web/lib/api.ts`
- Added reusable frontend components:
  - `apps/web/components/AppShell.tsx`
  - `apps/web/components/EmptySection.tsx`
  - `apps/web/components/SectionPage.tsx`
- Added dashboard routing:
  - `/`
  - `/markets`
  - `/strategies`
  - `/backtests`
  - `/paper`
  - `/alerts`
  - `/settings`
- Added shared TypeScript contracts for:
  - `HealthStatus`
  - `DependencyStatus`
  - `ReadinessStatus`
- Updated dashboard CSS for:
  - Sidebar
  - Topbar
  - API health strip
  - Main dashboard content
  - Empty state panels
  - Responsive mobile layout

### Safety notes

- No live trading controls were added.
- Exchange writes remain shown as blocked.
- Strategy and paper trading UI areas are placeholders only.

### Verification performed

- `npm run lint` passed.
- `npm run typecheck` passed.
- `npm --workspace apps/web run build` passed.
- `npm --workspace apps/web run dev` started successfully at `http://localhost:3000`.
- HTTP checks returned `200 OK` for `/`, `/markets`, and `/settings`.
- The dashboard HTML included `Trading dashboard`, `writes blocked`, and `Candlestick workspace`.

### Verification notes

- The dev server was stopped after verification.

## 2026-06-18 - Dev command update

### User request

Add `npm run dev` so the server and frontend can be started together.

### Work completed

- Updated root `package.json` scripts:
  - `npm run dev` starts API and web together.
  - `npm run dev:api` starts FastAPI.
  - `npm run dev:web` starts Next.js.
  - `npm run dev:compose` starts Docker Compose.
- Implemented `npm run dev` with a simple shell command so no extra process-runner dependency is needed.
- Updated `Makefile`:
  - `make dev` now runs `npm run dev`.
  - `make compose` runs Docker Compose.
- Updated `README.md` with the new local dev commands.

### Notes

- `npm run dev:api` requires the Python API dependencies to be installed in the local Python environment.
- If local Python setup is not available, use `make compose` after Docker pull/credential access is fixed.

## 2026-06-18 - Frontend port update

### User request

Move the frontend from port `3000` to port `1000` to avoid conflicts with another project.

### Work completed

- Updated `apps/web/package.json` so Next.js dev runs with `--port 1000`.
- Updated `apps/web/Dockerfile` to expose port `1000`.
- Updated `docker-compose.yml` web port mapping to `1000:1000`.
- Updated `.env.example` and API default CORS origin to `http://localhost:1000`.
- Updated `README.md` local web URL.

### New local URLs

- Frontend: `http://localhost:1000`
- API: `http://localhost:8000`

### Verification notes

- `npm run lint` passed.
- `npm run typecheck` passed.
- `docker compose config --quiet` passed with `.env` generated from `.env.example`.
- `python3 -m compileall -q apps/api/app` passed.
- `npm run dev:web` attempted to bind `0.0.0.0:1000` and failed on this Linux host with `EACCES`, because port `1000` is below `1024`.
- `WEB_PORT` override was added for local fallback when privileged bind is not available.

## 2026-06-18 - Frontend port update to 2000

### User request

Move the frontend from port `1000` to port `2000`.

### Work completed

- Updated `apps/web/package.json` so Next.js dev defaults to `--port 2000`.
- Updated `apps/web/Dockerfile` to expose port `2000`.
- Updated `docker-compose.yml` web port mapping to `2000:2000`.
- Updated `.env.example` and API default CORS origin to `http://localhost:2000`.
- Updated `README.md` local web URL.

### New local URLs

- Frontend: `http://localhost:2000`
- API: `http://localhost:8000`

### Verification performed

- `npm run lint` passed.
- `npm run typecheck` passed.
- `docker compose config --quiet` passed with `.env` generated from `.env.example`.
- `npm run dev:web` started successfully at `http://localhost:2000`.
- HTTP check returned `200 OK` for `/`.
- The dashboard HTML included `Trading dashboard` and `writes blocked`.
- The dev server was stopped after verification.

## 2026-06-18 - Day 4 Docker Compose setup hardening

### User request

Continue reviewing docs and implement the next planned work.

### Work completed

- Reviewed the plan, session log, task framework, and Codex task handoff.
- Confirmed Day 4 Docker Compose setup was the next task.
- Added root `.dockerignore` to keep the web build context small.
- Added `apps/api/.dockerignore`.
- Added `.dockerignore` files for each service build context.
- Added API healthcheck to `docker-compose.yml`.
- Added web healthcheck to `docker-compose.yml`.
- Changed web dependency to wait for API service health.
- Moved domain service stubs behind the Compose `services` profile so the default Day 4 stack only includes PostgreSQL, Redis, API, and web.
- Updated `apps/api/Dockerfile` to set `PYTHONPATH=/app`.
- Updated `apps/api/Dockerfile` to copy `tests/` into the image.
- Added `docs/docker.md`.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `docker compose config --quiet` passed with `.env` generated from `.env.example`.
- `docker pull python:3.12-slim` passed.
- `docker compose --profile services config --quiet` passed with `.env` generated from `.env.example`.
- `docker compose build api` passed.
- `docker compose run --rm api pytest` passed with 4 tests.
- PostgreSQL and Redis containers started and became healthy during Compose test runs.
- `npm run lint` passed.
- `npm run typecheck` passed.
- `python3 -m compileall -q apps/api/app` passed.

### Verification not completed

- Full `docker compose up --build` was not completed.
- Frontend and backend accessibility through the long-running full Compose stack is still pending.
- `docker compose down` was run after test verification to clean up containers and network.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-18 - Day 5 developer commands polish

### User request

Continue implementing Day 5 from the development plan.

### Work completed

- Added `make up` for detached core Docker Compose startup.
- Added `make api-test` for backend pytest through Docker.
- Added `make web-test` for frontend lint, typecheck, and build.
- Updated `make test` to run API and web checks.
- Updated `make lint` so backend Python linting runs through Docker instead of requiring host Python tooling.
- Updated `make format` so backend Python formatting runs through Docker.
- Added npm fallback commands for environments without `make`.
- Updated README command usage.
- Updated Day 5 planning and task docs.

### Verification notes

- Direct `make` verification could not run because this environment does not have `make` installed.
- npm fallback commands will be used for verification in this environment.
- `npm run api-test` passed with 4 backend tests.
- `npm run web-test` passed frontend lint, typecheck, and production build.
- `npm run lint:api` passed through the built API Docker image.
- `npm test` passed end-to-end by running API and web checks.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-18 - Day 6 database foundation

### User request

Continue implementing Day 6 from the development plan.

### Work completed

- Added `alembic` to API requirements.
- Added SQLAlchemy database package:
  - `apps/api/app/db/base.py`
  - `apps/api/app/db/session.py`
- Updated API readiness check to use the shared database connection check.
- Added Alembic files:
  - `apps/api/alembic.ini`
  - `apps/api/migrations/env.py`
  - `apps/api/migrations/script.py.mako`
  - `apps/api/migrations/versions/20260618_0001_initial_empty.py`
- Updated `apps/api/Dockerfile` to copy Alembic files into the image.
- Added migration commands to `Makefile` and npm scripts.
- Added `docs/database.md`.
- Updated `README.md` with migration usage.

### Verification performed

- `npm run db:upgrade` passed.
- `npm run db:current` returned `20260619_0002 (head)` after Day 7 migration was added.
- `npm run api-test` passed.
- Backend `/health` returned OK through Docker Compose.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 7 core database models

### User request

Continue implementing Day 6 and Day 7.

### Work completed

- Added SQLAlchemy models:
  - `apps/api/app/models/user.py`
  - `apps/api/app/models/symbol.py`
  - `apps/api/app/models/candle.py`
  - `apps/api/app/models/watchlist.py`
  - `apps/api/app/models/mixins.py`
- Added model exports in `apps/api/app/models/__init__.py`.
- Updated Alembic env to import models so metadata is available.
- Added migration `apps/api/migrations/versions/20260619_0002_core_tables.py`.
- Added tests in `apps/api/tests/test_models.py`.
- Updated `docs/database.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q apps/api/app apps/api/tests` passed.
- `npm run lint:api` passed.
- `npm run db:upgrade` passed.
- `npm run db:current` returned `20260619_0002 (head)`.
- `npm run api-test` passed with 6 tests.
- PostgreSQL `\\dt` showed `users`, `symbols`, `candles`, `watchlists`, and `watchlist_items`.
- PostgreSQL `\\di` showed `ix_candles_symbol_timeframe_timestamp` and `uq_candles_symbol_timeframe_timestamp`.
- `npm run web-test` passed.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 8 repository layer

### User request

Continue implementing Day 8.

### Work completed

- Added repository package under `apps/api/app/repositories`.
- Added shared async `BaseRepository` with:
  - `create`
  - `get_by_id`
  - `list`
  - `update`
  - `delete`
- Added domain repositories:
  - `UserRepository`
  - `SymbolRepository`
  - `CandleRepository`
  - `WatchlistRepository`
  - `WatchlistItemRepository`
- Added symbol-specific lookup helpers:
  - `SymbolRepository.get_by_symbol`
  - `SymbolRepository.list_active`
- Added candle and watchlist query helpers for later API/service work.
- Added `apps/api/tests/test_symbol_repository.py`.
- Updated backend test command so `npm run api-test` and `make api-test` apply Alembic migrations before running pytest.
- Updated `docs/database.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q apps/api/app apps/api/tests` passed.
- `npm run lint:api` passed.
- `npm run api-test` passed with 7 tests.
- `npm run web-test` passed.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 9 Symbol API

### User request

Continue implementing Day 9.

### Work completed

- Added Pydantic symbol schemas in `apps/api/app/schemas/symbol.py`.
- Added Symbol API routes in `apps/api/app/api/routes/symbols.py`.
- Registered symbol routes in the central API router.
- Added endpoints:
  - `GET /symbols`
  - `GET /symbols/{symbol_id}`
  - `POST /symbols`
  - `PATCH /symbols/{symbol_id}`
  - `DELETE /symbols/{symbol_id}`
- Added duplicate symbol handling with `409 Conflict`.
- Added API tests in `apps/api/tests/test_symbols_api.py`.
- Added OpenAPI path verification for `/symbols` and `/symbols/{symbol_id}`.
- Updated `APP_ENV=test` backend test command and test DB engine behavior to avoid asyncpg event-loop reuse across pytest tests.
- Updated `README.md`, `docs/api.md`, `docs/database.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q apps/api/app apps/api/tests` passed.
- `npm run lint:api` passed.
- `npm run api-test` passed with 11 tests.
- `npm run web-test` passed.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 10 seed initial symbols

### User request

Continue implementing Day 10.

### Work completed

- Added seed package under `apps/api/app/seed`.
- Added default symbol seed list:
  - `BTCUSDT`
  - `ETHUSDT`
  - `SOLUSDT`
  - `BNBUSDT`
  - `XRPUSDT`
  - `XAUUSD`
  - `SP500`
  - `US100`
- Added CLI command `python -m app.cli.seed_symbols`.
- Added `make seed`.
- Added npm fallback `npm run seed`.
- Updated Docker-backed `api-test` and `seed` commands to create `.env` from `.env.example` when missing.
- Added seed idempotency tests in `apps/api/tests/test_seed_symbols.py`.
- Verified seeded symbols through `GET /symbols?active_only=true`.
- Updated `README.md`, `docs/database.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q apps/api/app apps/api/tests` passed.
- `npm run lint:api` passed.
- `npm run api-test` passed with 12 tests.
- `npm run seed` passed.
- `GET /symbols?active_only=true` returned the eight seeded default symbols.
- `npm run web-test` passed.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 11 MarketDataProvider interface

### User request

Continue implementing Day 11.

### Work completed

- Added normalized market-data schemas:
  - `MarketSymbol`
  - `Candle`
  - `LatestPrice`
- Added `MarketDataProvider` protocol with:
  - `get_symbols`
  - `get_historical_candles`
  - `get_latest_price`
- Added validation that candle and latest-price timestamps must be timezone-aware.
- Added validation that OHLC prices are positive and volume is zero or greater.
- Added market-data schema validation tests.
- Updated market-data Dockerfile to copy tests and set `PYTHONPATH=/service`.
- Added `make market-data-test`.
- Added npm fallback `npm run market-data-test`.
- Updated root `test` command to include market-data service tests.
- Updated shared TypeScript `Candle` type from `openedAt` to `timestamp`.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q services/market-data/app services/market-data/tests` passed.
- `npm run market-data-test` passed with 5 tests.
- `npm test` passed across API, market-data, and web checks.

### Safety notes

- No live trading behavior was added.
- No exchange write behavior was added.

## 2026-06-19 - Day 12 Binance and Oanda market-data adapters

### User request

Continue implementing Day 12.

### Work completed

- Checked the official Binance Spot API docs for public klines.
- Checked the official Oanda v20 docs for Bearer token authentication.
- Added `BinancePublicMarketDataProvider`.
- Added `OandaMarketDataProvider`.
- Added Binance public endpoint support for:
  - `GET /api/v3/exchangeInfo`
  - `GET /api/v3/klines`
  - `GET /api/v3/ticker/price`
- Added Oanda read-only endpoint support for:
  - `GET /v3/instruments/{instrument}/candles`
  - `GET /v3/accounts/{accountID}/instruments` when `OANDA_ACCOUNT_ID` is configured
- Converted Binance kline rows into the internal `Candle` schema.
- Converted Oanda candle rows into the internal `Candle` schema.
- Added symbol, timeframe, and time range validation.
- Added adapter errors for HTTP failures, Binance API errors, and invalid payloads.
- Added mocked HTTP tests for Binance and Oanda success/error cases.
- Added `.env.example` variables:
  - `OANDA_API_TOKEN`
  - `OANDA_ACCOUNT_ID`
  - `OANDA_ENVIRONMENT`
- Added `httpx` to the market-data service requirements.
- Added `docs/market-data.md`.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q services/market-data/app services/market-data/tests` passed.
- `npm run market-data-test` passed with 17 tests.
- `npm test` passed across API, market-data, and web checks.

### Safety notes

- No API key values were added.
- Oanda token configuration was added only as empty environment variables.
- No signed trading endpoints were added.
- No account, private, order, live trading, or exchange write behavior was added.

## 2026-06-20 - Day 13 Market Candles API

### User request

Implement Day 13 after reviewing how Oanda relates to Days 13 and 14.

### Work completed

- Added `GET /market/candles` to the market-data service.
- Added query parameters:
  - `symbol`
  - `timeframe`
  - `start`
  - `end`
- Added automatic provider routing:
  - Oanda for `XAUUSD`, `SP500`, and `US100`
  - Binance for other symbols
- Added response validation through the internal `Candle` schema.
- Added HTTP error mapping:
  - `400` for provider validation errors
  - `502` for upstream provider errors
  - `503` when Oanda token configuration is missing
- Added CORS configuration for the frontend origin.
- Exposed the market-data service on port `8101`.
- Added `NEXT_PUBLIC_MARKET_DATA_BASE_URL` to `.env.example`.
- Added endpoint tests with mocked providers.
- Updated `README.md`, `docs/market-data.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q services/market-data/app services/market-data/tests` passed.
- `npm run market-data-test` passed with 23 tests.
- `npm test` passed across API, market-data, and web checks.
- Market-data `/health` returned OK on port `8101`.
- XAUUSD request returned `503` with a clear `OANDA_API_TOKEN` configuration message when the token was empty.

### Safety notes

- No order or trading endpoints were added.
- Oanda remains read-only and requires an externally supplied token.
- No live trading or exchange write behavior was added.

## 2026-06-20 - Day 14 Candle Storage

### User request

Implement Day 14.

### Work completed

- Added async PostgreSQL engine/session support to the market-data service.
- Added a SQLAlchemy Core candle repository using the existing `symbols` and `candles` tables.
- Added symbol resolution with provider exchange preference.
- Added candle range queries ordered by timestamp.
- Added PostgreSQL upsert based on `symbol_id + timeframe + timestamp`.
- Added `CandleStorageService` to:
  - return complete cached ranges without calling the provider
  - fetch provider data when cache coverage is incomplete
  - deduplicate provider rows by timestamp before upsert
  - return normalized candle rows from PostgreSQL
- Updated `/market/candles` to use the storage service.
- Added 404 handling for symbols that are not registered in the symbol catalog.
- Updated market-data test commands to apply Alembic migrations before pytest.
- Added unit tests for cache hits, partial cache fetches, deduplication, and unknown symbols.
- Added a PostgreSQL integration test proving repeated upserts leave one candle row with updated values.
- Updated `README.md`, `docs/database.md`, `docs/market-data.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q services/market-data/app services/market-data/tests` passed.
- `npm run market-data-test` passed with 28 tests.

### Safety notes

- Candle persistence is read-only market-data infrastructure.
- No order, live trading, or exchange write behavior was added.

## 2026-06-20 - Day 15 Market Data Documentation

### User request

Implement Day 15.

### Work completed

- Updated `docs/architecture.md` with:
  - current implementation status
  - complete market-data request flow
  - `MarketDataProvider` contract
  - Binance and Oanda provider behavior
  - internal Candle contract
  - PostgreSQL cache and deduplication design
  - Oanda credential safety guidance
- Updated `docs/api.md` with:
  - market-data service base URL
  - `/market/candles` query parameters
  - Binance and Oanda examples
  - normalized response example
  - provider routing
  - cache behavior
  - HTTP error behavior
  - environment configuration
- Updated `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `python3 -m compileall -q services/market-data/app services/market-data/tests` passed.
- `npm run web-test` passed frontend lint, typecheck, and production build.
- Required market-data architecture and API documentation sections were verified with `rg`.
- `npm test` was attempted but Docker Desktop/WSL integration was unavailable at that moment. Earlier in the same work session, `npm run market-data-test` passed with 28 tests, including the PostgreSQL upsert integration test.

### Safety notes

- Documentation preserves read-only provider boundaries.
- No live trading or exchange write behavior was added.

## 2026-06-20 - Day 16 Chart Library Setup

### User request

Implement Day 16.

### Work completed

- Installed TradingView Lightweight Charts 5.2.0 in the web workspace.
- Added `/dashboard/chart`.
- Added Chart navigation to the application sidebar.
- Added a client-side mock candlestick renderer using `createChart` and `CandlestickSeries`.
- Added sixteen mock BTCUSDT hourly candles.
- Added responsive chart resizing and cleanup on unmount.
- Added an operational chart toolbar with mock symbol, timeframe, last price, and change.
- Added stable desktop/mobile chart dimensions.
- Added visible TradingView attribution.
- Kept the page disconnected from market-data APIs as required by Day 16.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `npm run web-test` passed lint, typecheck, and production build.
- Next.js build included `/dashboard/chart` as a static route.
- `GET /dashboard/chart` returned HTTP 200 from the local dev server.
- Server HTML included BTCUSDT, mock data status, and TradingView attribution.
- Chromium/Playwright was not available in the environment for an automated canvas screenshot.

### Safety notes

- Mock chart data is local and does not call Binance or Oanda.
- No live trading or exchange write behavior was added.

## 2026-06-20 - Day 17 Reusable CandlestickChart

### User request

Implement Day 17.

### Work completed

- Replaced `MockCandlestickChart` with reusable `CandlestickChart`.
- Added required props:
  - `candles`
  - `symbol`
  - `timeframe`
  - `height`
  - `loading`
  - `error`
- Added ISO timestamp conversion and chronological sorting.
- Added loading state with reduced-motion support.
- Added explicit error and empty-data states.
- Preserved stable dimensions for every component state.
- Preserved ResizeObserver-based width updates.
- Preserved chart and observer cleanup on state changes and unmount.
- Moved mock candles to `/dashboard/chart` and passed them through props.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `npm run web-test` passed lint, typecheck, and production build.
- Next.js build included `/dashboard/chart`.

### Safety notes

- Chart data remains local mock data.
- No live trading or exchange write behavior was added.
