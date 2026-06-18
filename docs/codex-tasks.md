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

- Run backend pytest in Docker or a Python environment with `pip`/`venv`.
- Docker pytest was attempted but blocked by Docker BuildKit credential resolution for `python:3.12-slim`.

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
- Added `docs/docker.md` with Compose usage, health checks, verification commands, and Docker credential troubleshooting.
- Updated README and task docs.

Verified:

- `docker compose config --quiet`
- `docker pull python:3.12-slim`
- PostgreSQL and Redis containers started during `docker compose run --build --rm api pytest`

Pending verification:

- Full `docker compose up --build`.
- Backend pytest through Docker.
- The latest Compose pytest attempt stalled during Python dependency installation in the API image before pytest started.

## Next task candidate

### Day 5 - Developer commands polish

Suggested scope:

- Add Makefile aliases expected by the plan, such as `make up`, `make api-test`, and `make web-test`.
- Ensure README command list matches Makefile.
- Keep Docker and local npm workflows separate and clear.
