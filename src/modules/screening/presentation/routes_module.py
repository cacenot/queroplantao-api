"""Screening module API routes."""

from fastapi import APIRouter

from src.modules.screening.presentation.routes import (
    document_router,
    process_router,
    public_router,
    step_router,
)

# Main router for authenticated endpoints
router = APIRouter(prefix="/screenings", tags=["Screening"])

# Include sub-routers
router.include_router(process_router)
router.include_router(step_router)
router.include_router(document_router)

# Public router for token-based access (no auth required)
public_screening_router = APIRouter(
    prefix="/public/screening", tags=["Screening Public"]
)
public_screening_router.include_router(public_router)
