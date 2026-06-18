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

### Day 3 - Next.js frontend skeleton review and dashboard hardening

Suggested scope:

- Add stable app layout with sidebar/topbar if desired.
- Add API health/readiness display.
- Add empty dashboard states for chart/watchlist areas.
- Keep no live trading controls visible.
