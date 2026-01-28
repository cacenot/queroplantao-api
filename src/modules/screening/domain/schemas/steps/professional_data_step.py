"""Professional data step schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.modules.screening.domain.schemas.steps.base import StepResponseBase


class ProfessionalDataStepCompleteRequest(BaseModel):
    """
    Request schema for completing professional data step.

    No data required - the use case validates that:
    - Professional is linked to the process
    - Professional has at least one qualification
    - Professional type matches expected (if configured)
    - Professional has expected specialty (if configured)
    """

    model_config = ConfigDict(from_attributes=True)


class ProfessionalDataStepResponse(StepResponseBase):
    """
    Response schema for professional data step.

    Includes reference to the professional record.
    """

    # Professional-specific fields
    professional_id: Optional[UUID] = None
    professional_version_id: Optional[UUID] = None
