# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Quero Plantão API** - A REST API for medical shift management and marketplace matching. HR Tech infrastructure connecting healthcare professionals with shift opportunities. Built with Clean Architecture and multi-tenant data isolation.

## Technology Stack

- **Framework**: FastAPI 0.128.0+ with Uvicorn
- **Python**: 3.14.2+
- **Database**: PostgreSQL (Neon-optimized) with SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Migrations**: Alembic
- **Messaging**: FastStream with LavinMQ/RabbitMQ
- **Auth**: Firebase Auth (external BFF) + JWT validation
- **Logging**: Structlog (JSON in prod, colored console in dev)

## Essential Commands

```bash
# Development
make install          # Install dependencies
make dev              # Install with dev extras
make run              # Start API (uvicorn with reload)
make worker           # Start FastStream workers
make docker-up        # Start PostgreSQL + LavinMQ
make docker-down      # Stop containers

# Quality Assurance
make lint             # Ruff + MyPy
make format           # Ruff format + fix
make test             # Run pytest
make test-cov         # Test + coverage report
make pre-commit       # Run all pre-commit hooks

# Database Migrations
make migrate-create msg="description"  # Generate migration
make migrate                            # Apply all pending
make migrate-rollback                   # Revert last
```

## Architecture

### Module Structure (Clean Architecture)

Each feature module in `src/modules/` follows:

```
module/
├── domain/
│   ├── models/              # SQLModel entities + enums
│   └── schemas/             # Pydantic schemas (request/response)
├── infrastructure/
│   └── repositories/        # Data access layer
├── presentation/
│   └── routes.py            # FastAPI router
└── use_cases/               # Business logic orchestration
```

### Key Directories

- `src/app/` - Core application (main.py, config, security, dependencies, middlewares)
- `src/shared/` - Shared code (base models, mixins, database connection, base repository)
- `src/modules/` - Feature modules (auth, professionals, organizations, contracts, units)
- `src/workers/` - FastStream async workers
- `alembic/` - Database migrations
- `docs/` - Module documentation

### Critical Files

- `src/app/main.py` - FastAPI app creation and lifespan
- `src/app/config.py` - Pydantic settings management
- `src/app/security.py` - JWT validation
- `src/shared/domain/models/mixins.py` - Reusable model mixins
- `src/shared/infrastructure/database/connection.py` - DB engine setup
- `src/shared/infrastructure/repositories/base.py` - Generic CRUD base class

## Core Patterns

### Database Design

- **UUID v7** for primary keys (time-ordered)
- **Soft deletes** via `SoftDeleteMixin` (add `deleted_at IS NULL` filters)
- **Multi-tenancy** via `organization_id` field - always filter by org for professional data
- **Mixins**: PrimaryKeyMixin, TimestampMixin, TrackingMixin, SoftDeleteMixin, AddressMixin, VerificationMixin, MetadataMixin, VersionMixin

### Dependency Injection

```python
# Database session
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]

# Authenticated user context
CurrentContext = Annotated[RequestContext, Depends(get_current_context)]

# In endpoint:
async def get_profile(session: SessionDep, context: CurrentContext):
    user_id = context.user_id
    has_admin = context.has_role("admin")
```

### Async-First

All database operations use async patterns:
```python
async with session.begin():
    result = await session.execute(query)
```

## Code Quality

- **Ruff**: Linting & formatting (line length: 120, double quotes)
- **MyPy**: Strict mode enabled - type everything, avoid `Any`
- **Pre-commit**: Hooks for format, lint, trailing whitespace, YAML validation

## Testing

- `pytest` with asyncio_mode="auto"
- Factory-boy for test data (`tests/factories/`)
- Structure: `tests/unit/`, `tests/integration/`, `tests/e2e/`

## Business Domain

**Key Entities:**
- **Organization**: Tenant root (hospital, clinic network)
- **Unit**: Physical location (branch, department)
- **Professional**: Healthcare worker (scoped to organization)
- **Contract**: Employment/client agreements
- **Qualification**: Professional licenses/certifications

**Multi-tenancy**: Same CPF can exist in multiple orgs with different data. No cross-org visibility.

## Documentation

Detailed module docs in `/docs/modules/`:
- AUTH_MODULE.md, PROFESSIONALS_MODULE.md, ORGANIZATIONS_MODULE.md, CONTRACTS_MODULE.md, UNITS_MODULE.md
