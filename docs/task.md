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
- [ ] Backend tests verified in local Python/Docker environment
- [ ] npm audit reviewed or accepted for current Next.js transitive advisory

## Current review task

Review the Day 1 foundation scaffold.

Focus areas:

- Confirm repo structure matches product plan.
- Confirm Docker Compose service names and dependencies are clear.
- Confirm `.env.example` keeps all trading safety switches off by default.
- Confirm exchange adapters are read-only by default.
- Confirm no live order execution exists.
- Confirm `apps/api` route shape is acceptable before deeper backend work.
- Confirm `apps/web` first screen is a useful MVP dashboard foundation.

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
