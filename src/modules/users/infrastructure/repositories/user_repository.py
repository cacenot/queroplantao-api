"""User repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.users.domain.models.user import User
from src.modules.users.domain.models.user_permission import UserPermission
from src.modules.users.domain.models.user_role import UserRole
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

    async def get_by_id_with_relations(self, user_id: UUID) -> User | None:
        """
        Get user by ID with eager loading of roles and permissions.

        Args:
            user_id: The user's UUID.

        Returns:
            User with roles and permissions loaded, or None if not found.
        """
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(UserRole.role),
                selectinload(User.permissions).selectinload(UserPermission.permission),
            )
        )
        return result.scalar_one_or_none()

    async def exists_by_cpf(self, cpf: str, *, exclude_id: UUID | None = None) -> bool:
        """
        Check if a user with the given CPF exists.

        Args:
            cpf: The CPF to check for.
            exclude_id: Optional user ID to exclude (for updates).

        Returns:
            True if a user with this CPF exists, False otherwise.
        """
        query = select(User.id).where(User.cpf == cpf)
        if exclude_id is not None:
            query = query.where(User.id != exclude_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None
