"""
Users module models.
"""

from src.modules.users.domain.models.permission import Permission, PermissionBase
from src.modules.users.domain.models.role import Role, RoleBase
from src.modules.users.domain.models.role_permission import RolePermission
from src.modules.users.domain.models.user import User, UserBase
from src.modules.users.domain.models.user_permission import UserPermission
from src.modules.users.domain.models.user_role import UserRole

__all__ = [
    # Base schemas
    "UserBase",
    "PermissionBase",
    "RoleBase",
    # Table models
    "User",
    "Permission",
    "Role",
    "RolePermission",
    "UserRole",
    "UserPermission",
]
