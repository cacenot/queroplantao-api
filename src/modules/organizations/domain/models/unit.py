"""Unit model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import PhoneField
from src.shared.domain.models.mixins import (
    AddressMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.organizations.domain.models.organization_member import (
        OrganizationMember,
    )
    from src.modules.organizations.domain.models.sector import Sector


class UnitBase(BaseModel):
    """Base fields for Unit."""

    name: str = Field(
        max_length=255,
        description="Unit name (e.g., 'Ala Sul', 'Prédio A')",
    )
    code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Internal code for the unit",
    )
    description: Optional[str] = Field(
        default=None,
        description="Unit description",
    )

    # Contact info
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Unit email address",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Unit phone number (E.164 format)",
    )

    # Geofence configuration (for check-in/out validation)
    geofence_radius_meters: Optional[int] = Field(
        default=None,
        ge=0,
        le=10000,
        description="Geofence radius in meters for check-in validation (uses AddressMixin lat/lng)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the unit is currently active",
    )


class Unit(
    UnitBase,
    AddressMixin,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    Unit table model.

    Represents a physical location within an organization.
    Examples: Hospital wing, building, branch office.

    Units have address with lat/lng for geofence support.
    Sectors inherit the unit's geofence if they don't define their own.
    """

    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_units_organization_code"),
    )

    # Parent organization
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Parent organization ID",
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="units")
    sectors: list["Sector"] = Relationship(back_populates="unit")
    members: list["OrganizationMember"] = Relationship(
        back_populates="unit",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.unit_id]",
        },
    )
