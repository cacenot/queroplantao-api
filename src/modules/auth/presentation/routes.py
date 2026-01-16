"""Auth module routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])


# TODO: Add authentication endpoints
# @router.post("/login")
# @router.post("/register")
# @router.post("/refresh")
# @router.post("/logout")
