"""User repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.auth.domain.models.user import User
from src.modules.auth.domain.models.user_permission import UserPermission
from src.modules.auth.domain.models.user_role import UserRole
from src.shared.infrastructure.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity with role and permission loading."""

    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """
        Get user by Firebase UID with eager loading of roles and permissions.

        Args:
            firebase_uid: The Firebase Auth UID to search for.

        Returns:
            User with roles and permissions loaded, or None if not found.
        """
        result = await self.session.execute(
            select(User)
            .where(User.firebase_uid == firebase_uid)
            .options(
                selectinload(User.roles).selectinload(UserRole.role),
                selectinload(User.permissions).selectinload(UserPermission.permission),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: The email address to search for.

        Returns:
            User or None if not found.
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    def extract_role_codes(user: User) -> list[str]:
        """
        Extract role codes from user's roles relationship.

        Args:
            user: User with roles loaded.

        Returns:
            List of role code strings.
        """
        return [user_role.role.code for user_role in user.roles if user_role.role]

    @staticmethod
    def extract_permission_codes(user: User) -> list[str]:
        """
        Extract permission codes from user's direct permissions.

        Note: This only extracts direct user permissions, not role-based permissions.
        For role-based permissions, query RolePermission table.

        Args:
            user: User with permissions loaded.

        Returns:
            List of permission code strings.
        """
        return [
            user_perm.permission.code
            for user_perm in user.permissions
            if user_perm.permission
        ]
