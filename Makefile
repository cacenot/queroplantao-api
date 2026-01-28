.PHONY: install dev test test-cov lint format migrate migrate-create migrate-rollback run worker docker-up docker-down docker-logs clean pre-commit-install pre-commit firebase-token help client-enums client-errors client-generate client-all client-release client-version-patch client-version-minor client-version-major

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
	uv run mypy src

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

## Generate Firebase Auth token for API testing
firebase-token:
	@set -a && [ -f .env ] && . ./.env && set +a; uv run python scripts/generate_firebase_token.py

# ============================================================================
# API Client Generation
# ============================================================================

CLIENT_DIR := packages/api-client

## Generate TypeScript enums from Python
client-enums:
	@echo "🔄 Generating TypeScript enums..."
	@uv run python scripts/generate_ts_enums.py

## Generate TypeScript error codes and messages
client-errors:
	@echo "🔄 Generating TypeScript error codes..."
	@uv run python scripts/generate_ts_error_codes.py

## Generate TypeScript API client from OpenAPI (requires API running)
client-generate:
	@echo "🔄 Generating TypeScript API client..."
	@echo "Starting API server on port 8099..."
	@uv run uvicorn src.app.main:app --port 8099 & echo $$! > .server.pid
	@sleep 4
	@echo "Fetching OpenAPI schema..."
	@curl -s http://localhost:8099/openapi.json > $(CLIENT_DIR)/openapi.json || (kill `cat .server.pid` 2>/dev/null; rm -f .server.pid; exit 1)
	@echo "Running orval..."
	@cd $(CLIENT_DIR) && npm run generate || (kill `cat .server.pid` 2>/dev/null; rm -f .server.pid; exit 1)
	@kill `cat .server.pid` 2>/dev/null || true
	@rm -f .server.pid
	@echo "✅ Client generated!"

## Generate everything: enums + errors + client
client-all: client-enums client-errors client-generate
	@echo "✅ Full API client package generated!"

## Release API client (interactive)
client-release:
	@./scripts/release_api_client.sh

## Bump API client patch version (0.1.0 -> 0.1.1)
client-version-patch:
	@cd $(CLIENT_DIR) && pnpm run version:patch
	@bash scripts/sync_client_version.sh
	@echo "✅ Version bumped to $$(cd $(CLIENT_DIR) && node -p "require('./package.json').version")"

## Bump API client minor version (0.1.0 -> 0.2.0)
client-version-minor:
	@cd $(CLIENT_DIR) && pnpm run version:minor
	@bash scripts/sync_client_version.sh
	@echo "✅ Version bumped to $$(cd $(CLIENT_DIR) && node -p "require('./package.json').version")"

## Bump API client major version (0.1.0 -> 1.0.0)
client-version-major:
	@cd $(CLIENT_DIR) && pnpm run version:major
	@bash scripts/sync_client_version.sh
	@echo "✅ Version bumped to $$(cd $(CLIENT_DIR) && node -p "require('./package.json').version")"

## Show this help message
help:
	@grep -E '^## ' Makefile | sed 's/## //'
