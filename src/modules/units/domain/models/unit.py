"""Unit model - work locations where professionals perform their activities."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.units.domain.models.enums import UnitType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import PhoneField
from src.shared.domain.models.mixins import (
    AddressMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.contracts.domain.models.professional_contract import (
        ProfessionalContract,
    )
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.units.domain.models.sector import Sector
    from src.shared.domain.models.company import Company


class UnitBase(BaseModel):
    """Base fields for Unit."""

    name: str = Field(
        max_length=255,
        description="Unit name (e.g., 'Hospital São Paulo - Centro')",
    )
    code: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Internal code (unique per organization)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional details about the unit",
    )
    unit_type: UnitType = Field(
        sa_type=SAEnum(UnitType, name="unit_type", create_constraint=True),
        description="Type of unit (HOSPITAL, CLINIC, UPA, etc.)",
    )

    # Contact info
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Unit contact email",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Unit contact phone (E.164 format)",
    )

    # Geofencing for clock-in/out validation
    geofence_radius_meters: Optional[int] = Field(
        default=None,
        ge=0,
        le=10000,
        description="Radius in meters for geofence validation (0-10000)",
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
    SoftDeleteMixin,
    table=True,
):
    """
    Unit table model.

    Represents a work location where professionals perform their activities.
    Units are the physical places (hospitals, clinics, UPAs, etc.) where
    shifts occur, job postings are created, and time tracking happens.

    Each unit belongs to an organization (multi-tenant isolation) and may
    optionally be linked to a Company for legal/administrative purposes.

    Units can have multiple Sectors (departments, floors, specialties).

    Geolocation:
    - AddressMixin provides latitude/longitude for the main location
    - geofence_radius_meters defines the valid radius for clock-in validation
    - Sectors can override geolocation if they have different physical locations
    """

    __tablename__ = "units"
    __table_args__ = (
        # Unique code per organization (when code is set and not soft-deleted)
        Index(
            "uq_units_org_code",
            "organization_id",
            "code",
            unique=True,
            postgresql_where="code IS NOT NULL AND deleted_at IS NULL",
        ),
        # Index for listing units by organization
        Index("ix_units_organization_id", "organization_id"),
        # Index for filtering by type
        Index("ix_units_unit_type", "unit_type"),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this unit",
    )

    # Optional legal entity link
    company_id: Optional[UUID] = Field(
        default=None,
        foreign_key="companies.id",
        nullable=True,
        description="Linked Company for legal/administrative purposes",
    )

    # Relationships
    organization: "Organization" = Relationship()
    company: Optional["Company"] = Relationship()
    sectors: list["Sector"] = Relationship(back_populates="unit")
    professional_contracts: list["ProfessionalContract"] = Relationship(
        back_populates="unit"
    )
