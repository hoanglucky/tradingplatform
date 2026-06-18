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

Review the Day 4 Docker Compose setup hardening.

Focus areas:

- Confirm Docker Compose config validates with `.env.example`.
- Confirm API and web Dockerfiles exist.
- Confirm PostgreSQL, Redis, API, and web healthchecks are present.
- Confirm web waits for API health before starting.
- Confirm `.dockerignore` files exclude generated files, local env files, and dependency folders.
- Confirm domain service stubs are isolated behind the Compose `services` profile.
- Confirm Docker credential issue is documented and not mistaken for an app test failure.
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
docker compose run --rm api pytest
```

Current blocker:

- Docker can now pull `python:3.12-slim`.
- API image build now completes.
- `docker compose run --rm api pytest` passes.
- Host Python does not have `pip`/`venv`, so pytest cannot run directly on the host yet.
