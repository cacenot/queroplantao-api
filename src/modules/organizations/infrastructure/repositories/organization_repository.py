"""Organization repository for database operations."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.organizations.domain.models import Organization, OrganizationMembership
from src.shared.infrastructure.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    """Repository for Organization model with membership operations."""

    model = Organization

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_id_with_parent(self, organization_id: UUID) -> Organization | None:
        """
        Get organization by ID with parent relationship loaded.

        Args:
            organization_id: The organization UUID.

        Returns:
            Organization with parent loaded, or None if not found.
        """
        result = await self.session.execute(
            select(Organization)
            .where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
            .options(selectinload(Organization.parent))
        )
        return result.scalar_one_or_none()

    async def get_active_by_id(self, organization_id: UUID) -> Organization | None:
        """
        Get active organization by ID.

        Args:
            organization_id: The organization UUID.

        Returns:
            Active organization or None if not found/inactive/deleted.
        """
        result = await self.session.execute(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.is_active.is_(True),
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_membership(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembership | None:
        """
        Get user's active membership in an organization.

        Returns the membership only if:
        - Membership exists
        - Membership is active
        - Membership is not expired

        Args:
            user_id: The user UUID.
            organization_id: The organization UUID.

        Returns:
            Active OrganizationMembership with role loaded, or None.
        """
        now = datetime.now(timezone.utc)
        result = await self.session.execute(
            select(OrganizationMembership)
            .where(
                and_(
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.is_active.is_(True),
                    or_(
                        OrganizationMembership.expires_at.is_(None),
                        OrganizationMembership.expires_at > now,
                    ),
                )
            )
            .options(selectinload(OrganizationMembership.role))
        )
        return result.scalar_one_or_none()

    async def is_child_of_parent(
        self,
        child_id: UUID,
        parent_id: UUID,
    ) -> bool:
        """
        Check if an organization is a child of another.

        Args:
            child_id: Potential child organization UUID.
            parent_id: Potential parent organization UUID.

        Returns:
            True if child_id's parent_id matches parent_id.
        """
        result = await self.session.execute(
            select(Organization.id).where(
                Organization.id == child_id,
                Organization.parent_id == parent_id,
                Organization.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none() is not None
