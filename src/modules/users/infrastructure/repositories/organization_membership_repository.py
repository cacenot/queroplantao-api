"""OrganizationMembership repository for database operations."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi_restkit.pagination import PaginatedResponse, PaginationParams
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.modules.organizations.domain.models.organization import Organization
from src.modules.organizations.domain.models.organization_membership import (
    OrganizationMembership,
)
from src.modules.users.domain.models.role import Role
from src.modules.users.domain.models.user import User
from src.modules.users.infrastructure.filters import (
    OrganizationUserFilter,
    OrganizationUserSorting,
)
from src.shared.infrastructure.repositories import BaseRepository


class OrganizationMembershipRepository(BaseRepository[OrganizationMembership]):
    """Repository for OrganizationMembership entity."""

    model = OrganizationMembership

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _base_query(self):
        """Base query with eager loading of relationships."""
        return select(OrganizationMembership).options(
            selectinload(OrganizationMembership.user),
            selectinload(OrganizationMembership.role),
            selectinload(OrganizationMembership.organization),
        )

    async def list_for_organization(
        self,
        organization_id: UUID,
        pagination: PaginationParams,
        *,
        filters: OrganizationUserFilter | None = None,
        sorting: OrganizationUserSorting | None = None,
        include_pending: bool = True,
    ) -> PaginatedResponse[OrganizationMembership]:
        """
        List all memberships for an organization.

        Args:
            organization_id: Organization ID to filter by
            pagination: Pagination parameters
            filters: Optional filters (search, role, is_active)
            sorting: Optional sorting
            include_pending: Whether to include pending invitations

        Returns:
            Paginated list of memberships
        """
        query = self._base_query().where(
            OrganizationMembership.organization_id == organization_id
        )

        if not include_pending:
            query = query.where(
                OrganizationMembership.accepted_at.isnot(None)
                | OrganizationMembership.invited_at.is_(None)
            )

        return await self.list_paginated(
            pagination,
            filters=filters,
            sorting=sorting,
            base_query=query,
        )

    async def get_by_id_for_organization(
        self,
        membership_id: UUID,
        organization_id: UUID,
    ) -> OrganizationMembership | None:
        """
        Get a membership by ID, scoped to organization.

        Args:
            membership_id: Membership ID
            organization_id: Organization ID for scope

        Returns:
            Membership if found and belongs to org, None otherwise
        """
        result = await self.session.execute(
            self._base_query().where(
                and_(
                    OrganizationMembership.id == membership_id,
                    OrganizationMembership.organization_id == organization_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> list[OrganizationMembership]:
        """
        Get all memberships for a user in an organization.

        A user can have multiple roles (multiple memberships) in the same org.

        Args:
            user_id: User ID
            organization_id: Organization ID

        Returns:
            List of memberships (one per role)
        """
        result = await self.session.execute(
            self._base_query().where(
                and_(
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.organization_id == organization_id,
                )
            )
        )
        return list(result.scalars().all())

    async def get_by_user_org_role(
        self,
        user_id: UUID,
        organization_id: UUID,
        role_id: UUID,
    ) -> OrganizationMembership | None:
        """
        Get a specific membership by user, org, and role.

        Args:
            user_id: User ID
            organization_id: Organization ID
            role_id: Role ID

        Returns:
            Membership if exists, None otherwise
        """
        result = await self.session.execute(
            self._base_query().where(
                and_(
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.role_id == role_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def exists_by_user_and_organization(
        self,
        user_id: UUID,
        organization_id: UUID,
    ) -> bool:
        """
        Check if user has any membership in the organization.

        Args:
            user_id: User ID
            organization_id: Organization ID

        Returns:
            True if user has at least one membership
        """
        result = await self.session.execute(
            select(func.count(OrganizationMembership.id)).where(
                and_(
                    OrganizationMembership.user_id == user_id,
                    OrganizationMembership.organization_id == organization_id,
                )
            )
        )
        return (result.scalar() or 0) > 0

    async def exists_pending_invitation(
        self,
        email: str,
        organization_id: UUID,
    ) -> bool:
        """
        Check if there's a pending invitation for this email in the organization.

        Args:
            email: Email address to check
            organization_id: Organization ID

        Returns:
            True if pending invitation exists
        """
        result = await self.session.execute(
            select(func.count(OrganizationMembership.id))
            .join(User, OrganizationMembership.user_id == User.id)
            .where(
                and_(
                    User.email == email,
                    OrganizationMembership.organization_id == organization_id,
                    OrganizationMembership.invited_at.isnot(None),
                    OrganizationMembership.accepted_at.is_(None),
                )
            )
        )
        return (result.scalar() or 0) > 0

    async def create_membership(
        self,
        user_id: UUID,
        organization_id: UUID,
        role_id: UUID,
        granted_by: UUID | None = None,
        is_invitation: bool = False,
    ) -> OrganizationMembership:
        """
        Create a new membership.

        Args:
            user_id: User ID
            organization_id: Organization ID
            role_id: Role ID
            granted_by: User who granted the role
            is_invitation: Whether this is a pending invitation

        Returns:
            Created membership
        """
        now = datetime.now(UTC)

        membership = OrganizationMembership(
            user_id=user_id,
            organization_id=organization_id,
            role_id=role_id,
            granted_by=granted_by,
            granted_at=now,
            invited_at=now if is_invitation else None,
            accepted_at=None if is_invitation else now,
            is_active=True,
            created_by=granted_by,
        )

        self.session.add(membership)
        await self.session.flush()
        await self.session.refresh(
            membership, attribute_names=["user", "role", "organization"]
        )

        return membership

    async def accept_invitation(
        self,
        membership_id: UUID,
    ) -> OrganizationMembership | None:
        """
        Accept a pending invitation.

        Args:
            membership_id: Membership ID to accept

        Returns:
            Updated membership or None if not found
        """
        membership = await self.get_by_id(membership_id)
        if not membership:
            return None

        membership.accepted_at = datetime.now(UTC)
        await self.session.flush()
        await self.session.refresh(
            membership, attribute_names=["user", "role", "organization"]
        )

        return membership

    async def update_role(
        self,
        membership_id: UUID,
        new_role_id: UUID,
        updated_by: UUID | None = None,
    ) -> OrganizationMembership | None:
        """
        Update the role of a membership.

        Args:
            membership_id: Membership ID
            new_role_id: New role ID
            updated_by: User making the update

        Returns:
            Updated membership or None if not found
        """
        membership = await self.get_by_id(membership_id)
        if not membership:
            return None

        membership.role_id = new_role_id
        membership.granted_at = datetime.now(UTC)
        membership.granted_by = updated_by
        membership.updated_by = updated_by

        await self.session.flush()
        await self.session.refresh(
            membership, attribute_names=["user", "role", "organization"]
        )

        return membership

    async def deactivate(
        self,
        membership_id: UUID,
        deactivated_by: UUID | None = None,
    ) -> OrganizationMembership | None:
        """
        Deactivate a membership (soft remove from org).

        Args:
            membership_id: Membership ID
            deactivated_by: User performing the action

        Returns:
            Updated membership or None if not found
        """
        membership = await self.get_by_id(membership_id)
        if not membership:
            return None

        membership.is_active = False
        membership.updated_by = deactivated_by

        await self.session.flush()
        return membership

    async def deactivate_all_for_user(
        self,
        user_id: UUID,
        organization_id: UUID,
        deactivated_by: UUID | None = None,
    ) -> int:
        """
        Deactivate all memberships for a user in an organization.

        Args:
            user_id: User ID
            organization_id: Organization ID
            deactivated_by: User performing the action

        Returns:
            Number of memberships deactivated
        """
        memberships = await self.get_by_user_and_organization(user_id, organization_id)

        for membership in memberships:
            membership.is_active = False
            membership.updated_by = deactivated_by

        await self.session.flush()
        return len(memberships)

    async def get_user_organizations(
        self,
        user_id: UUID,
        active_only: bool = True,
    ) -> list[Organization]:
        """
        Get all organizations a user belongs to.

        Args:
            user_id: User ID
            active_only: Only return orgs where membership is active

        Returns:
            List of organizations
        """
        query = (
            select(Organization)
            .join(OrganizationMembership)
            .where(OrganizationMembership.user_id == user_id)
        )

        if active_only:
            query = query.where(OrganizationMembership.is_active == True)  # noqa: E712

        result = await self.session.execute(query)
        return list(result.scalars().all())
