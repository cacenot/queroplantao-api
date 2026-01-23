# Copilot Instructions - Quero Plantão API

## Project Overview

REST API for medical shift management (HR Tech). Multi-tenant architecture with organization-scoped data isolation. Built with FastAPI + SQLModel + PostgreSQL.

## Essential Commands

```bash
make run              # Start API with uvicorn --reload
make worker           # Start FastStream workers
make docker-up        # Start PostgreSQL + LavinMQ
make lint             # Ruff + MyPy
make format           # Ruff format + fix
make test             # pytest
make migrate-create msg="description"  # New migration
make migrate          # Apply migrations
```

## Architecture

### Module Structure (`src/modules/{module}/`)
```
domain/
├── models/           # SQLModel entities + enums
└── schemas/          # Pydantic DTOs (Create, Update, Response)
infrastructure/
├── repositories/     # Data access (extends BaseRepository + mixins)
└── filters/          # FilterSet + SortingSet for pagination
presentation/
└── routes.py         # FastAPI router
use_cases/            # Business logic orchestration
```

### Key Base Classes
- `BaseRepository[ModelT]` - CRUD operations with pagination ([base.py](src/shared/infrastructure/repositories/base.py))
- `SoftDeletePaginationMixin` - Soft delete + filtering/sorting support ([mixins.py](src/shared/infrastructure/repositories/mixins.py))
- Model mixins: `PrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteMixin`, `TrackingMixin`, `VerificationMixin`

## Core Patterns

### Multi-Tenancy (CRITICAL)
All professional/contract data is scoped by `organization_id`. Always filter:
```python
def _base_query_for_organization(self, organization_id: UUID):
    return self._exclude_deleted().where(Model.organization_id == organization_id)
```

### Soft Delete
Models with `SoftDeleteMixin` use `deleted_at` column. Repositories must:
- Use `_exclude_deleted()` in all queries
- Create partial unique indexes: `postgresql_where=text("deleted_at IS NULL")`

### Use Case Pattern
```python
class CreateEntityUseCase:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = EntityRepository(session)

    async def execute(self, organization_id: UUID, data: EntityCreate) -> Entity:
        # 1. Validate business rules
        # 2. Check conflicts/uniqueness
        # 3. Create entity via repository
        return await self.repository.create(entity)
```

### Update with PATCH Semantics
```python
update_data = data.model_dump(exclude_unset=True)  # Only changed fields
for field, value in update_data.items():
    setattr(entity, field, value)
```

### Pagination with Filters
```python
# Repository method
async def list_for_organization(
    self, organization_id: UUID, pagination: PaginationParams,
    *, filters: EntityFilter | None = None, sorting: EntitySorting | None = None
) -> PaginatedResponse[Entity]:
    query = self._base_query_for_organization(organization_id)
    return await self.list_paginated(pagination, filters=filters, sorting=sorting, base_query=query)
```

### FilterSet/SortingSet Definition
```python
class EntityFilter(FilterSet):
    search: Annotated[str | None, Query(default=None)] = None
    is_active: Annotated[bool | None, Query(default=None)] = None
    
    class Config:
        search_fields = ["name", "email"]  # OR search across columns
        field_columns = {"is_active": "is_active"}

class EntitySorting(SortingSet):
    id: Annotated[str | None, Query(default=None)] = None  # UUID v7 = time-ordered
    created_at: Annotated[str | None, Query(default=None)] = None
    
    class Config:
        default_sort = [("id", "asc")]
```

### Use Case File Organization
Use cases are organized in submodules per entity. Each use case lives in its own file with a descriptive name:

```
use_cases/
├── __init__.py                    # Re-exports all use cases
└── {entity}/                      # Submodule per entity
    ├── __init__.py                # Re-exports entity's use cases
    ├── {entity}_create_use_case.py
    ├── {entity}_update_use_case.py
    ├── {entity}_delete_use_case.py
    ├── {entity}_get_use_case.py
    └── {entity}_list_use_case.py
```

**Naming Convention:**
- File: `{entity}_{action}_use_case.py` (e.g., `professional_document_create_use_case.py`)
- Class: `{Action}{Entity}UseCase` (e.g., `CreateProfessionalDocumentUseCase`)

**Why this structure:**
- Easy to search files by entity or action
- Each file has a single responsibility
- Submodule `__init__.py` re-exports for clean imports

### Presentation Layer (Routes)

Routes are organized in a `routes/` submodule with one file per entity:

```
presentation/
├── routes.py                          # Main router - aggregates all sub-routers
├── dependencies/
│   ├── __init__.py                    # Re-exports all dependencies
│   ├── {entity}.py                    # Use case factories for entity
│   └── ...
└── routes/
    ├── __init__.py                    # Re-exports all routers
    ├── {entity}_routes.py             # Routes for entity
    └── ...
```

**Naming Convention:**
- Route file: `{entity}_routes.py` (e.g., `organization_professional_routes.py`)
- Dependency file: `{entity}.py` (e.g., `organization_professional.py`)

**Dependencies Pattern:**
```python
# Use case factory function
def get_create_entity_use_case(session: SessionDep) -> CreateEntityUseCase:
    return CreateEntityUseCase(session)

# Type alias for cleaner route signatures
CreateEntityUC = Annotated[CreateEntityUseCase, Depends(get_create_entity_use_case)]
```

**Route Handler Pattern:**
```python
@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    data: EntityCreate,
    ctx: OrganizationContext,  # Validated context with organization
    use_case: CreateEntityUC,  # Use case injected via factory
) -> EntityResponse:
    result = await use_case.execute(
        organization_id=ctx.organization,  # Active organization ID
        data=data,
        created_by=ctx.user,               # Current user ID
    )
    return EntityResponse.model_validate(result)
```

**Context Dependencies (from `src.app.dependencies`):**
- `CurrentContext` - Validated request context (requires auth only)
- `OrganizationContext` - Context with organization validation (requires auth + org header)

**ValidatedContext Properties:**
- `ctx.user` - Current user's UUID
- `ctx.organization` - Active organization UUID (raises if not set)
- All `RequestContext` methods: `has_role()`, `is_org_admin()`, etc.

**Nested Routes:**
Sub-resources use path parameters:
- `/professionals/{professional_id}/documents`
- `/professionals/{professional_id}/qualifications`

**Global Routes:**
Reference data not scoped by organization (e.g., specialties) use `CurrentContext` for auth only.

## Database Conventions

- **UUID v7** primary keys (`uuid7` factory)
- **Partial unique indexes** for soft delete: `postgresql_where=text("deleted_at IS NULL")`
- **GIN trigram indexes** for search: `postgresql_using="gin"`, requires `pg_trgm` + `f_unaccent` function
- Denormalize `organization_id` when needed for unique constraints

## Exceptions
Use typed exceptions from `src.app.exceptions`:
- `NotFoundError(resource="Entity", identifier=str(id))`
- `ConflictError(message="Entity already exists")`
- `ValidationError(message="Invalid data")`

## Code Style
- Line length: 120 chars
- Double quotes for strings
- Type everything (strict MyPy)
- Async-first: all DB operations use `await`

## Value Objects & Validation
Use typed value objects for data validation in schemas:
- **CPF**: Use `CPF` from `src.shared.domain.value_objects` (auto-validates and normalizes to 11 digits)
- **Phone**: Use `Phone` from `src.shared.domain.value_objects` (auto-validates and normalizes to E.164 format)
- **URLs**: Use `HttpUrl` from `pydantic` (validates http/https URLs)
- **Email**: Use `EmailStr` from `pydantic`

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from src.shared.domain.value_objects import CPF, Phone

class ExampleCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[Phone] = None
    cpf: Optional[CPF] = None
    avatar_url: Optional[HttpUrl] = None
```
