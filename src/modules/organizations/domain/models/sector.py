"""Sector model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.organizations.domain.models.organization_member import (
        OrganizationMember,
    )
    from src.modules.organizations.domain.models.unit import Unit


class SectorBase(BaseModel):
    """Base fields for Sector."""

    name: str = Field(
        max_length=255,
        description="Sector name (e.g., 'UTI', 'Emergência', 'Cardiologia')",
    )
    code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Internal code for the sector",
    )
    description: Optional[str] = Field(
        default=None,
        description="Sector description",
    )

    # Optional geofence override (if different from unit)
    latitude: Optional[float] = Field(
        default=None,
        ge=-90,
        le=90,
        description="Sector latitude (overrides unit if set)",
    )
    longitude: Optional[float] = Field(
        default=None,
        ge=-180,
        le=180,
        description="Sector longitude (overrides unit if set)",
    )
    geofence_radius_meters: Optional[int] = Field(
        default=None,
        ge=0,
        le=10000,
        description="Geofence radius in meters (overrides unit if set)",
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
    table=True,
):
    """
    Sector table model.

    Represents a subdivision within a unit.
    Examples: ICU, Emergency Room, Cardiology department.

    Sectors can override the parent unit's geofence settings.
    If latitude/longitude/geofence_radius_meters are null, inherits from the unit.
    """

    __tablename__ = "sectors"
    __table_args__ = (UniqueConstraint("unit_id", "code", name="uq_sectors_unit_code"),)

    # Parent unit
    unit_id: UUID = Field(
        foreign_key="units.id",
        nullable=False,
        description="Parent unit ID",
    )

    # Relationships
    unit: "Unit" = Relationship(back_populates="sectors")
    members: list["OrganizationMember"] = Relationship(
        back_populates="sector",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.sector_id]",
        },
    )

    def get_effective_geofence(self) -> tuple[float | None, float | None, int | None]:
        """
        Get effective geofence settings (own or inherited from unit).

        Returns:
            Tuple of (latitude, longitude, radius_meters)
        """
        lat = self.latitude if self.latitude is not None else self.unit.latitude
        lng = self.longitude if self.longitude is not None else self.unit.longitude
        radius = (
            self.geofence_radius_meters
            if self.geofence_radius_meters is not None
            else self.unit.geofence_radius_meters
        )
        return (lat, lng, radius)
