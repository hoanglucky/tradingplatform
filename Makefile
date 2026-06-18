SHELL := /bin/bash

.PHONY: help setup dev down logs ps web api test lint format clean

help:
	@printf "Available commands:\n"
	@printf "  make setup   Create .env and install frontend dependencies\n"
	@printf "  make dev     Start API and web locally through npm\n"
	@printf "  make compose Start the full local stack with Docker Compose\n"
	@printf "  make down    Stop the local stack\n"
	@printf "  make logs    Tail Docker Compose logs\n"
	@printf "  make ps      Show service status\n"
	@printf "  make web     Run the Next.js app locally\n"
	@printf "  make api     Run the FastAPI app locally\n"
	@printf "  make test    Run backend tests\n"
	@printf "  make lint    Run available linters\n"
	@printf "  make format  Format Python code with ruff if available\n"

setup:
	@test -f .env || cp .env.example .env
	npm install

dev:
	npm run dev

compose:
	docker compose up --build

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

test:
	cd apps/api && pytest

lint:
	npm run lint
	cd apps/api && ruff check app tests

format:
	cd apps/api && ruff format app tests

clean:
	docker compose down -v
	rm -rf node_modules apps/web/node_modules apps/web/.next
