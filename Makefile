SHELL := /bin/bash

.PHONY: help setup dev up compose compose-services down logs ps web api api-test web-test test lint format clean

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
	@printf "  make web-test Run frontend checks\n"
	@printf "  make test    Run API and web checks\n"
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
	docker compose run --rm api pytest

web-test:
	npm --workspace apps/web run lint
	npm --workspace apps/web run typecheck
	npm --workspace apps/web run build

test: api-test web-test

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
