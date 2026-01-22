"""Permission repository for database operations."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.auth.domain.models.permission import Permission
from src.shared.infrastructure.repositories import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    """Repository for Permission entity."""

    model = Permission

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_code(self, code: str) -> Permission | None:
        """
        Get permission by code.

        Args:
            code: The permission code (e.g., 'shift:create').

        Returns:
            Permission or None if not found.
        """
        result = await self.session.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    async def list_by_module(self, module: str) -> list[Permission]:
        """
        List all permissions for a specific module.

        Args:
            module: The module name (e.g., 'shifts', 'schedules').

        Returns:
            List of permissions for the module.
        """
        result = await self.session.execute(
            select(Permission).where(Permission.module == module)
        )
        return list(result.scalars().all())
