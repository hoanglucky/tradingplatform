trading-framework/
│
├── apps/
│   ├── web/                  # Next.js frontend
│   └── api/                  # FastAPI backend
│
├── packages/
│   ├── shared/               # type/schema dùng chung
│   └── ui/                   # component UI dùng lại
│
├── services/
│   ├── market-data/          # lấy dữ liệu nến/giá
│   ├── strategy-engine/      # tính tín hiệu
│   ├── backtest-engine/      # chạy backtest
│   ├── paper-trading/        # tài khoản demo
│   ├── alert-engine/         # cảnh báo
│   └── exchange-adapters/    # Binance/Bybit adapter
│
├── infra/
│   ├── docker/
│   ├── nginx/
│   └── deployment/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   └── codex-tasks.md
│
├── docker-compose.yml
├── .env.example
├── README.md
└── Makefile
# Framework Snapshot

## Current state

The repository is a scaffolded trading MVP framework with:

- Next.js web app in `apps/web`
- FastAPI backend in `apps/api`
- PostgreSQL and Redis through Docker Compose
- Shared TypeScript contracts in `packages/shared`
- Shared UI primitives in `packages/ui`
- Service stubs for each trading domain under `services/`
- Infrastructure bootstrap files under `infra/`
- Architecture and task documentation under `docs/`

## Runtime boundaries

Frontend:

- Reads backend module and safety status.
- Displays a first-pass dashboard foundation.

Backend API:

- Exposes `/health`, `/safety`, and `/modules`.
- Loads environment configuration through Pydantic settings.
- Keeps trading mode and exchange write status visible.

Domain services:

- Each service currently exposes health and capabilities endpoints.
- Business logic is intentionally still minimal.
- Service boundaries are ready for incremental implementation.

Database:

- `infra/postgres/init.sql` creates initial tables for service events, candles, backtest runs, and paper orders.

Redis:

- Initial channel recommendations are documented in `infra/redis/README.md`.

## Safety posture

This framework is paper-first.

Current defaults:

- Live trading disabled.
- Exchange writes disabled.
- Exchange adapter mode read-only.
- No real-money order execution implemented.

## Review checkpoints

- Confirm folder structure matches the product roadmap.
- Confirm module names are stable before implementing internal APIs.
- Confirm route names are acceptable before frontend grows around them.
- Confirm Docker Compose service topology before adding migrations and queues.
- Confirm safety defaults before any exchange credential work.

## Next implementation targets

1. Harden `apps/api` folder structure for Day 2.
2. Add Alembic migrations.
3. Add API docs for endpoint contracts.
4. Add database docs for schema ownership.
5. Implement first market data provider in read-only mode.
