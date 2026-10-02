BACKEND := backend
FRONTEND := frontend
API_PORT := 8010

.PHONY: install infra up down migrate api worker web run check check-backend check-frontend test types

install:
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && pnpm install

infra:
	docker compose up -d --wait db redis

up:
	docker compose --profile app up -d --build

down:
	docker compose --profile app down

migrate:
	cd $(BACKEND) && uv run alembic upgrade head && uv run python -m app.cli.seed_examples

api:
	cd $(BACKEND) && uv run uvicorn main:app --reload --port $(API_PORT)

worker:
	cd $(BACKEND) && uv run celery -A app.worker.celery_app worker --loglevel=info --pool=solo

web:
	cd $(FRONTEND) && pnpm dev

run:
	cd $(BACKEND) && uv run python -m app.cli "$(IDEA)"

test:
	cd $(BACKEND) && uv run pytest

check: check-backend check-frontend

check-backend:
	cd $(BACKEND) && uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run pytest

check-frontend:
	cd $(FRONTEND) && pnpm lint && pnpm typecheck && pnpm build

types:
	cd $(BACKEND) && uv run python -m app.cli.export_openapi > ../$(FRONTEND)/openapi.json
	cd $(FRONTEND) && pnpm gen:api
