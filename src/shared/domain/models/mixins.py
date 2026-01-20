"""Mixins for SQLModel entities."""

from typing import Optional
from uuid import UUID, uuid7

from pydantic import AwareDatetime
from sqlalchemy import JSON, func
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

    Note: Field named 'extra_metadata' to avoid conflict with SQLModel's
    reserved 'metadata' attribute.
    """

    extra_metadata: Optional[dict] = Field(
        default=None,
        sa_type=JSON,
        sa_column_kwargs={"nullable": True},
        description="Flexible JSON metadata storage",
    )


class AddressMixin(SQLModel):
    """
    Mixin for address fields.

    Provides complete address information including:
    - Street address with number and complement
    - Neighborhood, city, and state (with both code and full name)
    - Postal code
    - Geographic coordinates
    """

    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Street address",
    )
    number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Street number",
    )
    complement: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Address complement (apt, suite, etc.)",
    )
    neighborhood: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Neighborhood/district",
    )
    city: Optional[str] = Field(
        default=None,
        max_length=100,
        description="City name",
    )
    state_code: Optional[str] = Field(
        default=None,
        max_length=2,
        description="State abbreviation (UF - 2 chars)",
    )
    state_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="State full name",
    )
    postal_code: Optional[str] = Field(
        default=None,
        max_length=10,
        description="Postal/ZIP code (CEP format: XXXXX-XXX)",
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Latitude coordinate",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Longitude coordinate",
    )


class VerificationMixin(SQLModel):
    """
    Mixin for verification tracking.

    Tracks when and by whom a record was verified.
    Useful for:
    - Document verification
    - Profile verification
    - Data validation workflows
    """

    verified_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Timestamp when the record was verified (UTC)",
    )
    verified_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="User ID who verified this record",
    )
