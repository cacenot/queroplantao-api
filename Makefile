.PHONY: install dev test test-cov lint format migrate migrate-create migrate-rollback run worker docker-up docker-down docker-logs clean pre-commit-install pre-commit help

## Install dependencies
install:
	uv sync

## Install with dev dependencies
dev:
	uv sync --all-extras

## Run tests
test:
	uv run pytest

## Run tests with coverage
test-cov:
	uv run pytest --cov=app --cov-report=html --cov-report=term

## Lint code
lint:
	uv run ruff check .
	uv run mypy app

## Format code
format:
	uv run ruff format .
	uv run ruff check --fix .

## Create a new migration
migrate-create:
	uv run alembic revision --autogenerate -m "$(msg)"

## Run migrations
migrate:
	uv run alembic upgrade head

## Rollback migration
migrate-rollback:
	uv run alembic downgrade -1

## Run the API server
run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Run the worker
worker:
	uv run python -m app.workers.main

## Start Docker services (PostgreSQL + LavinMQ)
docker-up:
	docker compose up -d

## Stop Docker services
docker-down:
	docker compose down

## View Docker logs
docker-logs:
	docker compose logs -f

## Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete

## Install pre-commit hooks
pre-commit-install:
	uv run pre-commit install

## Run pre-commit on all files
pre-commit:
	uv run pre-commit run --all-files

## Show this help message
help:
	@grep -E '^## ' Makefile | sed 's/## //'
