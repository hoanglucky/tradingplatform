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
- [ ] Backend pytest completed in local Python/Docker environment
- [x] Backend syntax compile check passed
- [x] npm audit reviewed or accepted for current Next.js transitive advisory

## Current review task

Review the Day 2 FastAPI backend skeleton hardening.

Focus areas:

- Confirm `apps/api/app/api/router.py` is the central API router.
- Confirm routes live under `apps/api/app/api/routes`.
- Confirm `/health` stays lightweight.
- Confirm `/health/ready` checks PostgreSQL and Redis.
- Confirm `/safety` still blocks live trading and exchange writes by default.
- Confirm no exchange write or live trading execution was added.
- Confirm `docs/api.md` matches implemented endpoint contracts.

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
docker compose run --rm api pytest
```

Current blocker:

- Docker BuildKit failed resolving `python:3.12-slim` with `error getting credentials`.
- Host Python does not have `pip`/`venv`, so pytest cannot run directly on the host yet.
