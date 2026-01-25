"""Role model."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.users.domain.models.role_permission import RolePermission
    from src.modules.users.domain.models.user_role import UserRole


class RoleBase(BaseModel):
    """Base fields for Role."""

    code: str = Field(
        max_length=50,
        description="Role code (e.g., 'admin', 'doctor', 'manager')",
    )
    name: str = Field(
        max_length=100,
        description="Human-readable role name",
    )
    description: Optional[str] = Field(
        default=None,
        description="Role description",
    )
    is_system: bool = Field(
        default=False,
        description="System roles cannot be deleted",
    )


class Role(RoleBase, PrimaryKeyMixin, TimestampMixin, table=True):
    """
    Role table model.

    Defines roles that group permissions together.
    System roles (is_system=True) are protected and cannot be deleted.
    """

    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("code", name="uq_roles_code"),)

    # Relationships
    permissions: list["RolePermission"] = Relationship(back_populates="role")
    users: list["UserRole"] = Relationship(back_populates="role")
