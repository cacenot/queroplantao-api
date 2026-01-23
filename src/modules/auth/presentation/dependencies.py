"""Dependencies for auth presentation layer."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.auth.use_cases import GetMeUseCase, UpdateMeUseCase


def get_me_use_case(session: SessionDep) -> GetMeUseCase:
    """Factory for GetMeUseCase."""
    return GetMeUseCase(session)


def get_update_me_use_case(session: SessionDep) -> UpdateMeUseCase:
    """Factory for UpdateMeUseCase."""
    return UpdateMeUseCase(session)


GetMeUC = Annotated[GetMeUseCase, Depends(get_me_use_case)]
UpdateMeUC = Annotated[UpdateMeUseCase, Depends(get_update_me_use_case)]
