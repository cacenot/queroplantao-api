"""UserPermission repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.users.domain.models.user_permission import UserPermission
from src.shared.infrastructure.repositories import BaseRepository


class UserPermissionRepository(BaseRepository[UserPermission]):
    """Repository for UserPermission junction entity."""

    model = UserPermission

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_and_permission(
        self, user_id: UUID, permission_id: UUID
    ) -> UserPermission | None:
        """
        Get a user-permission link.

        Args:
            user_id: The user UUID.
            permission_id: The permission UUID.

        Returns:
            UserPermission or None if not found.
        """
        result = await self.session.execute(
            select(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[UserPermission]:
        """
        List all direct permissions for a user.

        Args:
            user_id: The user UUID.

        Returns:
            List of UserPermission with Permission loaded.
        """
        result = await self.session.execute(
            select(UserPermission)
            .where(UserPermission.user_id == user_id)
            .options(selectinload(UserPermission.permission))
        )
        return list(result.scalars().all())
