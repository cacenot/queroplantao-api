"""Use case for retrieving current user's complete profile."""

from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.exceptions import NotFoundError
from src.modules.auth.domain.models import User, UserPermission, UserRole
from src.modules.auth.domain.schemas import (
    OrganizationMembershipInfo,
    ParentOrganizationInfo,
    PermissionInfo,
    RoleInfo,
    UserMeResponse,
)
from src.modules.organizations.domain.models.organization import Organization
from src.modules.organizations.domain.models.organization_membership import (
    OrganizationMembership,
)


class GetMeUseCase:
    """
    Use case for retrieving current user's complete profile.

    Returns user data including:
    - Basic profile info
    - Global roles
    - Direct permissions
    - Organization memberships with roles grouped by organization
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def execute(self, user_id: UUID) -> UserMeResponse:
        """
        Get current user's complete profile.

        Args:
            user_id: The authenticated user's UUID.

        Returns:
            UserMeResponse with complete user data.

        Raises:
            NotFoundError: If user not found.
        """
        # Load user with roles and permissions
        result = await self.session.execute(
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(UserRole.role),
                selectinload(User.permissions).selectinload(UserPermission.permission),
            )
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError(resource="User", identifier=str(user_id))

        # Load organization memberships with organization and parent
        memberships_result = await self.session.execute(
            select(OrganizationMembership)
            .where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.is_active.is_(True),
            )
            .options(
                selectinload(OrganizationMembership.organization).selectinload(
                    Organization.parent
                ),
                selectinload(OrganizationMembership.role),
            )
        )
        memberships = memberships_result.scalars().all()

        # Group memberships by organization
        org_memberships: dict[UUID, list[OrganizationMembership]] = defaultdict(list)
        for m in memberships:
            if m.organization:
                org_memberships[m.organization.id].append(m)

        # Build organization membership info with grouped roles
        organizations: list[OrganizationMembershipInfo] = []
        for org_id, org_members in org_memberships.items():
            # All memberships for same org have same organization data
            first = org_members[0]
            org = first.organization

            # Collect all roles for this organization
            roles = [
                RoleInfo(
                    id=m.role.id,
                    code=m.role.code,
                    name=m.role.name,
                )
                for m in org_members
                if m.role
            ]

            organizations.append(
                OrganizationMembershipInfo(
                    organization_id=org.id,
                    organization_name=org.name,
                    is_active=any(m.is_active for m in org_members),
                    roles=roles,
                    parent=(
                        ParentOrganizationInfo(
                            id=org.parent.id,
                            name=org.parent.name,
                        )
                        if org.parent
                        else None
                    ),
                )
            )

        # Build response
        return UserMeResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            cpf=user.cpf,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            email_verified_at=user.email_verified_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[
                RoleInfo(
                    id=ur.role.id,
                    code=ur.role.code,
                    name=ur.role.name,
                )
                for ur in user.roles
                if ur.role
            ],
            permissions=[
                PermissionInfo(
                    id=up.permission.id,
                    code=up.permission.code,
                    name=up.permission.name,
                    module=up.permission.module,
                )
                for up in user.permissions
                if up.permission
            ],
            organizations=organizations,
        )
