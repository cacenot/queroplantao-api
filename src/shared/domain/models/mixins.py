"""Mixins for SQLModel entities."""

from typing import Optional
from uuid import UUID, uuid7

from pydantic import AwareDatetime
from sqlalchemy import func
from sqlmodel import Field, SQLModel

from src.shared.domain.models.fields import AwareDatetimeField


class PrimaryKeyMixin(SQLModel):
    """
    Mixin for UUID v7 primary key.

    UUID v7 provides:
    - Time-ordered identifiers
    - Better database index performance
    - Avoids index fragmentation
    """

    id: UUID = Field(
        default_factory=uuid7,
        primary_key=True,
        description="Unique identifier (UUID v7)",
    )


class TimestampMixin(SQLModel):
    """
    Mixin for automatic timestamp tracking.

    Tracks creation and last update times using database-level defaults
    for consistency across different application instances.
    Uses timezone-aware datetime fields for proper UTC storage.
    """

    created_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        },
        nullable=False,
        description="Timestamp when the record was created (UTC)",
    )
    updated_at: AwareDatetime | None = AwareDatetimeField(
        default=None,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": func.now(),
            "nullable": True,
        },
        nullable=True,
        description="Timestamp when the record was last updated (UTC)",
    )


class TrackingMixin(SQLModel):
    """
    Mixin for tracking who created and last modified a record.

    Useful for audit trails and accountability.
    Should be populated from JWT claims in the application layer.
    """

    created_by: Optional[UUID] = Field(
        default=None,
        sa_column_kwargs={"nullable": True},
        description="UUID of user who created this record",
    )
    updated_by: Optional[UUID] = Field(
        default=None,
        sa_column_kwargs={"nullable": True},
        description="UUID of user who last updated this record",
    )


class VersionMixin(SQLModel):
    """
    Mixin for optimistic locking with version control.

    Helps prevent concurrent update conflicts.
    The version is automatically incremented on each update.
    """

    version: int = Field(
        default=1,
        sa_column_kwargs={
            "nullable": False,
            "server_default": "1",
        },
        description="Version number for optimistic locking",
    )


class SoftDeleteMixin(SQLModel):
    """
    Mixin for soft delete functionality.

    Instead of physically deleting records, marks them as deleted
    with a timestamp. This allows:
    - Recovery of accidentally deleted data
    - Audit trails and compliance
    - Historical data analysis
    """

    deleted_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        sa_column_kwargs={"nullable": True},
        nullable=True,
        description="Timestamp when the record was soft deleted (UTC)",
    )

    @property
    def is_deleted(self) -> bool:
        """Check if the record is soft deleted."""
        return self.deleted_at is not None


class MetadataMixin(SQLModel):
    """
    Mixin for flexible metadata storage.

    Stores arbitrary JSON data for extensibility without schema changes.
    Useful for:
    - Custom fields
    - Feature flags
    - Experimental data
    """

    metadata: Optional[dict] = Field(
        default=None,
        sa_column_kwargs={"nullable": True},
        description="Flexible JSON metadata storage",
    )
