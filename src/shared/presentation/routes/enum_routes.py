"""Enum routes - Global reference data for frontend consumption."""

from fastapi import APIRouter

from src.modules.professionals.domain.models.enums import (
    PROFESSIONAL_TYPE_LABELS,
    PROFESSIONAL_TYPE_TO_COUNCIL,
    ProfessionalType,
)
from src.shared.domain.schemas.enum import ProfessionalTypeItem
from src.shared.presentation.dependencies import CurrentContext


router = APIRouter(prefix="/enums", tags=["Enums"])


@router.get(
    "/professional-types",
    response_model=list[ProfessionalTypeItem],
    summary="List professional types",
    description="List all professional types with PT-BR labels and associated council.",
)
async def list_professional_types(
    _context: CurrentContext,
) -> list[ProfessionalTypeItem]:
    """List all professional types with labels and associated councils."""
    return [
        ProfessionalTypeItem(
            value=pt.value,
            label=PROFESSIONAL_TYPE_LABELS.get(pt, pt.value),
            council=PROFESSIONAL_TYPE_TO_COUNCIL.get(pt, "OTHER").value,
        )
        for pt in ProfessionalType
    ]


# NOTE: document-types endpoint removed - DocumentType is now a database model
# Use /screening/document-types or /professionals/document-types endpoints instead
