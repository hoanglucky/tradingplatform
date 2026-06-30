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

Review the TradingView candle opening-time alignment correction.

Focus areas:

- Confirm Lightweight Charts coordinates use unshifted provider opening timestamps.
- Confirm a Bangkok 5m candle opened at 14:55 is selected as 14:55, not 15:00.
- Confirm 1m candles no longer gain an extra minute on the crosshair.
- Confirm UTC and Asia/Bangkok formatting only changes display timezone.
- Confirm derived close-time helpers do not alter historical or realtime candle payloads.
- Confirm every layout window uses the same opening-time convention.
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
