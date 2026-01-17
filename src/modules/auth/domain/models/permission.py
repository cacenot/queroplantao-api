"""Permission model."""

from typing import TYPE_CHECKING, Optional

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    BaseModel,
    PrimaryKeyMixin,
)

if TYPE_CHECKING:
    from src.modules.auth.domain.models.role_permission import RolePermission
    from src.modules.auth.domain.models.user_permission import UserPermission


class PermissionBase(BaseModel):
    """Base fields for Permission."""

    code: str = Field(
        max_length=100,
        description="Permission code (e.g., 'shift:create', 'schedule:view')",
    )
    name: str = Field(
        max_length=255,
        description="Human-readable permission name",
    )
    description: Optional[str] = Field(
        default=None,
        description="Permission description",
    )
    module: str = Field(
        max_length=50,
        description="Module this permission belongs to (e.g., 'shifts', 'schedules')",
    )


class Permission(PermissionBase, PrimaryKeyMixin, table=True):
    """
    Permission table model.

    Defines granular permissions available in the system.
    Permissions follow the pattern: 'resource:action' (e.g., 'shift:create').
    """

    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("code", name="uq_permissions_code"),)

    created_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={"server_default": "now()", "nullable": False},
        nullable=False,
        description="Timestamp when the permission was created (UTC)",
    )

    # Relationships
    roles: list["RolePermission"] = Relationship(back_populates="permission")
    users: list["UserPermission"] = Relationship(back_populates="permission")
