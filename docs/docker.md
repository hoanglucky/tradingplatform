# Docker

## Local stack

Create the local environment file:

```bash
cp .env.example .env
```

Start the core Compose stack:

```bash
make compose
```

Equivalent npm command:

```bash
npm run dev:compose
```

The default Compose stack includes:

- `postgres`
- `redis`
- `api`
- `web`

Domain service stubs are behind the `services` profile so Day 4 stays focused on the core development stack. To start everything:

```bash
make compose-services
```

Equivalent raw Compose command:

```bash
docker compose --profile services up --build
```

Expected local URLs:

- Frontend: `http://localhost:2000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Health checks

Docker Compose includes health checks for:

- PostgreSQL via `pg_isready`
- Redis via `redis-cli ping`
- API via `GET /health`
- Web via `GET /`

The web service waits for the API health check before starting.

## Build contexts

The repository includes `.dockerignore` files to keep build contexts small and avoid copying:

- `node_modules`
- `.next`
- Python cache files
- local `.env`
- local database volumes

## Verification commands

Validate Compose config without starting containers:

```bash
test -f .env || cp .env.example .env
docker compose config --quiet
```

Run backend tests through Compose:

```bash
docker compose run --rm api pytest
```

Show container status:

```bash
docker compose ps
```

Tail logs:

```bash
docker compose logs -f
```

Stop containers:

```bash
docker compose down
```

## Known Docker Desktop issue

On this development machine, Docker BuildKit previously failed while resolving `python:3.12-slim`:

```txt
failed to solve: error getting credentials
```

This is a Docker credential/pull issue rather than an application test failure. Fix by refreshing Docker Desktop authentication or credential helper state, then retry:

```bash
docker pull python:3.12-slim
docker compose run --rm api pytest
```

Current follow-up note:

- `docker pull python:3.12-slim` later succeeded.
- `docker compose build api` later succeeded.
- `docker compose run --rm api pytest` later passed with 4 tests.
- The remaining Day 4 check is long-running `docker compose up --build` accessibility verification for web/API.
