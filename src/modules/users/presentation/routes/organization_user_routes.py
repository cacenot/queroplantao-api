"""Routes for organization users management (/users)."""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi_restkit.filterset import filter_as_query
from src.shared.domain.schemas import PaginatedResponse, PaginationParams
from fastapi_restkit.sortingset import sorting_as_query

from src.app.constants.error_codes import UserErrorCodes
from src.app.dependencies import OrganizationContext
from src.modules.users.domain.schemas import (
    OrganizationUserInvite,
    OrganizationUserListItem,
    OrganizationUserResponse,
    OrganizationUserUpdate,
)
from src.modules.users.infrastructure.filters import (
    OrganizationUserFilter,
    OrganizationUserSorting,
)
from src.modules.users.presentation.dependencies import (
    GetOrganizationUserUC,
    InviteOrganizationUserUC,
    ListOrganizationUsersUC,
    RemoveOrganizationUserUC,
    UpdateOrganizationUserUC,
)
from src.shared.domain.schemas.common import ErrorResponse

router = APIRouter(prefix="/users", tags=["Organization Users"])


@router.get(
    "/",
    response_model=PaginatedResponse[OrganizationUserResponse],
    summary="List organization users",
    description="List all users (members) of the organization with their roles.",
)
async def list_users(
    ctx: OrganizationContext,
    use_case: ListOrganizationUsersUC,
    pagination: PaginationParams = Depends(),
    filters: OrganizationUserFilter = Depends(filter_as_query(OrganizationUserFilter)),
    sorting: OrganizationUserSorting = Depends(
        sorting_as_query(OrganizationUserSorting)
    ),
) -> PaginatedResponse[OrganizationUserResponse]:
    """List all users in the organization."""
    return await use_case.execute(
        organization_id=ctx.organization,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )


@router.get(
    "/summary",
    response_model=PaginatedResponse[OrganizationUserListItem],
    summary="List organization users (summary)",
    description="List users with simplified data: basic info and role.",
)
async def list_users_summary(
    ctx: OrganizationContext,
    use_case: ListOrganizationUsersUC,
    pagination: PaginationParams = Depends(),
    filters: OrganizationUserFilter = Depends(filter_as_query(OrganizationUserFilter)),
    sorting: OrganizationUserSorting = Depends(
        sorting_as_query(OrganizationUserSorting)
    ),
) -> PaginatedResponse[OrganizationUserListItem]:
    """List all users in the organization with simplified data."""
    return await use_case.execute_summary(
        organization_id=ctx.organization,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
    )


@router.post(
    "/invite",
    response_model=OrganizationUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invite user to organization",
    description="Send an invitation to a user to join the organization with a specific role.",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "Conflict - User already member or invitation already sent",
            "content": {
                "application/json": {
                    "examples": {
                        "already_member": {
                            "summary": "User already member",
                            "value": {
                                "code": UserErrorCodes.USER_ALREADY_MEMBER,
                                "message": "Usuário já é membro desta organização",
                            },
                        },
                        "invitation_sent": {
                            "summary": "Invitation already sent",
                            "value": {
                                "code": UserErrorCodes.INVITATION_ALREADY_SENT,
                                "message": "Já existe um convite pendente para este e-mail",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Role not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.ROLE_NOT_FOUND,
                        "message": "Função não encontrada",
                    },
                }
            },
        },
    },
)
async def invite_user(
    data: OrganizationUserInvite,
    ctx: OrganizationContext,
    use_case: InviteOrganizationUserUC,
) -> OrganizationUserResponse:
    """Invite a user to join the organization."""
    return await use_case.execute(
        organization_id=ctx.organization,
        data=data,
        invited_by=ctx.user,
    )


@router.get(
    "/{membership_id}",
    response_model=OrganizationUserResponse,
    summary="Get organization user",
    description="Get details of a specific organization member.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Membership not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.MEMBERSHIP_NOT_FOUND,
                        "message": "Associação não encontrada",
                    },
                }
            },
        },
    },
)
async def get_user(
    membership_id: UUID,
    ctx: OrganizationContext,
    use_case: GetOrganizationUserUC,
) -> OrganizationUserResponse:
    """Get a specific organization member."""
    return await use_case.execute(
        organization_id=ctx.organization,
        membership_id=membership_id,
    )


@router.patch(
    "/{membership_id}",
    response_model=OrganizationUserResponse,
    summary="Update organization user",
    description="Update a member's role or status in the organization.",
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Membership or role not found",
            "content": {
                "application/json": {
                    "examples": {
                        "membership_not_found": {
                            "summary": "Membership not found",
                            "value": {
                                "code": UserErrorCodes.MEMBERSHIP_NOT_FOUND,
                                "message": "Associação não encontrada",
                            },
                        },
                        "role_not_found": {
                            "summary": "Role not found",
                            "value": {
                                "code": UserErrorCodes.ROLE_NOT_FOUND,
                                "message": "Função não encontrada",
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_user(
    membership_id: UUID,
    data: OrganizationUserUpdate,
    ctx: OrganizationContext,
    use_case: UpdateOrganizationUserUC,
) -> OrganizationUserResponse:
    """Update a member's role or status."""
    return await use_case.execute(
        organization_id=ctx.organization,
        membership_id=membership_id,
        data=data,
        updated_by=ctx.user,
    )


@router.delete(
    "/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove user from organization",
    description="Remove a member from the organization.",
    responses={
        403: {
            "model": ErrorResponse,
            "description": "Cannot remove owner or self",
            "content": {
                "application/json": {
                    "examples": {
                        "cannot_remove_owner": {
                            "summary": "Cannot remove owner",
                            "value": {
                                "code": UserErrorCodes.CANNOT_REMOVE_OWNER,
                                "message": "Não é possível remover o dono da organização",
                            },
                        },
                        "cannot_remove_self": {
                            "summary": "Cannot remove self",
                            "value": {
                                "code": UserErrorCodes.CANNOT_REMOVE_SELF,
                                "message": "Não é possível remover a si mesmo da organização",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Membership not found",
            "content": {
                "application/json": {
                    "example": {
                        "code": UserErrorCodes.MEMBERSHIP_NOT_FOUND,
                        "message": "Associação não encontrada",
                    },
                }
            },
        },
    },
)
async def remove_user(
    membership_id: UUID,
    ctx: OrganizationContext,
    use_case: RemoveOrganizationUserUC,
) -> None:
    """Remove a member from the organization."""
    await use_case.execute(
        organization_id=ctx.organization,
        membership_id=membership_id,
        removed_by=ctx.user,
    )
