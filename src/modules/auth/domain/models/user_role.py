"""UserRole junction model."""

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
    from src.modules.auth.domain.models.role import Role
    from src.modules.auth.domain.models.user import User


class UserRole(PrimaryKeyMixin, table=True):
    """
    Junction table for User-Role N:N relationship.

    Links users to roles with optional expiration for temporary role assignments.
    The granted_by field is nullable to support:
    - Auto-registration: user creates account and receives default role automatically
    - Migrations: roles imported from legacy systems
    - System processes: roles assigned by automated processes
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_roles_user_role"),
    )

    user_id: UUID = Field(
        foreign_key="users.id",
        nullable=False,
        description="User ID",
    )
    role_id: UUID = Field(
        foreign_key="roles.id",
        nullable=False,
        description="Role ID",
    )
    granted_by: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="User who granted this role (null for auto-assignment)",
    )
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

    # Relationships
    user: "User" = Relationship(
        back_populates="roles",
        sa_relationship_kwargs={"foreign_keys": "[UserRole.user_id]"},
    )
    role: "Role" = Relationship(back_populates="users")
