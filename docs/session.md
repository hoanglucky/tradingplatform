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
