"""API v1 main router - aggregates all v1 endpoints."""

from fastapi import APIRouter

# Import module routers
from src.modules.auth.presentation.routes import router as auth_router
from src.modules.job_postings.presentation.routes import router as job_postings_router
from src.modules.organizations.presentation.routes import router as organizations_router
from src.modules.professionals.presentation.routes import router as professionals_router
from src.modules.schedules.presentation.routes import router as schedules_router
from src.modules.shifts.presentation.routes import router as shifts_router
from src.shared.presentation import enum_router, specialty_router


# Create main v1 router
router = APIRouter(prefix="/api/v1")

# Include module routers
router.include_router(auth_router)
router.include_router(professionals_router)
router.include_router(organizations_router)
router.include_router(schedules_router)
router.include_router(shifts_router)
router.include_router(job_postings_router)

# Include shared routers (global reference data)
router.include_router(enum_router)
router.include_router(specialty_router)
