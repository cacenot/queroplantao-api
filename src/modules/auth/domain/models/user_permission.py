"""UserPermission junction model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    PrimaryKeyMixin,
)

if TYPE_CHECKING:
    from src.modules.auth.domain.models.permission import Permission
    from src.modules.auth.domain.models.user import User


class UserPermission(PrimaryKeyMixin, table=True):
    """
    Junction table for User-Permission N:N relationship.

    Allows assigning standalone permissions directly to users,
    bypassing role-based assignment. Useful for granular permission overrides.
    """

    __tablename__ = "user_permissions"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "permission_id", name="uq_user_permissions_user_permission"
        ),
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        description="User ID",
    )
    permission_id: UUID = Field(
        foreign_key="permissions.id",
        nullable=False,
        description="Permission ID",
    )
    granted_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="User who granted this permission",
    )
    granted_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={"server_default": "now()", "nullable": False},
        nullable=False,
        description="Timestamp when the permission was granted (UTC)",
    )
    expires_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Optional expiration timestamp for temporary permissions (UTC)",
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="permissions",
        sa_relationship_kwargs={"foreign_keys": "[UserPermission.user_id]"},
    )
    permission: "Permission" = Relationship(back_populates="users")
