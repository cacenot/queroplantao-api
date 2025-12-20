"""API v1 main router - aggregates all v1 endpoints."""

from fastapi import APIRouter


# Create main v1 router
router = APIRouter(prefix="/api/v1")

# TODO: Include sub-routers as they are created
# Example:
# from app.presentation.api.v1 import users, shifts, hospitals
# router.include_router(users.router, prefix="/users", tags=["Users"])
# router.include_router(shifts.router, prefix="/shifts", tags=["Shifts"])
# router.include_router(hospitals.router, prefix="/hospitals", tags=["Hospitals"])
