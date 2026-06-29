# Codex Task Framework

## Rule
- One task per branch.
- One feature per PR.
- Add tests before marking done.
- Never implement real-money live trading in MVP.
- Update docs after each module.

## Branch naming
- feature/backend-skeleton
- feature/market-data-provider
- feature/chart-component
- feature/strategy-engine
- feature/backtest-engine
- feature/paper-trading
- feature/alert-engine

## Done checklist
- [x] Code implemented
- [x] Tests added
- [x] Existing frontend checks pass
- [x] README/docs updated
- [x] No hardcoded secrets
- [x] No live trading execution
- [x] Backend pytest completed in Docker environment
- [x] Backend syntax compile check passed
- [x] npm audit reviewed or accepted for current Next.js transitive advisory

## Current review task

Review the Day 27 watchlist API.

Focus areas:

- Confirm all watchlist routes resolve ownership through `get_mvp_user`.
- Confirm the configured default watchlist is created idempotently.
- Confirm GET returns watchlist metadata and joined symbol details.
- Confirm POST normalizes symbol case and requires an active catalog symbol.
- Confirm duplicate item insertion returns `409` without duplicate rows.
- Confirm DELETE handles lowercase paths and returns `204` on success.
- Confirm missing catalog symbols and missing items return distinct `404` responses.
- Confirm tests isolate temporary users and do not modify the local MVP watchlist.
- Confirm no live trading or exchange write behavior was added.

## Verification commands

```bash
cd trading-framework
npm run lint
npm run typecheck
npm --workspace apps/web run build
test -f .env || cp .env.example .env
docker compose config --quiet
```

Backend tests:

```bash
npm run api-test
```

Market-data service tests:

```bash
npm run market-data-test
```

Seed command:

```bash
npm run seed
```

Database migrations:

```bash
npm run db:upgrade
npm run db:current
```

Current blocker:

- Docker can now pull `python:3.12-slim`.
- API image build now completes.
- `npm run api-test` applies Alembic migrations and runs pytest.
- API tests run with `APP_ENV=test` so SQLAlchemy uses `NullPool` and avoids asyncpg event-loop reuse issues in pytest.
- Host Python does not have `pip`/`venv`, so pytest cannot run directly on the host yet.
