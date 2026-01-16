"""Health check endpoint."""

from fastapi import APIRouter

from src.app.dependencies import get_settings
from src.shared.domain.schemas import HealthResponse


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API health status",
)
async def health_check() -> HealthResponse:
    """Return API health status."""
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.APP_ENV,
    )
