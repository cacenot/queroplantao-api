"""Routes for invitation acceptance (public endpoints)."""

from fastapi import APIRouter, status

from src.app.constants.error_codes import UserErrorCodes
from src.modules.users.domain.schemas import (
    InvitationAcceptRequest,
    InvitationAcceptResponse,
)
from src.modules.users.presentation.dependencies import AcceptInvitationUC
from src.shared.domain.schemas.common import ErrorResponse

router = APIRouter(prefix="/invitations", tags=["Invitations"])


@router.post(
    "/accept",
    response_model=InvitationAcceptResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept invitation",
    description="Accept an organization invitation using the token from the email.",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Invalid token",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.INVITATION_INVALID_TOKEN,
                        "message": "Token de convite inválido",
                    },
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Invitation not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.MEMBERSHIP_NOT_FOUND,
                        "message": "Associação não encontrada",
                    },
                }
            },
        },
        409: {
            "model": ErrorResponse,
            "description": "Invitation already accepted",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.INVITATION_ALREADY_ACCEPTED,
                        "message": "Este convite já foi aceito",
                    },
                }
            },
        },
        410: {
            "model": ErrorResponse,
            "description": "Invitation expired",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.INVITATION_EXPIRED,
                        "message": "O convite expirou",
                    },
                }
            },
        },
    },
)
async def accept_invitation(
    data: InvitationAcceptRequest,
    use_case: AcceptInvitationUC,
) -> InvitationAcceptResponse:
    """
    Accept an organization invitation.

    This is a public endpoint that doesn't require authentication.
    The token in the request body contains the invitation details.
    """
    return await use_case.execute(token=data.token)
