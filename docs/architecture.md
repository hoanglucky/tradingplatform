# Architecture

## Overview

Trading Framework is a modular, paper-first trading MVP foundation. The web app provides the operator experience, the FastAPI API exposes product-facing contracts, PostgreSQL stores durable state, Redis supports low-latency events and cache data, and each domain service owns one bounded area of trading logic.

Live real-money trading is intentionally out of scope for this scaffold. Exchange adapters are read-only by default, and the provided order endpoint rejects writes.

## Implementation Status

Current scaffold status as of 2026-06-18:

- Monorepo structure has been created.
- Next.js frontend scaffold exists in `apps/web`.
- FastAPI backend scaffold exists in `apps/api`.
- Docker Compose defines PostgreSQL, Redis, API, web, and domain services.
- Each domain service has a minimal FastAPI health/capabilities interface.
- PostgreSQL bootstrap SQL exists in `infra/postgres/init.sql`.
- Redis usage notes exist in `infra/redis/README.md`.
- The exchange adapter service blocks order writes by default.

Open architecture work:

- Add Alembic migrations.
- Define durable event schemas.
- Decide whether Redis pub/sub is enough for MVP or if a durable queue is needed.
- Add API and database contract docs.
- Add authentication and authorization boundaries before user-specific data is introduced.

## Components

| Component | Responsibility |
| --- | --- |
| `apps/web` | Next.js frontend for dashboards, module status, strategy views, backtest results, and paper portfolio screens. |
| `apps/api` | FastAPI backend for authentication-ready API boundaries, orchestration, safety status, and product-facing endpoints. |
| `packages/shared` | Shared TypeScript domain contracts used by frontend packages. |
| `packages/ui` | Shared UI primitives for the web app. |
| `services/market-data` | Normalizes external market data into quotes, candles, and order book snapshots. |
| `services/indicator-engine` | Computes indicators from normalized market data. |
| `services/strategy-engine` | Evaluates strategies and emits signals for paper trading or backtesting. |
| `services/backtest-engine` | Replays historical data and calculates performance metrics. |
| `services/paper-trading` | Simulates order placement, fills, positions, balances, and PnL. |
| `services/alert-engine` | Routes notifications for signals, failures, and risk events. |
| `services/exchange-adapters` | Provides read-only exchange connectivity until write support is explicitly designed later. |

## Data Flow

1. Exchange adapters fetch read-only market data or account snapshots.
2. Market data normalizes raw exchange payloads and publishes events.
3. Indicator engine consumes market events and publishes indicator updates.
4. Strategy engine consumes market and indicator events, then emits strategy signals.
5. Paper trading consumes signals and simulates orders, fills, positions, and PnL.
6. Backtest engine uses historical candles and strategy definitions to produce repeatable simulation results.
7. Alert engine dispatches notifications for selected signals, risk states, and system failures.
8. API exposes stable product contracts to the Next.js frontend.

## Storage

PostgreSQL is the source of truth for durable entities such as candles, backtest runs, paper orders, positions, strategy definitions, and audit records. Redis is the initial event and cache layer for local development. If the system grows, Redis pub/sub can be replaced or complemented with Kafka, Redpanda, NATS, or another durable event log.

## Safety Model

The scaffold uses defense-in-depth defaults:

- `DEFAULT_TRADING_MODE=paper`
- `ENABLE_LIVE_TRADING=false`
- `ENABLE_EXCHANGE_WRITES=false`
- `EXCHANGE_ADAPTER_MODE=read_only`

Exchange write paths must check all safety switches. This repository currently includes no live order placement implementation.

## Deployment Notes

The Docker Compose setup is intended for local development. A production deployment should add:

- Secrets management instead of `.env` files.
- Database migrations with Alembic.
- TLS termination and authentication.
- Service-level health checks and metrics.
- Centralized logs and traces.
- CI gates for tests, type checks, and container builds.
