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
