"""RolePermission junction model."""

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    PrimaryKeyMixin,
)

if TYPE_CHECKING:
    from src.modules.users.domain.models.permission import Permission
    from src.modules.users.domain.models.role import Role


class RolePermission(PrimaryKeyMixin, table=True):
    """
    Junction table for Role-Permission N:N relationship.

    Links permissions to roles, allowing roles to have multiple permissions.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "role_id", "permission_id", name="uq_role_permissions_role_permission"
        ),
    )

    role_id: UUID = Field(
        foreign_key="roles.id",
        nullable=False,
        description="Role ID",
    )
    permission_id: UUID = Field(
        foreign_key="permissions.id",
        nullable=False,
        description="Permission ID",
    )
    created_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={"server_default": "now()", "nullable": False},
        nullable=False,
        description="Timestamp when the role-permission link was created (UTC)",
    )

    # Relationships
    role: "Role" = Relationship(back_populates="permissions")
    permission: "Permission" = Relationship(back_populates="roles")
