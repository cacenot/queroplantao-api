# Makefile for Quero Plantão MCP Server
# Uses uv as package manager

.PHONY: help install test run run-sse run-debug clean lint format check-env setup

# Default target
help: ## Show this help message
	@echo "Quero Plantão MCP Server - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Installation and setup
install: ## Install dependencies with uv
	uv sync

setup: ## Setup development environment (install + create .env)
	uv sync
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file from .env.example"; \
		echo "⚠️  Please edit .env and add your OPENAI_API_KEY"; \
	else \
		echo "✅ .env file already exists"; \
	fi

check-env: ## Check if environment is properly configured
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run 'make setup' first."; \
		exit 1; \
	fi
	@if ! grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then \
		echo "⚠️  OPENAI_API_KEY not set in .env file."; \
		echo "   Edit .env and add your OpenAI API key."; \
	else \
		echo "✅ Environment configured correctly"; \
	fi

# Testing
test: ## Run the comprehensive test suite
	uv run python test_server.py

test-quick: ## Run a quick import test
	@uv run python -c "\
	from queroplantao_mcp.server import mcp; \
	from queroplantao_mcp.config import validate_project_structure; \
	structure = validate_project_structure(); \
	all_valid = all(structure.values()); \
	print(f'✅ Server imports: OK'); \
	print(f'✅ Tools registered: {len(mcp._tool_manager._tools)}'); \
	print(f'✅ Project structure: {\"OK\" if all_valid else \"ISSUES\"}'); \
	"

# Running the server
run: check-env ## Run MCP server in stdio mode (for Claude Desktop)
	@echo "🚀 Starting MCP server in stdio mode..."
	@echo "   Use this with Claude Desktop or other MCP clients"
	uv run mcp-server

run-sse: check-env ## Run MCP server in SSE mode (HTTP server)
	@echo "🚀 Starting MCP server in SSE mode..."
	@echo "   Server will be available at http://127.0.0.1:8080"
	uv run mcp-server --sse

run-debug: check-env ## Run MCP server with debug logging
	@echo "🚀 Starting MCP server in debug mode..."
	OPENAI_API_KEY=$$(grep OPENAI_API_KEY .env | cut -d'=' -f2) \
	MCP_LLM_MODEL=gpt-4o-mini \
	MCP_LLM_TEMPERATURE=0.1 \
	MCP_LLM_MAX_TOKENS=4096 \
	uv run mcp-server

# Development tools
lint: ## Run ruff linter
	uv run ruff check .

format: ## Format code with ruff
	uv run ruff format .

fix: ## Auto-fix linting issues
	uv run ruff check . --fix
	uv run ruff format .

# Cleanup
clean: ## Clean up cache files and temporary data
	rm -rf .ruff_cache/
	rm -rf __pycache__/
	rm -rf src/queroplantao_mcp/__pycache__/
	rm -rf src/queroplantao_mcp/*/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

clean-all: clean ## Clean everything including virtual environment
	rm -rf .venv/
	rm -rf uv.lock

# Information
info: ## Show server information
	@echo "Quero Plantão MCP Server"
	@echo "========================"
	@echo "Python version: $$(uv run python --version)"
	@echo "Project root: $$(pwd)"
	@echo ""
	@echo "Environment check:"
	@if [ -f .env ]; then echo "  ✅ .env file exists"; else echo "  ❌ .env file missing"; fi
	@if grep -q "OPENAI_API_KEY=sk-" .env 2>/dev/null; then echo "  ✅ OpenAI API key configured"; else echo "  ⚠️  OpenAI API key not configured"; fi
	@echo ""
	@echo "Run 'make test' to verify everything is working"

# Development workflow
dev: setup test info ## Setup, test, and show info (recommended first run)

# Production deployment helpers
build: ## Build for production (if needed)
	@echo "MCP server doesn't require building - it's pure Python"
	@echo "Just ensure dependencies are installed with 'make install'"

# Docker helpers (if using Docker in the future)
docker-build: ## Build Docker image (future use)
	@echo "Docker support not implemented yet"

docker-run: ## Run with Docker (future use)
	@echo "Docker support not implemented yet"