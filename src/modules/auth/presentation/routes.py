"""Auth module routes."""

from fastapi import APIRouter

from src.app.dependencies import CurrentContext
from src.modules.auth.domain.schemas import UserMeResponse
from src.modules.auth.presentation.dependencies import GetMeUC

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


# TODO: Add authentication endpoints
# @router.post("/login")
# @router.post("/register")
# @router.post("/refresh")
# @router.post("/logout")
