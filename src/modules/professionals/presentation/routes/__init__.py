"""Routes for the professionals module."""

from fastapi import APIRouter

from src.modules.professionals.presentation.routes.organization_professional_routes import (
    router as organization_professional_router,
)
from src.modules.professionals.presentation.routes.professional_company_routes import (
    router as professional_company_router,
)
from src.modules.professionals.presentation.routes.professional_document_routes import (
    router as professional_document_router,
)
from src.modules.professionals.presentation.routes.professional_education_routes import (
    router as professional_education_router,
)
from src.modules.professionals.presentation.routes.professional_qualification_routes import (
    router as professional_qualification_router,
)
from src.modules.professionals.presentation.routes.professional_specialty_routes import (
    router as professional_specialty_router,
)

# Create main professionals router
router = APIRouter(prefix="/professionals", tags=["Professionals"])

# Include all sub-routers
router.include_router(organization_professional_router)
router.include_router(professional_company_router)
router.include_router(professional_document_router)
router.include_router(professional_education_router)
router.include_router(professional_qualification_router)
router.include_router(professional_specialty_router)


__all__ = [
    "router",
    "organization_professional_router",
    "professional_company_router",
    "professional_document_router",
    "professional_education_router",
    "professional_qualification_router",
    "professional_specialty_router",
]
