"""Role repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.models.role import Role
from src.shared.infrastructure.repositories import BaseRepository


class RoleRepository(BaseRepository[Role]):
    """Repository for Role entity."""

    model = Role

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_code(self, code: str) -> Role | None:
        """
        Get role by code.

        Args:
            code: The role code (e.g., 'admin', 'org_owner').

        Returns:
            Role or None if not found.
        """
        result = await self.session.execute(select(Role).where(Role.code == code))
        return result.scalar_one_or_none()

    async def list_system_roles(self) -> list[Role]:
        """
        List all system roles (is_system=True).

        Returns:
            List of system roles.
        """
        result = await self.session.execute(
            select(Role).where(Role.is_system.is_(True))
        )
        return list(result.scalars().all())
