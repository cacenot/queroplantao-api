"""Dependencies for users presentation layer."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.users.use_cases import (
    AcceptInvitationUseCase,
    GetMeUseCase,
    GetOrganizationUserUseCase,
    InviteOrganizationUserUseCase,
    ListOrganizationUsersUseCase,
    RemoveOrganizationUserUseCase,
    UpdateMeUseCase,
    UpdateOrganizationUserUseCase,
)


# =============================================================================
# Me Use Cases
# =============================================================================


def get_me_use_case(session: SessionDep) -> GetMeUseCase:
    """Factory for GetMeUseCase."""
    return GetMeUseCase(session)


def get_update_me_use_case(session: SessionDep) -> UpdateMeUseCase:
    """Factory for UpdateMeUseCase."""
    return UpdateMeUseCase(session)


GetMeUC = Annotated[GetMeUseCase, Depends(get_me_use_case)]
UpdateMeUC = Annotated[UpdateMeUseCase, Depends(get_update_me_use_case)]


# =============================================================================
# Organization User Use Cases
# =============================================================================


def get_list_organization_users_use_case(
    session: SessionDep,
) -> ListOrganizationUsersUseCase:
    """Factory for ListOrganizationUsersUseCase."""
    return ListOrganizationUsersUseCase(session)


def get_get_organization_user_use_case(
    session: SessionDep,
) -> GetOrganizationUserUseCase:
    """Factory for GetOrganizationUserUseCase."""
    return GetOrganizationUserUseCase(session)


def get_invite_organization_user_use_case(
    session: SessionDep,
) -> InviteOrganizationUserUseCase:
    """Factory for InviteOrganizationUserUseCase."""
    return InviteOrganizationUserUseCase(session)


def get_update_organization_user_use_case(
    session: SessionDep,
) -> UpdateOrganizationUserUseCase:
    """Factory for UpdateOrganizationUserUseCase."""
    return UpdateOrganizationUserUseCase(session)


def get_remove_organization_user_use_case(
    session: SessionDep,
) -> RemoveOrganizationUserUseCase:
    """Factory for RemoveOrganizationUserUseCase."""
    return RemoveOrganizationUserUseCase(session)


def get_accept_invitation_use_case(session: SessionDep) -> AcceptInvitationUseCase:
    """Factory for AcceptInvitationUseCase."""
    return AcceptInvitationUseCase(session)


ListOrganizationUsersUC = Annotated[
    ListOrganizationUsersUseCase, Depends(get_list_organization_users_use_case)
]
GetOrganizationUserUC = Annotated[
    GetOrganizationUserUseCase, Depends(get_get_organization_user_use_case)
]
InviteOrganizationUserUC = Annotated[
    InviteOrganizationUserUseCase, Depends(get_invite_organization_user_use_case)
]
UpdateOrganizationUserUC = Annotated[
    UpdateOrganizationUserUseCase, Depends(get_update_organization_user_use_case)
]
RemoveOrganizationUserUC = Annotated[
    RemoveOrganizationUserUseCase, Depends(get_remove_organization_user_use_case)
]
AcceptInvitationUC = Annotated[
    AcceptInvitationUseCase, Depends(get_accept_invitation_use_case)
]
