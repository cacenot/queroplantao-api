"""Use case for inviting a user to an organization."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import Settings
from src.app.dependencies import get_settings
from src.app.exceptions import (
    InvitationAlreadySentError,
    RoleNotFoundError,
    UserAlreadyMemberError,
)
from src.modules.organizations.infrastructure.repositories import OrganizationRepository
from src.modules.users.domain.schemas import (
    OrganizationUserInvite,
    OrganizationUserResponse,
)
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
    RoleRepository,
    UserRepository,
)
from src.modules.users.infrastructure.services import (
    InvitationTokenService,
    get_invitation_token_service,
)
from src.shared.infrastructure.email import EmailService, get_email_service


class InviteOrganizationUserUseCase:
    """
    Use case for inviting a user to an organization.

    Handles two scenarios:
    1. User exists in system → Creates membership directly (can still send notification)
    2. User doesn't exist → Creates user placeholder, sends invitation email
    """

    def __init__(
        self,
        session: AsyncSession,
        email_service: EmailService | None = None,
        token_service: InvitationTokenService | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.membership_repository = OrganizationMembershipRepository(session)
        self.user_repository = UserRepository(session)
        self.role_repository = RoleRepository(session)
        self.org_repository = OrganizationRepository(session)
        self.email_service = email_service or get_email_service()
        self.token_service = token_service or get_invitation_token_service()
        self.settings = settings or get_settings()

    async def execute(
        self,
        organization_id: UUID,
        data: OrganizationUserInvite,
        invited_by: UUID,
    ) -> OrganizationUserResponse:
        """
        Invite a user to join an organization.

        Args:
            organization_id: The organization to invite to
            data: Invitation data (email, role_id, optional name)
            invited_by: User ID of the inviter

        Returns:
            Created membership (pending acceptance)

        Raises:
            RoleNotFoundError: If the specified role doesn't exist
            UserAlreadyMemberError: If user is already an active member
            InvitationAlreadySentError: If there's a pending invitation
        """
        # Validate role exists
        role = await self.role_repository.get_by_id(data.role_id)
        if not role:
            raise RoleNotFoundError()

        # Get organization for email
        organization = await self.org_repository.get_by_id(organization_id)

        # Get inviter for email
        inviter = await self.user_repository.get_by_id(invited_by)
        inviter_name = inviter.full_name if inviter else "Um administrador"

        # Check if user already exists
        existing_user = await self.user_repository.get_by_email(data.email)

        if existing_user:
            # User exists - check if already a member
            existing_memberships = (
                await self.membership_repository.get_by_user_and_organization(
                    user_id=existing_user.id,
                    organization_id=organization_id,
                )
            )

            active_membership = next(
                (m for m in existing_memberships if m.is_active and not m.is_pending),
                None,
            )
            if active_membership:
                raise UserAlreadyMemberError()

            # Check for pending invitation with same role
            pending_with_role = next(
                (
                    m
                    for m in existing_memberships
                    if m.is_pending and m.role_id == data.role_id
                ),
                None,
            )
            if pending_with_role:
                raise InvitationAlreadySentError()

            # Create membership as invitation (user will need to accept)
            membership = await self.membership_repository.create_membership(
                user_id=existing_user.id,
                organization_id=organization_id,
                role_id=data.role_id,
                granted_by=invited_by,
                is_invitation=True,
            )
        else:
            # User doesn't exist - create placeholder user and invitation
            from src.modules.users.domain.models import User

            new_user = User(
                firebase_uid=f"pending_{data.email}_{datetime.now(UTC).timestamp()}",
                email=data.email,
                full_name=data.full_name or data.email.split("@")[0],
                is_active=False,  # Will be activated on invitation accept
            )
            self.session.add(new_user)
            await self.session.flush()

            membership = await self.membership_repository.create_membership(
                user_id=new_user.id,
                organization_id=organization_id,
                role_id=data.role_id,
                granted_by=invited_by,
                is_invitation=True,
            )

        # Generate invitation token and link
        token = self.token_service.create_token(
            email=data.email,
            organization_id=organization_id,
            role_id=data.role_id,
            invited_by=invited_by,
            membership_id=membership.id,
        )
        invitation_link = self.token_service.get_invitation_link(token)

        # Send invitation email
        await self.email_service.send_invitation_email(
            to=data.email,
            invitee_name=data.full_name or "",
            organization_name=organization.name if organization else "Organização",
            inviter_name=inviter_name,
            role_name=role.name,
            invitation_link=invitation_link,
            expires_in_days=self.settings.INVITATION_TOKEN_EXPIRE_DAYS,
        )

        await self.session.commit()

        # Refresh to get relationships
        await self.session.refresh(
            membership, attribute_names=["user", "role", "organization"]
        )

        return OrganizationUserResponse.from_membership(membership)
