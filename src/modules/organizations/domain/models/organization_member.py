"""OrganizationMember model for polymorphic membership."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import CheckConstraint, Enum as SAEnum, Index
from sqlmodel import Field, Relationship

from src.modules.organizations.domain.models.enums import EntityType, MemberRole
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.auth.domain.models import User
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.organizations.domain.models.sector import Sector
    from src.modules.organizations.domain.models.unit import Unit


class OrganizationMemberBase(BaseModel):
    """Base fields for OrganizationMember."""

    role: MemberRole = Field(
        default=MemberRole.VIEWER,
        sa_type=SAEnum(MemberRole, name="member_role", create_constraint=True),
        description="Member's role within the entity",
    )

    # Invitation/acceptance tracking
    invited_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the invitation was sent (UTC)",
    )
    accepted_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the invitation was accepted (UTC)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the membership is currently active",
    )


class OrganizationMember(
    OrganizationMemberBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    OrganizationMember table model.

    Polymorphic membership table linking users to organizations, units, or sectors.
    A member can have different roles at different levels of the hierarchy.

    Examples:
    - User A is OWNER of Organization X
    - User B is MANAGER of Unit Y (within Organization X)
    - User C is SCHEDULER of Sector Z (within Unit Y)

    Permission inheritance:
    - Organization members have access to all units/sectors (with same or lower role)
    - Unit members have access to all sectors within that unit
    - Sector members have access only to that sector
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        # Ensure exactly one entity type is set
        CheckConstraint(
            "(organization_id IS NOT NULL AND unit_id IS NULL AND sector_id IS NULL) OR "
            "(organization_id IS NULL AND unit_id IS NOT NULL AND sector_id IS NULL) OR "
            "(organization_id IS NULL AND unit_id IS NULL AND sector_id IS NOT NULL)",
            name="ck_organization_members_entity",
        ),
        # Unique membership per user per entity
        Index(
            "uq_organization_members_user_org",
            "user_id",
            "organization_id",
            unique=True,
            postgresql_where="organization_id IS NOT NULL",
        ),
        Index(
            "uq_organization_members_user_unit",
            "user_id",
            "unit_id",
            unique=True,
            postgresql_where="unit_id IS NOT NULL",
        ),
        Index(
            "uq_organization_members_user_sector",
            "user_id",
            "sector_id",
            unique=True,
            postgresql_where="sector_id IS NOT NULL",
        ),
    )

    # User reference
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        description="User ID",
    )

    # Polymorphic entity references (exactly one should be set)
    organization_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        nullable=True,
        description="Organization ID (if member of organization)",
    )
    unit_id: Optional[UUID] = Field(
        default=None,
        foreign_key="units.id",
        nullable=True,
        description="Unit ID (if member of unit)",
    )
    sector_id: Optional[UUID] = Field(
        default=None,
        foreign_key="sectors.id",
        nullable=True,
        description="Sector ID (if member of sector)",
    )

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.user_id]",
            "lazy": "selectin",
        }
    )
    organization: Optional["Organization"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.organization_id]",
        },
    )
    unit: Optional["Unit"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.unit_id]",
        },
    )
    sector: Optional["Sector"] = Relationship(
        back_populates="members",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.sector_id]",
        },
    )

    @property
    def entity_type(self) -> EntityType:
        """Get the type of entity this membership is for."""
        if self.organization_id is not None:
            return EntityType.ORGANIZATION
        elif self.unit_id is not None:
            return EntityType.UNIT
        else:
            return EntityType.SECTOR

    @property
    def entity_id(self) -> UUID:
        """Get the ID of the entity this membership is for."""
        if self.organization_id is not None:
            return self.organization_id
        elif self.unit_id is not None:
            return self.unit_id
        else:
            return self.sector_id  # type: ignore

    @property
    def is_pending(self) -> bool:
        """Check if the invitation is pending acceptance."""
        return self.invited_at is not None and self.accepted_at is None
