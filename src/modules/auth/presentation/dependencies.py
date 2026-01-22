"""Dependencies for auth presentation layer."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.auth.use_cases import GetMeUseCase


def get_me_use_case(session: SessionDep) -> GetMeUseCase:
    """Factory for GetMeUseCase."""
    return GetMeUseCase(session)


GetMeUC = Annotated[GetMeUseCase, Depends(get_me_use_case)]
