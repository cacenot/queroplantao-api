"""RolePermission repository for database operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.users.domain.models.role_permission import RolePermission
from src.shared.infrastructure.repositories import BaseRepository


class RolePermissionRepository(BaseRepository[RolePermission]):
    """Repository for RolePermission junction entity."""

    model = RolePermission

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_role_and_permission(
        self, role_id: UUID, permission_id: UUID
    ) -> RolePermission | None:
        """
        Get a role-permission link.

        Args:
            role_id: The role UUID.
            permission_id: The permission UUID.

        Returns:
            RolePermission or None if not found.
        """
        result = await self.session.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_role(self, role_id: UUID) -> list[RolePermission]:
        """
        List all permissions for a role.

        Args:
            role_id: The role UUID.

        Returns:
            List of RolePermission with Permission loaded.
        """
        result = await self.session.execute(
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .options(selectinload(RolePermission.permission))
        )
        return list(result.scalars().all())

    async def list_permissions_for_roles(self, role_ids: list[UUID]) -> list[str]:
        """
        Get all permission codes for a list of roles.

        Args:
            role_ids: List of role UUIDs.

        Returns:
            List of unique permission codes.
        """
        if not role_ids:
            return []

        result = await self.session.execute(
            select(RolePermission)
            .where(RolePermission.role_id.in_(role_ids))
            .options(selectinload(RolePermission.permission))
        )
        permissions = result.scalars().all()
        return list({rp.permission.code for rp in permissions if rp.permission})
