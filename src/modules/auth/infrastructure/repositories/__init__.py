"""
Auth module repositories.
"""

from src.modules.auth.infrastructure.repositories.permission_repository import (
    PermissionRepository,
)
from src.modules.auth.infrastructure.repositories.role_permission_repository import (
    RolePermissionRepository,
)
from src.modules.auth.infrastructure.repositories.role_repository import (
    RoleRepository,
)
from src.modules.auth.infrastructure.repositories.user_permission_repository import (
    UserPermissionRepository,
)
from src.modules.auth.infrastructure.repositories.user_repository import (
    UserRepository,
)
from src.modules.auth.infrastructure.repositories.user_role_repository import (
    UserRoleRepository,
)

__all__ = [
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
    "UserRoleRepository",
    "UserPermissionRepository",
    "RolePermissionRepository",
]
