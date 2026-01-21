"""Professionals module routes - aggregates all sub-routers."""

from fastapi import APIRouter

from src.modules.professionals.presentation.routes import (
    organization_professional_router,
    professional_company_router,
    professional_document_router,
    professional_education_router,
    professional_qualification_router,
    professional_specialty_router,
    specialty_router,
)


# Main router that aggregates all sub-routers
router = APIRouter()

# Include all sub-routers
router.include_router(organization_professional_router)
router.include_router(professional_document_router)
router.include_router(professional_education_router)
router.include_router(professional_qualification_router)
router.include_router(professional_specialty_router)
router.include_router(professional_company_router)
router.include_router(specialty_router)
