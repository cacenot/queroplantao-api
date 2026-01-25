"""Routes for current authenticated user (/auth/me)."""

from fastapi import APIRouter

from src.app.dependencies import CurrentContext
from src.modules.users.domain.schemas import UserMeResponse, UserMeUpdate
from src.modules.users.presentation.dependencies import GetMeUC, UpdateMeUC

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user",
    description="Get the authenticated user's profile with roles, permissions, and organizations.",
)
async def get_me(
    ctx: CurrentContext,
    use_case: GetMeUC,
) -> UserMeResponse:
    """Get current authenticated user's complete profile."""
    return await use_case.execute(user_id=ctx.user)


@router.patch(
    "/me",
    response_model=UserMeResponse,
    summary="Update current user",
    description="Update the authenticated user's profile. Only provided fields are updated (PATCH semantics).",
)
async def update_me(
    data: UserMeUpdate,
    ctx: CurrentContext,
    use_case: UpdateMeUC,
) -> UserMeResponse:
    """Update current authenticated user's profile."""
    return await use_case.execute(user_id=ctx.user, data=data)
