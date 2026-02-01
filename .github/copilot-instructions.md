# Copilot Instructions - Quero Plantão API

## Project Overview

REST API for medical shift management (HR Tech). Multi-tenant architecture with organization-scoped data isolation. Built with FastAPI + SQLModel + PostgreSQL.

**IMPORTANT: This API is in active development with no production deployment yet. Deprecated code should be immediately removed instead of being marked as `deprecated=True`.**

## Terminal Commands

**ALWAYS use `uv run` to execute any Python command in this project.** This project uses `uv` as the package manager and virtual environment tool.

Examples:
- `uv run alembic upgrade head` (NOT `alembic upgrade head`)
- `uv run pytest` (NOT `pytest`)
- `uv run python script.py` (NOT `python script.py`)
- `uv run ruff check .` (NOT `ruff check .`)

The `make` commands already handle this internally, so you can use them directly.

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

## API Client (packages/api-client)

When adding endpoints or enums, always keep the API client in sync:

- Regenerate client artifacts: run `make client-all`.
- Enums/labels: update `ENUM_LABELS` and `MANUAL_ENUM_DEFINITIONS` in [scripts/generate_ts_enums.py](scripts/generate_ts_enums.py), then run `make client-enums`.
- ESM/NodeNext: use explicit `.js` extensions in API client relative imports and barrel re-exports.
- Releases: workflow requires `contents: write` and should skip release when the version already exists in [ .github/workflows/publish-api-client.yml ](.github/workflows/publish-api-client.yml).

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
- `SoftDeleteMixin[ModelT]` - Soft delete support, overrides `get_query()` and `delete()` ([mixins.py](src/shared/infrastructure/repositories/mixins.py))
- `OrganizationScopeMixin[ModelT]` - Organization/family scope for multi-tenant queries ([organization_scope_mixin.py](src/shared/infrastructure/repositories/organization_scope_mixin.py))
- Model mixins: `PrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteMixin`, `TrackingMixin`, `VerificationMixin`

## Repository System

The repository layer provides a composable, type-safe data access pattern using mixins.

### BaseRepository

The base class for all repositories. Provides CRUD operations and paginated listing.

```python
from src.shared.infrastructure.repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    model = User
```

**Core Methods:**
- `get_query()` → Returns base `SELECT` query. Override in mixins to add filters.
- `get_by_id(id)` → Get entity by UUID or `None`
- `get_by_id_or_raise(id)` → Get entity or raise `NotFoundError`
- `list(*, filters, sorting, limit, offset, base_query)` → Paginated listing with FilterSet/SortingSet
- `create(entity)` → Insert and return entity
- `update(entity)` → Update and return entity
- `delete(id)` → Hard delete entity

**Pagination Parameters:**
```python
result = await repository.list(
    filters=MyFilter(search="john"),  # FilterSet instance
    sorting=MySorting(name="asc"),    # SortingSet instance
    limit=25,                          # Page size (default: 25)
    offset=0,                          # Skip N records (default: 0)
)
# Returns PaginatedResponse[Entity] with items, total, page, page_size, pages
```

### SoftDeleteMixin

Adds soft delete behavior. Must be listed BEFORE `BaseRepository` in inheritance.

```python
from src.shared.infrastructure.repositories import BaseRepository, SoftDeleteMixin

class ProfessionalRepository(SoftDeleteMixin[Professional], BaseRepository[Professional]):
    model = Professional
```

**What it does:**
- Overrides `get_query()` → Adds `WHERE deleted_at IS NULL` filter
- Overrides `delete(id)` → Sets `deleted_at = now()` instead of hard delete

**Additional Methods:**
- `get_by_id_including_deleted(id)` → Bypass soft-delete filter (for restore/audit)
- `restore(id)` → Clear `deleted_at` to restore entity

**Behavior:**
```python
# With SoftDeleteMixin:
await repo.delete(id)  # Sets deleted_at, entity hidden from queries
await repo.get_by_id(id)  # Returns None (filtered out)
await repo.get_by_id_including_deleted(id)  # Returns entity
await repo.restore(id)  # Clears deleted_at, entity visible again
```

### OrganizationScopeMixin

Adds organization-scoped queries with support for family hierarchy. Must be listed BEFORE other mixins.

```python
from src.shared.infrastructure.repositories import (
    BaseRepository,
    OrganizationScopeMixin,
    SoftDeleteMixin,
)

class OrganizationProfessionalRepository(
    OrganizationScopeMixin[OrganizationProfessional],
    SoftDeleteMixin[OrganizationProfessional],
    BaseRepository[OrganizationProfessional],
):
    model = OrganizationProfessional
    default_scope_policy = "FAMILY"  # or "ORGANIZATION_ONLY"
```

**Scope Policies:**
- `"ORGANIZATION_ONLY"` → Query only the current organization (default)
- `"FAMILY"` → Query all organizations in the family (parent + children)

**Methods:**
```python
# Get entity within organization scope
entity = await repo.get_by_organization(
    id=entity_id,
    organization_id=org_id,
    family_org_ids=family_ids,
    scope_policy="FAMILY",  # Optional, uses default if omitted
)

# List with organization scope + pagination
result = await repo.list_by_organization(
    organization_id=org_id,
    family_org_ids=family_ids,
    filters=MyFilter(),
    sorting=MySorting(),
    limit=25,
    offset=0,
    scope_policy="FAMILY",
)

# Check existence in family
exists = await repo.exists_in_family(
    family_org_ids=family_ids,
    cpf="12345678901",  # Field filters as kwargs
)

# Find single record in family
entity = await repo.find_in_family(
    family_org_ids=family_ids,
    exclude_id=current_id,  # Optional: exclude from results
    email="user@example.com",
)
```

### Mixin Composition Order (CRITICAL)

The order of mixins in inheritance matters due to Python's Method Resolution Order (MRO):

```python
# ✅ CORRECT ORDER: OrganizationScope → SoftDelete → Base
class MyRepository(
    OrganizationScopeMixin[Entity],
    SoftDeleteMixin[Entity],
    BaseRepository[Entity],
):
    model = Entity

# Method Resolution:
# - list_by_organization() calls super().get_query() → SoftDeleteMixin.get_query()
# - SoftDeleteMixin.get_query() returns query with deleted_at filter
# - list_by_organization() then applies org scope to that query
```

**Rule:** More specific mixins go FIRST (leftmost), `BaseRepository` goes LAST.

### Repository Composition Examples

```python
# 1. Simple repository (no soft delete, no org scope)
class RoleRepository(BaseRepository[Role]):
    model = Role

# 2. With soft delete only
class SpecialtyRepository(SoftDeleteMixin[Specialty], BaseRepository[Specialty]):
    model = Specialty

# 3. With org scope only (no soft delete)
class ContractRepository(OrganizationScopeMixin[Contract], BaseRepository[Contract]):
    model = Contract
    default_scope_policy = "ORGANIZATION_ONLY"

# 4. Full stack: org scope + soft delete
class ProfessionalRepository(
    OrganizationScopeMixin[Professional],
    SoftDeleteMixin[Professional],
    BaseRepository[Professional],
):
    model = Professional
    default_scope_policy = "FAMILY"
```

### Custom Repository Methods

Add domain-specific methods by extending the base patterns:

```python
class ProfessionalRepository(
    OrganizationScopeMixin[Professional],
    SoftDeleteMixin[Professional],
    BaseRepository[Professional],
):
    model = Professional
    default_scope_policy = "FAMILY"

    async def find_by_cpf(
        self,
        cpf: str,
        organization_id: UUID,
        family_org_ids: tuple[UUID, ...],
    ) -> Professional | None:
        """Find professional by CPF within family scope."""
        return await self.find_in_family(
            family_org_ids=family_org_ids,
            cpf=cpf,
        )

    async def exists_by_email_in_family(
        self,
        email: str,
        family_org_ids: tuple[UUID, ...],
        *,
        exclude_id: UUID | None = None,
    ) -> bool:
        """Check if email exists in family, optionally excluding an ID."""
        existing = await self.find_in_family(
            family_org_ids=family_org_ids,
            exclude_id=exclude_id,
            email=email,
        )
        return existing is not None
```

## Core Patterns

### Multi-Tenancy with Family Scope (CRITICAL)
Professionals are shared within an organization family (parent + children). Use `OrganizationScopeMixin` with `default_scope_policy = "FAMILY"`:

```python
class ProfessionalRepository(
    OrganizationScopeMixin[Professional],
    SoftDeleteMixin[Professional],
    BaseRepository[Professional],
):
    model = Professional
    default_scope_policy = "FAMILY"

# In use case:
professionals = await repo.list_by_organization(
    organization_id=ctx.organization,
    family_org_ids=ctx.family_org_ids,
    filters=filters,
    sorting=sorting,
    limit=limit,
    offset=offset,
)
```

**Family Scope Validation:**
- CPF uniqueness is validated at family level (not just organization)
- Email uniqueness is validated at family level
- Council registration uniqueness is validated at family level
- Use `exists_in_family()` and `find_in_family()` for validation

### Soft Delete
Models with `SoftDeleteMixin` (model) use `deleted_at` column. Repositories using `SoftDeleteMixin` (repository):
- Automatically filter out deleted records via `get_query()`
- Use `delete()` which performs soft delete
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

### Pagination in Routes
```python
@router.get("/", response_model=PaginatedResponse[EntityResponse])
async def list_entities(
    ctx: OrganizationContext,
    use_case: ListEntitiesUC,
    filters: Annotated[EntityFilter, Depends()],
    sorting: Annotated[EntitySorting, Depends()],
    limit: Annotated[int, Query(ge=1, le=100)] = 25,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> PaginatedResponse[EntityResponse]:
    return await use_case.execute(
        organization_id=ctx.organization,
        family_org_ids=ctx.family_org_ids,
        filters=filters,
        sorting=sorting,
        limit=limit,
        offset=offset,
    )
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
        family_org_ids=ctx.family_org_ids, # For family scope validation
    )
    return EntityResponse.model_validate(result)
```

**Context Dependencies (from `src.app.dependencies`):**
- `CurrentContext` - Validated request context (requires auth only)
- `OrganizationContext` - Context with organization validation (requires auth + org header)

**ValidatedContext Properties:**
- `ctx.user` - Current user's UUID
- `ctx.organization` - Active organization UUID (raises if not set)
- `ctx.family_org_ids` - Tuple of all organization IDs in the family (cached in Redis)
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

### Migration Naming Convention (REQUIRED)
Migrations use **sequential numeric prefixes** (12 digits, zero-padded) instead of Alembic's random revision IDs:

```
000000000001_add_postgresql_extensions.py
000000000002_seed_roles_and_specialties.py
000000000003_unify_document_types.py
...
000000000006_remove_redundant_step_fields.py
```

**Rules:**
1. **Check existing migrations first**: List `alembic/versions/` to find the highest prefix number
2. **Increment by 1**: New migration = highest existing number + 1
3. **Use as revision ID**: The prefix IS the revision ID (e.g., `revision: str = "000000000006"`)
4. **Set down_revision**: Point to previous sequential number (e.g., `down_revision = "000000000005"`)
5. **File naming**: `{prefix}_{snake_case_description}.py`

**Example migration header:**
```python
"""description_of_change

Revision ID: 000000000006
Revises: 000000000005
Create Date: 2026-01-28 14:00:00.000000
"""
revision: str = "000000000006"
down_revision: Union[str, Sequence[str], None] = "000000000005"
```

## Exceptions & Error Codes

### Domain-Specific Exceptions (REQUIRED)
Always use domain-specific exceptions instead of generic ones. Each module has its own exception classes with unique error codes.

#### Exception Structure
```
src/app/
├── constants/
│   └── error_codes.py           # Error code enums (AuthErrorCodes, ProfessionalErrorCodes, etc.)
└── exceptions/
    ├── __init__.py              # Re-exports all exceptions
    ├── base.py                  # AppException base class
    ├── auth_exceptions.py       # Auth-specific exceptions
    ├── organization_exceptions.py
    └── professional_exceptions.py
```

#### Error Code Convention
- Prefix with module abbreviation: `AUTH_`, `ORG_`, `PROF_`
- Descriptive name: `PROF_CPF_ALREADY_EXISTS`, `PROF_QUALIFICATION_NOT_FOUND`
- Add to `{Module}ErrorCodes` enum in `error_codes.py`

#### Creating Domain-Specific Exceptions
```python
# In error_codes.py
class ProfessionalErrorCodes(str, Enum):
    PROF_CPF_ALREADY_EXISTS = "PROF_CPF_ALREADY_EXISTS"
    PROF_NOT_FOUND = "PROF_NOT_FOUND"

# In professional_exceptions.py
class ProfessionalCpfExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message=get_message(ProfessionalMessages.CPF_ALREADY_EXISTS),
            code=ProfessionalErrorCodes.PROF_CPF_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
        )
```

#### Using Domain Exceptions in Use Cases
```python
# ❌ DON'T use generic exceptions
raise ConflictError(message="CPF already exists")
raise NotFoundError(resource="Professional", identifier=str(id))

# ✅ DO use domain-specific exceptions
raise ProfessionalCpfExistsError()
raise ProfessionalNotFoundError(professional_id=str(id))
```

### OpenAPI Error Documentation (REQUIRED)
Document error responses in route handlers using FastAPI's `responses` parameter:

```python
from src.app.constants.error_codes import ProfessionalErrorCodes
from src.shared.presentation.schemas import ErrorResponse

@router.post(
    "/",
    response_model=EntityResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Conflict",
            "content": {
                "application/json": {
                    "examples": {
                        "cpf_exists": {
                            "summary": "CPF already exists",
                            "value": {"code": ProfessionalErrorCodes.PROF_CPF_ALREADY_EXISTS, "message": "..."},
                        },
                        "email_exists": {
                            "summary": "Email already exists",
                            "value": {"code": ProfessionalErrorCodes.PROF_EMAIL_ALREADY_EXISTS, "message": "..."},
                        },
                    }
                }
            },
        },
    },
)
```

### Bruno Documentation (REQUIRED)
Add error codes table to all `.bru` files in the `docs {}` block:

```
docs {
  # Endpoint Description
  
  ...existing docs...
  
  ## Error Codes
  
  | Status | Code | Descrição |
  |--------|------|-----------|
  | 404 | `PROF_NOT_FOUND` | Profissional não encontrado |
  | 409 | `PROF_CPF_ALREADY_EXISTS` | Já existe profissional com este CPF |
}
```

## Internationalization (i18n)

All error messages are centralized and translated to Brazilian Portuguese (pt-BR). Use the i18n system from `src.app.i18n`:

### Message Keys
Message keys are organized in enums by domain:
- `AuthMessages` - Authentication/authorization errors
- `OrganizationMessages` - Organization-related errors
- `ResourceMessages` - Generic resource errors (not found, conflict, validation)
- `ProfessionalMessages` - Professional module business errors
- `ValidationMessages` - Value object validation errors (CPF, CNPJ, Phone, CEP)

### Usage Pattern
```python
from src.app.i18n import get_message, ProfessionalMessages

# Simple message
raise ConflictError(message=get_message(ProfessionalMessages.CPF_ALREADY_EXISTS))

# Message with interpolation
raise ValidationError(
    message=get_message(
        ProfessionalMessages.INVALID_COUNCIL_TYPE,
        council_type=data.council_type.value,
        professional_type=data.professional_type.value,
    )
)
```

### Adding New Messages
1. Add key to appropriate enum in `src/app/i18n/messages.py`
2. Add pt-BR translation in `src/app/i18n/locales/pt_br.py`
3. Use `{variable}` placeholders for interpolation

### Structure
```
src/app/i18n/
├── __init__.py          # get_message() function + exports
├── messages.py          # Message key enums (AuthMessages, etc.)
└── locales/
    ├── __init__.py
    └── pt_br.py         # Brazilian Portuguese translations
```

## Code Style
- Line length: 120 chars
- Double quotes for strings
- Type everything (strict MyPy)
- Async-first: all DB operations use `await`

## ScreeningProcess Model Rule
- Keep only FK columns and relationships in `ScreeningProcess`.
- Move all other properties/columns to `ScreeningProcessBase`.

## Value Objects & Validation
**ALWAYS use typed value objects for data validation in schemas. NEVER use raw `str` for these fields:**

- **CPF**: Use `CPF` from `src.shared.domain.value_objects` (auto-validates and normalizes to 11 digits)
- **CNPJ**: Use `CNPJ` from `src.shared.domain.value_objects` (auto-validates and normalizes to 14 digits)
- **CPFOrCNPJ**: Use `CPFOrCNPJ` from `src.shared.domain.value_objects` (accepts either CPF or CNPJ)
- **Phone**: Use `Phone` from `src.shared.domain.value_objects` (auto-validates and normalizes to E.164 format)
- **StateUF**: Use `StateUF` from `src.shared.domain.value_objects` (validates Brazilian state codes, normalizes to uppercase)
- **PostalCode**: Use `PostalCode` from `src.shared.domain.value_objects` (validates CEP with 8 digits)
- **URLs**: Use `HttpUrl` from `pydantic` (validates http/https URLs)
- **Email**: Use `EmailStr` from `pydantic`

```python
from pydantic import BaseModel, EmailStr, HttpUrl
from src.shared.domain.value_objects import CNPJ, CPF, CPFOrCNPJ, Phone, PostalCode, StateUF

class ExampleCreate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[Phone] = None
    cpf: Optional[CPF] = None
    cnpj: Optional[CNPJ] = None
    document: Optional[CPFOrCNPJ] = None  # When field accepts either CPF or CNPJ
    state_code: Optional[StateUF] = None  # e.g., "SP", "RJ"
    postal_code: Optional[PostalCode] = None
    avatar_url: Optional[HttpUrl] = None
```

### StateUF Features
```python
from src.shared.domain.value_objects import StateUF, BRAZILIAN_STATES

uf = StateUF("sp")  # Normalizes to "SP"
print(uf.full_name)  # "São Paulo"
print(uf.region)     # "Sudeste"

# Get all states
print(BRAZILIAN_STATES)  # {"AC": "Acre", "AL": "Alagoas", ...}

# Get states by region
sudeste = StateUF.get_states_by_region("Sudeste")  # [SP, RJ, MG, ES]
```
