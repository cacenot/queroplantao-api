"""Invitation token service for generating and validating invitation tokens."""

from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import TypedDict
from uuid import UUID

import jwt

from src.app.config import Settings
from src.app.logging import get_logger

logger = get_logger(__name__)


class InvitationPayload(TypedDict):
    """Invitation token payload."""

    email: str
    organization_id: str
    role_id: str
    invited_by: str
    membership_id: str


class InvitationTokenService:
    """Service for creating and validating invitation tokens."""

    def __init__(self, settings: Settings) -> None:
        """Initialize invitation token service."""
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        self.expire_days = settings.INVITATION_TOKEN_EXPIRE_DAYS
        self.frontend_url = settings.FRONTEND_URL

    def create_token(
        self,
        email: str,
        organization_id: UUID,
        role_id: UUID,
        invited_by: UUID,
        membership_id: UUID,
    ) -> str:
        """
        Create a signed invitation token.

        Args:
            email: Email address of the invitee
            organization_id: Organization the user is being invited to
            role_id: Role being assigned
            invited_by: User ID of the inviter
            membership_id: ID of the created OrganizationMembership

        Returns:
            Signed JWT token
        """
        now = datetime.now(UTC)
        expire = now + timedelta(days=self.expire_days)

        payload = {
            "email": email,
            "organization_id": str(organization_id),
            "role_id": str(role_id),
            "invited_by": str(invited_by),
            "membership_id": str(membership_id),
            "iat": now,
            "exp": expire,
            "type": "invitation",
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        logger.info(
            "invitation_token_created",
            email=email,
            organization_id=str(organization_id),
            expires_at=expire.isoformat(),
        )

        return token

    def validate_token(self, token: str) -> InvitationPayload | None:
        """
        Validate an invitation token.

        Args:
            token: The JWT token to validate

        Returns:
            Invitation payload if valid, None if invalid/expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Verify token type
            if payload.get("type") != "invitation":
                logger.warning(
                    "invitation_token_invalid_type", token_type=payload.get("type")
                )
                return None

            return InvitationPayload(
                email=payload["email"],
                organization_id=payload["organization_id"],
                role_id=payload["role_id"],
                invited_by=payload["invited_by"],
                membership_id=payload["membership_id"],
            )

        except jwt.ExpiredSignatureError:
            logger.warning("invitation_token_expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("invitation_token_invalid", error=str(e))
            return None

    def get_invitation_link(self, token: str) -> str:
        """
        Generate the full invitation link.

        Args:
            token: The invitation token

        Returns:
            Full URL for accepting the invitation
        """
        return f"{self.frontend_url}/invitations/accept?token={token}"


@lru_cache
def get_invitation_token_service() -> InvitationTokenService:
    """Get cached invitation token service instance."""
    from src.app.dependencies import get_settings

    return InvitationTokenService(get_settings())
