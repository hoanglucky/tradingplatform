SHELL := /bin/bash

.PHONY: help setup dev up compose compose-services down logs ps web api api-test market-data-test structure-test web-test test db-upgrade db-downgrade db-current db-revision seed lint format clean

help:
	@printf "Available commands:\n"
	@printf "  make setup   Create .env and install frontend dependencies\n"
	@printf "  make dev     Start API and web locally through npm\n"
	@printf "  make up      Start the core Docker Compose stack in the background\n"
	@printf "  make compose Start the core Docker Compose stack\n"
	@printf "  make compose-services Start core stack plus domain service stubs\n"
	@printf "  make down    Stop the local stack\n"
	@printf "  make logs    Tail Docker Compose logs\n"
	@printf "  make ps      Show service status\n"
	@printf "  make web     Run the Next.js app locally\n"
	@printf "  make api     Run the FastAPI app locally\n"
	@printf "  make api-test Run backend tests in Docker\n"
	@printf "  make market-data-test Run market-data service tests in Docker\n"
	@printf "  make structure-test Run structure-engine tests in Docker\n"
	@printf "  make web-test Run frontend checks\n"
	@printf "  make test    Run API and web checks\n"
	@printf "  make db-upgrade Apply Alembic migrations\n"
	@printf "  make db-current Show current Alembic revision\n"
	@printf "  make seed    Seed default market symbols\n"
	@printf "  make lint    Run available linters\n"
	@printf "  make format  Format Python code with ruff if available\n"

setup:
	@test -f .env || cp .env.example .env
	npm install

dev:
	npm run dev

up:
	docker compose up --build -d

compose:
	docker compose up --build

compose-services:
	docker compose --profile services up --build

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

web:
	npm --workspace apps/web run dev

api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

api-test:
	@test -f .env || cp .env.example .env
	docker compose build api
	docker compose run --rm api sh -c "APP_ENV=test alembic upgrade head && APP_ENV=test pytest"

web-test:
	npm --workspace apps/web run lint
	npm --workspace apps/web run test
	npm --workspace apps/web run typecheck
	npm --workspace apps/web run build

market-data-test:
	@test -f .env || cp .env.example .env
	docker compose --profile services build api market-data
	docker compose run --rm api alembic upgrade head
	docker compose --profile services run --rm market-data sh -c "APP_ENV=test pytest"

structure-test:
	docker compose --profile services build structure-engine
	docker compose --profile services run --rm structure-engine pytest

test: api-test market-data-test web-test

db-upgrade:
	docker compose run --rm api alembic upgrade head

db-downgrade:
	docker compose run --rm api alembic downgrade -1

db-current:
	docker compose run --rm api alembic current

db-revision:
	docker compose run --rm api alembic revision --autogenerate -m "$(message)"

seed:
	@test -f .env || cp .env.example .env
	docker compose build api
	docker compose run --rm api sh -c "alembic upgrade head && python -m app.cli.seed_symbols"

lint:
	npm run lint
	docker compose build api
	docker run --rm trading-framework-api ruff check app tests

format:
	docker compose build api
	docker run --rm trading-framework-api ruff format app tests

clean:
	docker compose down -v
	rm -rf node_modules apps/web/node_modules apps/web/.next
