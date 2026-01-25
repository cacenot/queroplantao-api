"""OrganizationMembership model for organization membership with roles."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.users.domain.models.role import Role
    from src.modules.users.domain.models.user import User
    from src.modules.organizations.domain.models.organization import Organization


class OrganizationMembershipBase(BaseModel):
    """Base fields for OrganizationMembership."""

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

    # Role grant tracking
    granted_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={"server_default": "now()", "nullable": False},
        nullable=False,
        description="Timestamp when the role was granted (UTC)",
    )
    expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Optional expiration timestamp for temporary roles (UTC)",
    )

    # Status
    is_active: bool = Field(
        default=True,
        description="Whether the membership is currently active",
    )


class OrganizationMembership(
    OrganizationMembershipBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    Organization membership table model.

    Links users to organizations with specific roles.
    A user can have multiple roles in the same organization (multiple rows).
    Membership is implicit: if user has at least one active role, they are a member.

    Examples:
    - User A in Org X has role ORG_OWNER (1 row)
    - User B in Org Y has roles ORG_ADMIN and ORG_SCHEDULER (2 rows)
    """

    __tablename__ = "organization_memberships"
    __table_args__ = (
        # Unique role per user per organization
        UniqueConstraint(
            "user_id",
            "organization_id",
            "role_id",
            name="uq_org_memberships_user_org_role",
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

    # Role reference
    role_id: UUID = Field(
        foreign_key="roles.id",
        nullable=False,
        description="Role ID",
    )

    # Who granted this role
    granted_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="User who granted this role",
    )

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMembership.user_id]",
            "lazy": "selectin",
        }
    )
    organization: "Organization" = Relationship(
        back_populates="memberships",
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMembership.organization_id]",
        },
    )
    role: "Role" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[OrganizationMembership.role_id]",
            "lazy": "selectin",
        },
    )

    @property
    def is_pending(self) -> bool:
        """Check if the invitation is pending acceptance."""
        return self.invited_at is not None and self.accepted_at is None

    @property
    def role_code(self) -> str | None:
        """Get the role code for this membership."""
        return self.role.code if self.role else None
