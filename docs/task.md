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

Review the Day 5 developer commands polish.

Focus areas:

- Confirm `make dev`, `make up`, `make down`, and `make logs` exist.
- Confirm `make api-test` runs backend tests through Docker.
- Confirm `make web-test` runs frontend lint, typecheck, and build.
- Confirm `make lint` does not require host Python tooling.
- Confirm README command list matches Makefile.
- Confirm npm fallback commands exist for environments without `make`.
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
