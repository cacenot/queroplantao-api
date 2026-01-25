"""Use case for accepting an organization invitation."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.exceptions import (
    InvitationAlreadyAcceptedError,
    InvitationExpiredError,
    InvitationInvalidTokenError,
    MembershipNotFoundError,
)
from src.app.i18n import UserMessages, get_message
from src.modules.organizations.infrastructure.repositories import OrganizationRepository
from src.modules.users.domain.schemas import InvitationAcceptResponse
from src.modules.users.infrastructure.repositories import (
    OrganizationMembershipRepository,
    UserRepository,
)
from src.modules.users.infrastructure.services import (
    InvitationTokenService,
    get_invitation_token_service,
)


class AcceptInvitationUseCase:
    """
    Use case for accepting an organization invitation.

    Validates the invitation token and marks the membership as accepted.
    For new users, activates their account.
    """

    def __init__(
        self,
        session: AsyncSession,
        token_service: InvitationTokenService | None = None,
    ) -> None:
        self.session = session
        self.membership_repository = OrganizationMembershipRepository(session)
        self.user_repository = UserRepository(session)
        self.org_repository = OrganizationRepository(session)
        self.token_service = token_service or get_invitation_token_service()

    async def execute(
        self,
        token: str,
        firebase_uid: str | None = None,
    ) -> InvitationAcceptResponse:
        """
        Accept an organization invitation.

        Args:
            token: The invitation token from the email
            firebase_uid: If provided, updates the user's Firebase UID (for new users)

        Returns:
            Acceptance confirmation with organization details

        Raises:
            InvitationInvalidTokenError: If token is invalid
            InvitationExpiredError: If token has expired
            MembershipNotFoundError: If membership not found
            InvitationAlreadyAcceptedError: If already accepted
        """
        # Validate token
        payload = self.token_service.validate_token(token)
        if not payload:
            raise InvitationInvalidTokenError()

        membership_id = UUID(payload["membership_id"])

        # Get membership
        membership = await self.membership_repository.get_by_id(membership_id)
        if not membership:
            raise MembershipNotFoundError()

        # Check if already accepted
        if membership.accepted_at is not None:
            raise InvitationAlreadyAcceptedError()

        # Accept invitation
        membership = await self.membership_repository.accept_invitation(membership_id)

        # Activate user if they were in pending state
        user = await self.user_repository.get_by_id(membership.user_id)
        if user and not user.is_active:
            user.is_active = True
            if firebase_uid:
                user.firebase_uid = firebase_uid

        await self.session.commit()

        # Get organization name for response
        organization = await self.org_repository.get_by_id(membership.organization_id)
        org_name = organization.name if organization else "Organização"

        # Get role name
        role_name = membership.role.name if membership.role else "Membro"

        return InvitationAcceptResponse(
            message=get_message(
                UserMessages.INVITATION_ACCEPTED, organization_name=org_name
            ),
            organization_id=membership.organization_id,
            organization_name=org_name,
            role_name=role_name,
        )
