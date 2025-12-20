"""Base models and mixins for SQLModel entities."""

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import MetaData
from sqlmodel import Field, SQLModel


# Naming convention for constraints (helps with Alembic migrations)
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel(SQLModel):
    """
    Base model with common fields for all entities.

    Provides:
    - UUID primary key
    - Created/updated timestamps
    """

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique identifier",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
        sa_column_kwargs={"nullable": False},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
        sa_column_kwargs={"nullable": False, "onupdate": datetime.utcnow},
    )

    def model_dump_for_update(self, **kwargs: Any) -> dict[str, Any]:
        """Dump model excluding id and timestamps for updates."""
        exclude = kwargs.pop("exclude", set())
        exclude = set(exclude) | {"id", "created_at", "updated_at"}
        return self.model_dump(exclude=exclude, **kwargs)


class TenantMixin(SQLModel):
    """
    Mixin for multi-tenant entities.

    All tenant-scoped tables should inherit from this mixin.
    The tenant_id is required and indexed for efficient filtering.
    """

    tenant_id: UUID = Field(
        index=True,
        nullable=False,
        description="Tenant identifier for multi-tenancy isolation",
    )


class TenantBaseModel(BaseModel, TenantMixin):
    """
    Base model for tenant-scoped entities.

    Combines BaseModel (id, timestamps) with TenantMixin (tenant_id).
    Use this as base for all multi-tenant tables.

    Example:
        class Shift(TenantBaseModel, table=True):
            title: str
            start_time: datetime
            end_time: datetime
    """

    pass


class GlobalBaseModel(BaseModel):
    """
    Base model for global (cross-tenant) entities.

    Use this for entities that are shared across all tenants,
    such as the global professionals registry (CRM/UF).

    Example:
        class Professional(GlobalBaseModel, table=True):
            crm: str
            uf: str
            name: str
    """

    pass
