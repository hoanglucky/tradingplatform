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

## 2026-06-23 - Day 18 Symbol and Timeframe Selectors

### User request

Implement Day 18.

### Work completed

- Added client-side `ChartWorkspace` component.
- Added native symbol selector with:
  - BTCUSDT
  - ETHUSDT
  - SOLUSDT
  - XAUUSD
  - SP500
  - US100
- Added segmented timeframe selector with:
  - 1m
  - 5m
  - 15m
  - 1h
  - 4h
  - 1d
- Set defaults to BTCUSDT and 15m.
- Added selected and focus-visible control states.
- Added deterministic mock candle generation per symbol and timeframe.
- Updated chart title, provider label, latest price, and percentage change from selection state.
- Kept selectors disconnected from market-data APIs for Day 18.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `npm run web-test` passed lint, typecheck, and production build.
- Next.js build included `/dashboard/chart`.
- `GET /dashboard/chart` returned HTTP 200.
- Initial page HTML contained BTCUSDT, 15m, and Binance/Oanda symbol options.

### Safety notes

- Selection changes only local mock chart data.
- No live trading or exchange write behavior was added.

## 2026-06-23 - Day 19 Connect Chart to Backend

### User request

Implement Day 19.

### Work completed

- Removed the client-side mock candle generator from `ChartWorkspace`.
- Connected the chart to `NEXT_PUBLIC_MARKET_DATA_BASE_URL/market/candles`.
- Added automatic fetches when symbol or timeframe changes.
- Added 120-bar lookback ranges aligned to timeframe boundaries.
- Added AbortController cleanup to prevent stale requests from updating state.
- Added API response validation.
- Converted API Decimal strings into numeric OHLCV values.
- Connected backend data to the reusable `CandlestickChart`.
- Connected latest close and percentage change to fetched candles.
- Added live/loading/unavailable status feedback.
- Passed backend errors into the chart error state.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `npm run web-test` passed lint, typecheck, and production build.
- Next.js build included `/dashboard/chart`.
- PostgreSQL, Redis, and market-data services started successfully through Docker Compose.
- Default symbols were migrated and seeded.
- A live BTCUSDT 15m request returned HTTP 200 with normalized Binance candles.

### Safety notes

- The chart only requests read-only market data.
- No order, live trading, or exchange write behavior was added.

## 2026-06-23 - Day 20 Chart UI Polish

### User request

Implement Day 20.

### Work completed

- Refined the chart toolbar into a responsive market header.
- Kept symbol/provider identification and the read-only exchange label visible.
- Added a clearly labeled latest-close value and period percentage change.
- Added an accessible manual refresh button using a Lucide icon.
- Disabled refresh while a request is active and added reduced-motion-aware spinner feedback.
- Added loading, refreshing, live, and unavailable states.
- Added the last successful update time.
- Preserved existing candles on screen while a manual refresh runs.
- Reset stale chart values immediately when symbol or timeframe changes.
- Improved tablet and mobile control layout.
- Updated `README.md`, `docs/plan.md`, `docs/task.md`, and `docs/codex-tasks.md`.

### Verification performed

- `npm run web-test` passed lint, typecheck, and production build.
- Next.js production build included `/dashboard/chart`.
- `GET http://localhost:2000/dashboard/chart` returned HTTP 200.
- `GET http://localhost:8101/health` returned HTTP 200.

### Safety notes

- Refresh only repeats a read-only `GET /market/candles` request.
- No order, live trading, or exchange write behavior was added.

## 2026-06-23 - Day 21 Backend WebSocket Endpoint

### User request

Implement Day 21.

### Work completed

- Added FastAPI endpoint `WS /ws/market`.
- Added Pydantic contracts for subscriptions, acknowledgements, candles, and errors.
- Added symbol normalization and validation for the six chart timeframes.
- Added periodic mock OHLCV updates aligned to timeframe boundaries.
- Added `MARKET_WS_INTERVAL_SECONDS` configuration with a three-second default.
- Supported resubscription on an existing WebSocket connection.
- Kept connections open after invalid subscription messages so clients can retry.
- Added WebSocket tests for successful streaming and validation errors.
- Updated `.env.example`, `README.md`, and API, architecture, plan, task, and session docs.

### Verification performed

- `npm run lint:api` passed Ruff checks.
- `npm run api-test` passed all 14 backend tests.
- Docker API healthcheck reached `healthy`.
- A live Docker WebSocket client received both `subscribed` and `candle` messages.

### Safety notes

- Day 21 emits explicitly marked mock market data.
- The WebSocket exposes no order, live trading, account write, or exchange write operation.

## 2026-06-23 - Day 22 Real Market Stream Service

### User request

Implement Day 22.

### Work completed

- Replaced the Day 21 mock candle producer with Binance's public kline WebSocket.
- Added explicit `websockets` runtime dependency.
- Added strict normalization and OHLC range validation for Binance kline payloads.
- Added `source`, `mock`, and candle `closed` fields to realtime messages.
- Added `MarketStreamHub` with one upstream task per symbol/timeframe.
- Added bounded queues that broadcast updates to all matching frontend clients.
- Added resubscription cleanup and cancellation after the final client disconnects.
- Added reconnect status events and bounded exponential backoff.
- Added environment configuration for the Binance URL and reconnect delays.
- Added unit and route tests for normalization, fan-out, reconnect, resubscribe, and cleanup.
- Updated README, API, architecture, plan, task, and session documentation.

### Verification performed

- `python3 -m compileall -q apps/api/app apps/api/tests` passed.
- `npm run lint:api` passed Ruff checks.
- `npm run api-test` passed all 20 backend tests.
- Docker API healthcheck reached `healthy`.
- Live `/ws/market` smoke test received a real BTCUSDT 1m candle from Binance.

### Safety notes

- The Binance source uses the public market-data-only endpoint and needs no API key.
- No account stream, order endpoint, live trading, or exchange write behavior was added.
- Oanda-only symbols are not yet supported by the realtime stream.

## 2026-06-29 - Day 23 Frontend WebSocket Subscription

### User request

Implement Day 23.

### Work completed

- Added `NEXT_PUBLIC_MARKET_WS_URL` frontend configuration.
- Connected Binance chart selections to `WS /ws/market` after historical candles load.
- Added strict realtime candle normalization and OHLCV validation.
- Added epoch-based candle merging so equivalent ISO timestamps update one bar.
- Appended only strictly newer candles and ignored stale unknown updates.
- Limited retained realtime history to 500 candles.
- Added connection-version guards to prevent stale sockets from mutating new selections.
- Closed sockets when symbol/timeframe changes, during refresh, and on unmount.
- Added realtime, connecting, reconnecting, disconnected, unavailable, and historical-only status text.
- Kept Oanda-only selections on the historical HTTP path.
- Refactored `CandlestickChart` to preserve its chart instance during realtime updates.
- Added four frontend tests for normalization, update, append, stale data, and invalid OHLC handling.
- Updated Makefile and npm web-test commands to include frontend tests.
- Updated README, architecture, plan, task, and session documentation.

### Verification performed

- `npm run web-test` passed lint, four tests, typecheck, and production build.
- Next.js production build included `/dashboard/chart`.
- `GET http://localhost:2000/dashboard/chart` returned HTTP 200.
- API and market-data health endpoints returned HTTP 200.
- Live `WS /ws/market` smoke test received a real BTCUSDT candle from Binance.

### Safety notes

- The frontend consumes only public, read-only market data.
- No account stream, order action, live trading, or exchange write behavior was added.
- Oanda-only symbols do not open a Binance WebSocket.

## 2026-06-29 - Day 24 Reconnect and Heartbeat

### User request

Implement Day 24.

### Work completed

- Added frontend WebSocket reconnect with bounded exponential backoff.
- Reset reconnect attempts after a successful subscription acknowledgement.
- Added retry timer and connection-version cleanup on selection changes, refresh, and unmount.
- Guarded each socket so it sends at most one subscription.
- Added explicit frontend retry and upstream reconnect UI states.
- Added backend heartbeat messages with monotonically increasing ids and UTC timestamps.
- Added frontend pong replies using the matching heartbeat id.
- Added backend stale-client detection and close code `1001`.
- Made repeated identical subscriptions idempotent.
- Added environment settings for frontend retry and backend heartbeat/stale timing.
- Added backend tests for heartbeat, stale cleanup, and duplicate subscriptions.
- Expanded frontend tests for reconnect backoff and heartbeat pong validation.
- Updated README, API, architecture, plan, task, and session documentation.

### Verification performed

- `npm run lint:api` passed Ruff checks.
- `npm run api-test` passed all 23 backend tests.
- `npm run web-test` passed lint, six tests, typecheck, and production build.
- Live WebSocket smoke test received a BTCUSDT candle and heartbeat, then returned pong.
- Docker API healthcheck reached `healthy`.

### Safety notes

- Heartbeat and reconnect logic only manage read-only market-data connections.
- No account stream, order action, live trading, or exchange write behavior was added.
- Oanda-only symbols remain on historical HTTP data.

## 2026-06-29 - Day 25 Realtime Tests

### User request

Implement Day 25.

### Work completed

- Split candle append and stale-candle behavior into independent tests.
- Added explicit empty-chart initialization coverage.
- Added duplicate-timestamp replacement coverage for a multi-candle series.
- Confirmed duplicate replacement preserves candle order.
- Confirmed existing-candle updates do not mutate historical input objects.
- Retained tests for invalid OHLC values, reconnect backoff, and heartbeat pong messages.
- Updated README, plan, task, Codex task, and session documentation.

### Verification performed

- Nine frontend market-stream tests passed.
- Required Day 25 cases all have direct regression coverage.

### Safety notes

- Day 25 changes test coverage only and does not add execution behavior.
- No account stream, order action, live trading, or exchange write behavior was added.

## 2026-06-29 - Day 26 Mock User Mode

### User request

Implement Day 26.

### Work completed

- Added `MVP_USER_MODE`, `MVP_USER_EMAIL`, and `MVP_USER_DISPLAY_NAME` configuration.
- Added PostgreSQL conflict-safe `UserRepository.get_or_create_by_email`.
- Added `ensure_mvp_user` and reusable FastAPI `get_mvp_user` dependency.
- Added `GET /users/me` with explicit `mvp_local` response mode.
- Added a `503` response when MVP mode is disabled and authentication is unavailable.
- Added tests for idempotent creation, stable identity, disabled mode, and OpenAPI registration.
- Documented how Day 27 watchlist and Day 29 settings routes must reuse the dependency.
- Updated README, API, architecture, database, plan, task, Codex task, and session docs.

### Verification performed

- `npm run lint:api` passed Ruff checks.
- `npm run api-test` passed all 27 backend tests.
- `npm run web-test` passed lint, nine tests, typecheck, and production build.
- Live `GET /users/me` requests returned HTTP 200 twice with the same UUID.
- The persisted user uses the configured local email and display name.

### Safety notes

- MVP user mode is explicitly not authentication or authorization.
- No passwords, sessions, roles, permissions, or exchange credentials were added.
- No live trading or exchange write behavior was added.

## 2026-06-29 - Day 27 Watchlist API

### User request

Implement Day 27.

### Work completed

- Added `MVP_WATCHLIST_NAME` configuration.
- Added conflict-safe default watchlist creation for the MVP user.
- Added `GET /watchlist` with joined catalog symbol metadata.
- Added `POST /watchlist/items` with uppercase normalization and active-symbol validation.
- Added duplicate item protection with HTTP `409`.
- Added `DELETE /watchlist/items/{symbol}` with lowercase path support.
- Added distinct `404` responses for unknown catalog symbols and missing watchlist items.
- Added repository helpers for watchlist lookup, joins, item insertion, and deletion.
- Added six API integration tests using isolated temporary MVP users.
- Updated README, API, architecture, database, plan, task, Codex task, and session docs.

### Verification performed

- `npm run lint:api` passed Ruff checks.
- `npm run api-test` passed all 33 backend tests.
- Live CRUD smoke test returned GET `200`, add `201`, duplicate `409`, list `200`, and delete `204`.
- The live list response included normalized `BTCUSDT` symbol metadata.

### Safety notes

- Watchlist operations only modify local application data for the MVP user.
- No exchange account, order action, live trading, or exchange write behavior was added.

## 2026-06-29 - Day 28 Watchlist Frontend

### User request

Implement Day 28.

### Work completed

- Replaced the dashboard watchlist placeholder with a live `WatchlistPanel`.
- Loaded the MVP watchlist and active symbol catalog concurrently.
- Filtered pinned and inactive symbols from the add selector.
- Added accessible icon controls for add, remove, and refresh.
- Added stable loading, empty, initial-error, and mutation-error states.
- Refreshed watchlist data after successful mutations without reloading the dashboard.
- Added latest-price placeholders to watchlist rows.
- Linked each symbol to `/dashboard/chart?symbol=...`.
- Updated the chart route to accept and validate an initial symbol query.
- Added BNBUSDT and XRPUSDT to supported chart markets.
- Added shared watchlist TypeScript contracts and pure helper tests.
- Updated README, architecture, plan, task, Codex task, and session documentation.

### Verification performed

- `npm run web-test` passed lint, 11 tests, typecheck, and production build.
- `GET http://localhost:2000/` returned HTTP 200.
- `GET http://localhost:2000/dashboard/chart?symbol=ETHUSDT` returned HTTP 200.
- Server-rendered HTML marked ETHUSDT as the selected chart symbol.
- `GET http://localhost:8000/watchlist` returned HTTP 200.

### Safety notes

- Watchlist UI mutates only local application watchlist data.
- Chart links continue to consume read-only market data.
- No account stream, order action, live trading, or exchange write behavior was added.
## Day 28 follow-up - Watchlist on chart

- Added the watchlist panel directly beside the chart workspace.
- Watchlist symbol links now remount the chart workspace with the selected symbol.
- Added a responsive single-column layout for smaller screens.
- The watchlist remains available on the main dashboard.

## 2026-06-29 - Oanda realtime follow-up and Day 29 settings API

### Work completed

- Routed `XAUUSD`, `SP500`, and `US100` through Oanda in the shared market WebSocket.
- Added read-only current-candle polling every two seconds because the configured Oanda account pricing stream returns `403` while instrument candles return `200`.
- Normalized Oanda candle events to the existing realtime OHLCV contract.
- Added the missing Oanda provider assignment for SP500 and US100 through Alembic migration `20260629_0003`.
- Added one-to-one user settings model, repository, schemas, and migration `20260629_0004`.
- Added `GET /settings` and `PATCH /settings` with MVP user ownership and preference validation.
- Added shared frontend `UserSettings` contract and updated architecture, API, database, plan, task, and README documentation.

### Verification performed

- Live WebSocket smoke tests received open Oanda candles for XAUUSD, SP500, and US100.
- `npm run api-test` passed all 48 backend tests.
- `npm run lint:api` passed after the settings implementation.
- `npm run web-test` passed lint, 11 tests, typecheck, and production build.

### Safety notes

- Oanda integration reads instrument candles only.
- Account pricing stream permissions were not bypassed.
- No order, account mutation, live trading, or exchange write behavior was added.

## 2026-06-29 - One-month chart history

### Work completed

- Added `1D`, `1W`, and `1M` history range controls to the chart toolbar.
- Oanda chart links now default to one month of history at the existing 15-minute timeframe.
- Added chunked Oanda requests for ranges beyond the 5000-candle provider limit.
- Added paginated Binance requests for ranges beyond the 1000-kline provider limit.
- Long-range candles continue to use PostgreSQL deduplication and caching.
- Oanda cache coverage tolerates weekend edge gaps so month windows do not refetch unchanged closed-market periods.

### Verification performed

- Live 30-day `15m` requests returned 1866 candles each for XAUUSD, SP500, and US100.
- The first returned candle was the first available market session after the weekend boundary.
- Market-data and frontend regression suites passed after the range changes.

### Safety notes

- Historical requests are read-only.
- No account mutation, trading, or exchange write path was added.

## 2026-06-29 - Day 30 frontend settings persistence

### Work completed

- Added a typed frontend settings API client for `GET /settings` and `PATCH /settings`.
- Delayed the first candle request until stored chart preferences resolve.
- Restored supported default symbol and timeframe values on chart load.
- Made a valid URL/watchlist symbol override the stored symbol and persist as the next default.
- Serialized settings writes so rapid selection changes retain request order.
- Kept chart fallbacks usable when the settings API is unavailable.
- Added preference loading, precedence, fallback, GET, and PATCH regression tests.

### Verification performed

- `npm run web-test` passed lint, settings and realtime tests, typecheck, and production build.
- Live API smoke testing confirmed settings survive consecutive reads.

### Safety notes

- Settings writes modify local application preferences only.
- No order, account mutation, live trading, or exchange write behavior was added.

## 2026-06-29 - Day 30.1 multi-timeframe workspace model

### Work completed

- Added TypeScript contracts for multi-timeframe windows, layouts, timeframes, and 1/2/4/8 window counts.
- Added a default four-window layout using 4h, 1h, 15m, and 5m.
- Added helpers that clone default window state and update one shared normalized symbol.
- Added prepared multi-timeframe state to `ChartWorkspace` and synchronized it with settings and dropdown symbol changes.
- Kept the state non-visual so Day 30.2 can add layout controls without changing the existing single-chart workflow early.

### Verification performed

- Four multi-timeframe model/state tests passed.
- `npm run web-test` passed lint, 21 tests, typecheck, and production build.

### Safety notes

- No backend, market-data request, candle aggregation, signal, paper order, or exchange-write behavior was added.

## 2026-06-29 - Day 30.2 multi-timeframe layout selector

### Work completed

- Added an accessible segmented selector for 1, 2, 4, and 8 review windows.
- Added a visible active state and shared-symbol summary.
- Added resize behavior that disables extra windows while preserving their timeframe and review state.
- Restored hidden state when expanding and created stable unique windows when growing to eight.
- Kept the existing single-chart workspace rendered below the prepared review controls.

### Verification performed

- Layout reduction, restoration, expansion, unique-ID, and state-preservation tests passed.
- `npm run web-test` passed lint, 23 tests, typecheck, and production build.

### Safety notes

- No multi-window candle request, aggregation, strategy signal, paper order, or exchange write was added.

## 2026-06-29 - Day 30.3 multi-timeframe grid UI

### Work completed

- Added a controlled `MultiTimeframeGrid` component for visible review windows.
- Added per-window timeframe selectors and Reviewed checkboxes keyed by stable window IDs.
- Added placeholder chart regions without connecting candle requests early.
- Added responsive 1/2/4-column layouts with a one-column mobile fallback.
- Kept one shared symbol across every window and retained the existing live single chart.

### Verification performed

- Per-window update and enabled-window filtering tests passed.
- `npm run web-test` passed lint, 25 tests, typecheck, and production build.

### Safety notes

- Reviewed state remains local UI workflow state only.
- No candle aggregation, strategy signal, paper order, or exchange write was added.

## 2026-06-30 - Day 30.4 extended timeframe presets and plan review

### Work completed

- Reviewed the expanded roadmap from Day 30.x through custom aggregation, structure/setup engines, cross-market data, orderflow/liquidity, premium providers, and quant modules.
- Added review-only 30m and 2h options while leaving the single-chart selector unchanged.
- Added final defaults for 1/2/4/8 layouts, including eight distinct timeframes for layout 8.
- Added direct OANDA H2 support for two-hour historical candles.
- Reconciled completed Day 30.1–30.4 checklists in the newly updated plan.

### Verification performed

- `npm run web-test` passed lint, 27 tests, typecheck, and production build.
- `npm run market-data-test` passed all 32 tests.
- Live `XAUUSD` 2h smoke testing returned direct OANDA candles with timeframe `2h`.

### Plan review

- Complete Day 30.5–30.7 before custom timeframe and aggregation work.
- Implement Day 30.10–30.22 as one dependency chain: parser, aggregator, partial handling, capability routing, API, persistence, cache, tests, and docs.
- Treat Day 30.30+, 30.50+, 30.80+, and 30.90+ as later module groups rather than parallel work.
- The new Day 30.x entries are plain-text headings; converting them to Markdown headings later would improve navigation without changing scope.

### Safety notes

- No candle aggregation, strategy signal, paper order, live trading, or exchange write was added.

## 2026-06-30 - Day 30.5 review checkbox workflow

### Work completed

- Added a live Reviewed progress indicator for visible/enabled windows.
- Added Clear review with disabled zero-progress state.
- Cleared review flags across visible and hidden windows to prevent stale state after expansion.
- Kept review actions local to the chart workspace.

### Verification performed

- Progress and clear-all state tests passed.
- `npm run web-test` passed lint, 29 tests, typecheck, and production build.

### Safety notes

- Review flags do not create signals, invoke strategy evaluation, create paper orders, or access exchange writes.

## 2026-06-30 - Day 30.6 persist multi-timeframe layout

### Work completed

- Added nullable JSONB layout storage and migration `20260630_0005`.
- Added nested backend schemas and active-symbol validation.
- Added shared TypeScript contracts and frontend runtime validation.
- Loaded valid saved layouts, repaired invalid layouts with a safe default, and queued layout writes with existing preferences.
- Preserved default symbol, timeframe, indicators, theme, and timezone behavior.

### Verification performed

- `npm run api-test` passed all 52 backend tests.
- `npm run lint:api` passed Ruff.
- `npm run web-test` passed lint, 33 tests, typecheck, and production build.
- Migration head is `20260630_0005`.
- Live API save/reload returned the persisted XAUUSD four-window layout.

### Safety notes

- Layout persistence only modifies local user preferences and cannot create signals or orders.

## 2026-06-30 - Day 30.7 connect multi-window candles

### Work completed

- Extracted shared candle request, error, and normalization logic from `ChartWorkspace`.
- Reused that client for the existing chart and every enabled multi-timeframe window.
- Added per-window loading, error, candle, and AbortController state.
- Replaced placeholders with the existing `CandlestickChart` component.
- Loaded the latest 120 candles independently for each direct provider timeframe.

### Verification performed

- Shared client tests cover range alignment, normalization, query construction, and provider errors.
- `npm run web-test` passed lint, 36 tests, typecheck, and production build.
- Direct API smoke testing covered all persisted layout timeframes.

### Safety notes

- No candle aggregation, strategy signal, paper order, multi-window realtime stream, or exchange write was added.

## 2026-06-30 - Day 30.10 timeframe parser and validation

### Work completed

- Added a pure parser for positive integer minute, hour, and day timeframe strings.
- Added canonical lowercase normalization and duration milliseconds.
- Added explicit validation errors and a 31-day upper safety bound.
- Kept the parser disconnected from providers, storage, and the candle API.

### Verification performed

- Added 20 parser cases including 6m, 7m, 45m, 3h, invalid syntax, and unsafe durations.
- `npm run market-data-test` passed all 52 tests.
- Ruff passed for the parser and its tests.

### Safety notes

- No candle aggregation, route behavior change, trading signal, paper order, or exchange write was added.

## 2026-06-30 - Day 30.11 CandleAggregator base utility

### Work completed

- Added a pure `CandleAggregator` and functional `aggregate_candles` entry point.
- Added deterministic fixed UTC bucket grouping for custom target durations.
- Implemented first-open, maximum-high, minimum-low, last-close, summed-volume, and bucket-start output rules.
- Added source consistency, target size, and exact duration multiple validation.

### Verification performed

- Added 11 tests covering 1m to 5m, 6m, 7m, and 15m, exact OHLCV output, timeframe normalization, timezone normalization, reversed input, empty input, and invalid combinations.
- `npm run market-data-test` passed all 63 tests.
- Ruff passed for the aggregator and its tests.

### Follow-up boundary

- Closed versus partial candle classification remains Day 30.12 work.
- Provider fallback, API, database, and cache integration remain disconnected.

### Safety notes

- No strategy signal, paper order, live trading, account mutation, or exchange write was added.

## 2026-06-30 - Day 30.8 multi-window realtime synchronization

### Work completed

- Removed the standalone chart that was rendered below the multi-timeframe workspace.
- Made layout selection render exactly 1, 2, 4, or 8 charts; single mode uses a taller chart.
- Moved realtime ownership to the workspace and deduplicated subscriptions by visible timeframe.
- Merged each direct-provider realtime candle into its matching history and synchronized all active candle prices to the latest workspace quote.
- Added WebSocket and Oanda realtime mappings for 30m/M30 and 2h/H2.
- Kept per-window loading/error state, heartbeat pong, reconnect backoff, settings persistence, and refresh-all behavior.

### Verification performed

- `npm run web-test` passed lint, 38 tests, typecheck, and production build.
- `npm run api-test` passed all 56 tests.
- Ruff and `git diff --check` passed.
- Live XAUUSD WebSocket smoke testing returned 4h, 1h, 5m, and 1m candles.
- Rebuilt API/web containers are healthy at ports 8000 and 2000.

### Safety notes

- All market connections remain read-only; no strategy, order, account mutation, or exchange write path was added.

## 2026-06-30 - Day 30.9 right-click chart view reset

### Work completed

- Added `resetCandlestickChartView` for deterministic time and price scale reset.
- Added right-click handling to every loaded `CandlestickChart` canvas.
- Suppressed the browser context menu on the canvas and reset only the selected chart instance.
- Kept candle state, historical requests, realtime streams, and settings untouched.

### Verification performed

- Added tests for time-axis fitting, right-price-axis auto-scale, and unavailable chart instances.
- `npm run web-test` passed lint, 40 tests, typecheck, and production build.

### Safety notes

- This is a presentation-only interaction and adds no trading or exchange-write behavior.

## 2026-06-30 - Day 30.9.1 candle timestamp and timezone alignment

### Work completed

- Confirmed Oanda timestamps are UTC candle-open instants and left transport/storage unchanged.
- Added open/close-time utilities for every multi-timeframe preset.
- Kept chart points on provider opening instants and added timezone-aware axis/crosshair formatters.
- Added a persisted UTC/Bangkok chart timezone control shared by all windows.
- Set the local MVP user's persisted chart timezone to `Asia/Bangkok`.

### Verification performed

- Corrected an earlier duration offset that displayed a 14:55 candle as 15:00 when selected.
- Verified the live 1m API contains every candle from 15:00 through 15:05; only axis labels were sampled.
- Added an exact candle timestamp overlay driven by crosshair movement for every chart window.
- Expanded the overlay to show the full bucket range for all preset timeframes.
- Tests cover unchanged provider-open coordinates, derived close calculations, UTC/Bangkok formatting, and invalid timestamps/timeframes.
- `npm run web-test` passed lint, 46 tests, typecheck, and production build.

### Safety notes

- No provider payload, database timestamp, strategy, order, account, or exchange-write behavior changed.

## 2026-06-30 - Day 30.9.2 Oanda trailing candle cache repair

### Work completed

- Reproduced stale 5m/15m and hourly API ranges while 1m data remained current.
- Identified a three-day Oanda tolerance incorrectly applied to the cache trailing edge.
- Kept weekend tolerance at the leading edge and restored strict duration-based trailing coverage.
- Rebuilt market-data and refetched all XAUUSD preset timeframe ranges into PostgreSQL.

### Verification performed

- Added a regression test proving stale Oanda tails call the provider and return a complete range.
- `npm run market-data-test` passed all 64 tests.
- Live diagnostics show latest completed provider candles for every preset through 4h.
- Remaining larger gaps match Oanda daily maintenance or weekend closure periods.

### Safety notes

- The change only refreshes read-only candle cache data and adds no exchange-write behavior.

## 2026-06-30 - Day 30.12 closed versus partial candle handling

### Work completed

- Added an `AggregatedCandle` schema with complementary closed/partial state.
- Classified buckets from their UTC end against a timezone-aware evaluation instant.
- Kept partial candles enabled by default for chart consumers.
- Added deterministic partial exclusion for backtest and replay consumers.
- Rejected naive `as_of` values to avoid timezone-dependent results.

### Verification performed

- Added tests for active partial buckets, completed buckets, exact close boundaries, backtest exclusion, and invalid evaluation time.
- `npm run market-data-test` passed all 68 tests.
- Ruff passed for the updated schema, aggregator, and tests.

### Follow-up boundary

- Provider capability selection starts in Day 30.13.
- Aggregate fallback and API integration remain Day 30.14–30.15.

### Safety notes

- No provider write, strategy signal, paper order, live trading, account mutation, or exchange write was added.

## 2026-06-30 - Day 30.13 provider capability map

### Work completed

- Added an immutable capability registry sourced from Oanda and Binance adapter timeframe constants.
- Added provider, venue, market type, data type, intended use, direct timeframe, and read-only metadata.
- Classified Oanda as the primary CFD/FX source and Binance public as crypto development data.
- Added normalized direct lookup and explicit aggregate-required detection for valid custom intervals.

### Verification performed

- Added 18 tests covering metadata, adapter-constant parity, direct intervals, custom intervals, malformed values, unknown providers, and registry immutability.
- `npm run market-data-test` passed all 86 tests.
- Ruff passed for the capability module and tests.

### Follow-up boundary

- Day 30.14 consumes the registry for direct-versus-aggregate candle routing.
- `/market/candles` custom timeframe exposure remains Day 30.15.

### Safety notes

- Every provider remains explicitly read-only; no account or order behavior was added.

## 2026-06-30 - Day 30.9.3 chart workspace control layout polish

### Work completed

- Consolidated chart controls into one symbol → timeframe → windows → actions toolbar.
- Added active-window selection for shared timeframe buttons while preserving local selectors.
- Removed global and per-window numeric realtime price displays.
- Moved timezone to the bottom-right footer and kept settings persistence.
- Simplified axis tick labels to `HH:mm` and retained full crosshair candle ranges.
- Added responsive toolbar and footer behavior for mobile layouts.

### Verification performed

- Frontend lint passed.
- All 46 frontend tests passed.
- TypeScript and production build passed.

### Safety notes

- Realtime synchronization remains read-only and unchanged; no trading behavior was added.

## 2026-06-30 - Day 30.9.4 collapsible chart navigation sidebars

### Work completed

- Added an icon-based primary navigation that collapses toward the left edge.
- Added active-route styling, keyboard focus treatment, and collapsed tooltips.
- Converted the chart watchlist into a right-side market rail with its own collapse control.
- Made the center chart grid expand when either sidebar is collapsed.
- Persisted both independent states in local storage through `useSyncExternalStore`.
- Added responsive fallbacks for the market rail on narrow screens.

### Verification performed

- Frontend lint passed.
- All 46 frontend tests passed.
- TypeScript, diff check, and production build passed.

### Safety notes

- This is frontend layout state only; market access remains read-only and no trading behavior changed.

## 2026-06-30 - Day 30.9.5 automatic chart recovery after browser pause

### Work completed

- Added automatic chart recovery when the document becomes visible, the window regains focus, or the browser returns online.
- Refetches the recent authoritative range for all visible timeframes to fill candles missed during browser throttling.
- Recreates every active WebSocket subscription after recovery.
- Debounces duplicate browser resume events and retains existing candles while backfill runs.

### Verification performed

- Added a unit test for hidden, debounced, and eligible visible recovery states.
- Frontend lint, tests, typecheck, and production build are required before deployment.

### Safety notes

- Recovery is read-only market-data synchronization and adds no trading or exchange-write path.

## 2026-06-30 - Days 30.14–30.18 custom timeframe and favorites

### Work completed

- Connected direct-versus-aggregate timeframe routing to candle storage.
- Added cached aggregation fallback from compatible provider-native base candles.
- Added week support and calendar-month `1M` aggregation.
- Allowed safe custom timeframe values through `/market/candles` and persisted chart layouts.
- Added a grouped timeframe dropdown with custom input and star favorites.
- Toolbar buttons now reflect the saved favorite list.
- Added 10-second visible-tab REST sync for aggregate-only timeframes while direct intervals retain WebSocket updates.

### Verification performed

- 93 market-data tests passed.
- 57 API tests passed.
- 52 frontend tests, lint, typecheck, and production build passed.

### Remaining follow-up

- Add source/aggregation response metadata and the `Aggregated from …` window label.

### Safety notes

- All provider operations remain read-only; no live trading or exchange write was introduced.

## 2026-06-30 - Day 30.9.6 realtime candle open continuity repair

### Root cause

- A shared latest price from any active timeframe was mutating the final candle's close/high/low in every chart.
- Only the latest realtime candle was retained, so a previous live bucket could disappear before REST backfill.
- Reload appeared correct because authoritative historical candles replaced the temporary frontend state.

### Work completed

- Removed cross-timeframe OHLC synchronization.
- Added bounded per-symbol/timeframe realtime candle buffers.
- Reconciled exactly contiguous next-candle opens to the previous close while preserving genuine market gaps.
- Applied duration handling across standard and custom minute/hour/day/week/month values.

### Verification performed

- Added transition, real-gap, multi-timeframe, and consecutive-buffer regression tests.
- 55 frontend tests, lint, typecheck, and production build passed.

### Safety notes

- This only corrects read-only chart rendering; provider storage and trading behavior are unchanged.

## 2026-06-30 - Day 30.19 aggregation cache verification

### Work completed

- Added typed candle response metadata for provider, market type, aggregation, base timeframe, cache hit, and fetched ranges.
- Preserved a list-only service method for internal compatibility while the HTTP API returns a metadata envelope.
- Added exact aggregate target-cache verification and repeated-request coverage.
- Added direct/aggregated source labels to each chart window with cache diagnostics in the tooltip.

### Verification performed

- Repeated aggregate requests prove the second request makes no provider call, commit, or upsert.
- 94 market-data tests passed.
- 56 frontend tests, lint, and typecheck passed.
- Live XAUUSD `7m` verification returned miss/fetched `1` on the first uncached request, hit/fetched `0` on the second, and identical 30-candle payloads.

### Safety notes

- Metadata and cache behavior are read-only; no exchange write or trading path changed.

## 2026-06-30 - Custom timeframe ordering polish

### Work completed

- Added deterministic duration-based sorting for preset and custom timeframes.
- Favorite buttons now reorder automatically after add/remove operations.
- Favorited custom timeframes are included in every chart-window timeframe selector.
- Options are deduplicated while the active non-favorite custom timeframe remains selectable.

### Verification performed

- Added coverage proving `5m`, `6m`, `15m`, `1h`, `2w`, `1M` ordering.
- 57 frontend tests, lint, typecheck, and production build passed.
