# Trading Framework

A production-ready monorepo foundation for a web trading MVP. It includes a Next.js frontend, FastAPI backend, PostgreSQL, Redis, Docker Compose, and modular services for market data, indicators, strategies, backtesting, paper trading, alerts, and exchange adapters.

## Safety Defaults

- Real-money live trading is not implemented.
- Exchange adapters are read-only by default.
- Write-capable exchange integration is blocked unless a future implementation explicitly enables it with `ENABLE_LIVE_TRADING=true` and `ENABLE_EXCHANGE_WRITES=true`.
- The default trading mode is `paper`.

## Repository Layout

```text
apps/web                  Next.js frontend
apps/api                  FastAPI backend API
packages/shared           Shared TypeScript domain contracts
packages/ui               Shared UI primitives
services/market-data      Market ingestion and normalization service
services/indicator-engine Indicator calculation service
services/strategy-engine  Strategy signal service
services/backtest-engine  Historical simulation service
services/paper-trading    Simulated execution and portfolio service
services/alert-engine     Notification routing service
services/exchange-adapters Read-only exchange adapter service
infra                     Database and infrastructure config
docs                      Architecture and operational docs
```

## Quick Start

```bash
cd trading-framework
make setup
make dev
```

The local stack exposes:

- Web app: <http://localhost:3000>
- API: <http://localhost:8000>
- API docs: <http://localhost:8000/docs>
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Development Commands

```bash
make setup   # create .env and install frontend dependencies
make dev     # start all services with Docker Compose
make down    # stop containers
make logs    # tail logs
make web     # run Next.js outside Compose
make api     # run FastAPI outside Compose
make test    # run backend tests
make lint    # run configured linters
```

## Next Milestones

1. Add database migrations with Alembic.
2. Add durable event contracts between services.
3. Implement read-only exchange market data adapters.
4. Build paper order lifecycle and portfolio accounting.
5. Add backtest result persistence and report views.

