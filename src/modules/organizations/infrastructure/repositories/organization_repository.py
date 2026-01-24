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

    async def get_family_ids(self, organization_id: UUID) -> list[UUID]:
        """
        Get all organization IDs in the family (parent + children/siblings).

        For a parent organization: returns [parent_id, child1_id, child2_id, ...]
        For a child organization: returns [parent_id, self_id, sibling1_id, sibling2_id, ...]

        The hierarchy is limited to 1 level: parent → children (no grandchildren).

        Args:
            organization_id: The organization UUID to get family for.

        Returns:
            List of all family organization UUIDs including the given organization.
        """
        # First, get the organization to determine if it's a parent or child
        result = await self.session.execute(
            select(Organization).where(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
        )
        org = result.scalar_one_or_none()

        if not org:
            # Organization not found, return just the requested ID as fallback
            return [organization_id]

        # Determine the root (parent) ID
        if org.parent_id is None:
            # This is a parent organization
            root_id = org.id
        else:
            # This is a child organization, use its parent as root
            root_id = org.parent_id

        # Get all organizations in the family: parent + all children
        family_result = await self.session.execute(
            select(Organization.id).where(
                Organization.deleted_at.is_(None),
                or_(
                    Organization.id == root_id,  # The parent
                    Organization.parent_id == root_id,  # All children
                ),
            )
        )
        return list(family_result.scalars().all())
