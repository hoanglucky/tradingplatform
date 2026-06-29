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

Review the Day 30.3 multi-timeframe grid UI.

Focus areas:

- Confirm `MultiTimeframeGrid` renders only visible enabled windows.
- Confirm 1/2/4/8 layouts use responsive 1/2/4-column rules.
- Confirm every window displays the one shared symbol.
- Confirm timeframe changes update only the targeted window ID.
- Confirm Reviewed changes update only the targeted window ID.
- Confirm placeholder regions do not fetch candles yet.
- Confirm the old single live chart remains rendered below the grid.
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
