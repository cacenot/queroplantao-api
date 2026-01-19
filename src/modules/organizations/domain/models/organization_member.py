"""OrganizationMember model for organization membership."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.organizations.domain.models.enums import MemberRole
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


class OrganizationMemberBase(BaseModel):
    """Base fields for OrganizationMember."""

    role: MemberRole = Field(
        default=MemberRole.VIEWER,
        sa_type=SAEnum(MemberRole, name="member_role", create_constraint=True),
        description="Member's role within the organization",
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

    Links users to organizations with specific roles.
    A user can be a member of multiple organizations with different roles.

    Examples:
    - User A is OWNER of Organization X
    - User B is MANAGER of Organization Y
    - User C is SCHEDULER of Organization Z
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        # Unique membership per user per organization
        UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_organization_members_user_org",
        ),
    )

    # User reference
    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        description="User ID",
    )

    # Organization reference
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization ID",
    )

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.user_id]",
            "lazy": "selectin",
        }
    )
    organization: "Organization" = Relationship(
        back_populates="members",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMember.organization_id]",
        },
    )

    @property
    def is_pending(self) -> bool:
        """Check if the invitation is pending acceptance."""
        return self.invited_at is not None and self.accepted_at is None
