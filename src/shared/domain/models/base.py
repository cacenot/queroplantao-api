"""Base models using mixins for SQLModel entities."""

from typing import Any

from sqlalchemy import MetaData
from sqlmodel import SQLModel

from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TenantMixin,
    TimestampMixin,
    TrackingMixin,
)


# Naming convention for constraints (helps with Alembic migrations)
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel(PrimaryKeyMixin, TimestampMixin, SQLModel):
    """
    Base model with common fields for all entities.

    Provides:
    - UUID v7 primary key (PrimaryKeyMixin)
    - Created/updated timestamps (TimestampMixin)
    """

    def model_dump_for_update(self, **kwargs: Any) -> dict[str, Any]:
        """Dump model excluding id and timestamps for updates."""
        exclude = kwargs.pop("exclude", set())
        exclude = set(exclude) | {"id", "created_at", "updated_at"}
        return self.model_dump(exclude=exclude, **kwargs)


class TenantBaseModel(BaseModel, TenantMixin):
    """
    Base model for tenant-scoped entities.

    Combines:
    - BaseModel (id, timestamps)
    - TenantMixin (tenant_id)

    Use this as base for all multi-tenant tables.

    Example:
        class Shift(TenantBaseModel, table=True):
            __tablename__ = "shifts"
            title: str
            start_time: datetime
            end_time: datetime
    """

    pass


class TenantTrackableModel(TenantBaseModel, TrackingMixin):
    """
    Tenant model with user tracking.

    Combines:
    - TenantBaseModel (id, timestamps, tenant_id)
    - TrackingMixin (created_by, updated_by)

    Use for entities that need to track which user created/modified them.
    """

    pass


class GlobalBaseModel(BaseModel):
    """
    Base model for global (cross-tenant) entities.

    Use this for entities that are shared across all tenants,
    such as the global professionals registry (CRM/UF).

    Example:
        class Professional(GlobalBaseModel, table=True):
            __tablename__ = "professionals"
            crm: str
            uf: str
            name: str
    """

    pass
