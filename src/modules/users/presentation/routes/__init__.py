"""Users presentation routes."""

from fastapi import APIRouter

from src.modules.users.presentation.routes.invitation_routes import (
    router as invitation_router,
)
from src.modules.users.presentation.routes.me_routes import router as me_router
from src.modules.users.presentation.routes.organization_user_routes import (
    router as org_user_router,
)

# Main router that aggregates all user-related routes
router = APIRouter()

# Include sub-routers
router.include_router(me_router)  # /auth/me
router.include_router(org_user_router)  # /users
router.include_router(invitation_router)  # /invitations

__all__ = ["router", "me_router", "org_user_router", "invitation_router"]
