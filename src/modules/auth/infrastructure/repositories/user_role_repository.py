"""UserRole repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.auth.domain.models.user_role import UserRole
from src.shared.infrastructure.repositories import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    """Repository for UserRole junction entity."""

    model = UserRole

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_and_role(
        self, user_id: UUID, role_id: UUID
    ) -> UserRole | None:
        """
        Get a user-role link.

        Args:
            user_id: The user UUID.
            role_id: The role UUID.

        Returns:
            UserRole or None if not found.
        """
        result = await self.session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[UserRole]:
        """
        List all roles for a user.

        Args:
            user_id: The user UUID.

        Returns:
            List of UserRole with Role loaded.
        """
        result = await self.session.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .options(selectinload(UserRole.role))
        )
        return list(result.scalars().all())
