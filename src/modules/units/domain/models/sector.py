"""Sector model - subdivisions within a Unit."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Index
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.units.domain.models.unit import Unit


class SectorBase(BaseModel):
    """Base fields for Sector."""

    name: str = Field(
        max_length=255,
        description="Sector name (e.g., 'UTI Adulto', 'Emergência', 'Bloco A')",
    )
    code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Internal code (unique per unit)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional details about the sector",
    )

    # Geolocation override (if sector is in a different location than the unit)
    latitude: Optional[float] = Field(
        default=None,
        description="Latitude coordinate (overrides Unit if set)",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Longitude coordinate (overrides Unit if set)",
    )
    geofence_radius_meters: Optional[int] = Field(
        default=None,
        ge=0,
        le=10000,
        description="Radius in meters for geofence validation (overrides Unit if set)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the sector is currently active",
    )


class Sector(
    SectorBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    Sector table model.

    Represents a subdivision within a Unit (department, floor, wing, specialty area).
    Sectors allow more granular organization of work locations.

    Examples:
    - Hospital Unit -> Sectors: UTI Adulto, UTI Neonatal, Emergência, Centro Cirúrgico
    - Clinic Unit -> Sectors: Consultório 1, Consultório 2, Sala de Procedimentos

    Geolocation inheritance:
    - If latitude/longitude are NULL, use the parent Unit's location
    - If set, override the Unit's location (useful for large campuses)
    - Same logic applies to geofence_radius_meters
    """

    __tablename__ = "sectors"
    __table_args__ = (
        # Unique code per unit (when code is set and not soft-deleted)
        Index(
            "uq_sectors_unit_code",
            "unit_id",
            "code",
            unique=True,
            postgresql_where="code IS NOT NULL AND deleted_at IS NULL",
        ),
        # Index for listing sectors by unit
        Index("ix_sectors_unit_id", "unit_id"),
    )

    # Unit reference (required)
    unit_id: UUID = Field(
        foreign_key="units.id",
        nullable=False,
        description="Unit that contains this sector",
    )

    # Relationships
    unit: "Unit" = Relationship(back_populates="sectors")

    @property
    def effective_latitude(self) -> Optional[float]:
        """Get effective latitude (sector override or unit's latitude)."""
        if self.latitude is not None:
            return self.latitude
        return self.unit.latitude if self.unit else None

    @property
    def effective_longitude(self) -> Optional[float]:
        """Get effective longitude (sector override or unit's longitude)."""
        if self.longitude is not None:
            return self.longitude
        return self.unit.longitude if self.unit else None

    @property
    def effective_geofence_radius(self) -> Optional[int]:
        """Get effective geofence radius (sector override or unit's radius)."""
        if self.geofence_radius_meters is not None:
            return self.geofence_radius_meters
        return self.unit.geofence_radius_meters if self.unit else None
