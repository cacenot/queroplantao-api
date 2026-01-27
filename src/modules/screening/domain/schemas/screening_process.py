"""Schemas for ScreeningProcess."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.modules.screening.domain.models.enums import ScreeningStatus, StepType
from src.shared.domain.value_objects import CPF, Phone


class ScreeningProcessCreate(BaseModel):
    """
    Schema for creating a screening process (Step 1 - Conversation).

    This creates the screening with initial professional data collected
    during the first phone call (conversation step).
    """

    model_config = ConfigDict(from_attributes=True)

    # Professional identification (from conversation)
    professional_cpf: CPF = Field(
        description="Professional's CPF (11 digits)",
    )
    professional_name: str = Field(
        max_length=255,
        description="Professional's full name",
    )
    professional_phone: Phone = Field(
        description="Professional's phone number",
    )
    professional_email: Optional[EmailStr] = Field(
        default=None,
        description="Professional's email (optional)",
    )

    # Expected professional profile
    expected_professional_type: str = Field(
        max_length=50,
        description="Expected professional type (DOCTOR, NURSE, etc.)",
    )
    expected_specialty_id: Optional[UUID] = Field(
        default=None,
        description="Expected specialty ID (for doctors)",
    )

    # Assignment
    owner_id: Optional[UUID] = Field(
        default=None,
        description="User responsible for this screening (owner)",
    )

    # Client company (for outsourcing scenarios)
    client_company_id: Optional[UUID] = Field(
        default=None,
        description="Client company (empresa contratante)",
    )

    # Conversation notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the initial conversation",
    )


class ScreeningProcessUpdate(BaseModel):
    """Schema for updating a screening process (PATCH)."""

    model_config = ConfigDict(from_attributes=True)

    professional_email: Optional[EmailStr] = None
    professional_phone: Optional[str] = Field(
        default=None,
        max_length=20,
    )
    expected_professional_type: Optional[str] = Field(
        default=None,
        max_length=50,
    )
    expected_specialty_id: Optional[UUID] = None
    owner_id: Optional[UUID] = None
    current_actor_id: Optional[UUID] = None
    client_company_id: Optional[UUID] = None
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
    )


class ScreeningProcessApprove(BaseModel):
    """Schema for approving a screening process."""

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Approval notes",
    )


class ScreeningProcessReject(BaseModel):
    """Schema for rejecting a screening process."""

    model_config = ConfigDict(from_attributes=True)

    reason: str = Field(
        max_length=2000,
        description="Rejection reason",
    )


class ScreeningProcessListResponse(BaseModel):
    """Schema for screening process list (minimal fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ScreeningStatus
    professional_cpf: Optional[str]
    professional_name: Optional[str]
    professional_phone: Optional[str]
    professional_email: Optional[str]
    expected_professional_type: Optional[str]
    current_step_type: Optional[StepType]
    owner_id: Optional[UUID]
    current_actor_id: Optional[UUID]
    organization_professional_id: Optional[UUID]
    client_company_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]


class ScreeningProcessResponse(BaseModel):
    """Schema for full screening process response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    status: ScreeningStatus

    # Professional data
    professional_cpf: Optional[str]
    professional_name: Optional[str]
    professional_phone: Optional[str]
    professional_email: Optional[str]
    organization_professional_id: Optional[UUID]

    # Expected profile
    expected_professional_type: Optional[str]
    expected_specialty_id: Optional[UUID]

    # Assignment
    owner_id: Optional[UUID]
    current_actor_id: Optional[UUID]

    # Client company
    client_company_id: Optional[UUID]

    # Contract bindings
    professional_contract_id: Optional[UUID]
    client_contract_id: Optional[UUID]

    # Status fields
    current_step_type: Optional[StepType]
    rejection_reason: Optional[str]
    notes: Optional[str]

    # Timestamps
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]

    # Tracking
    created_by: Optional[UUID]
    updated_by: Optional[UUID]


class ScreeningProcessDetailResponse(ScreeningProcessResponse):
    """Schema for detailed screening process response with nested data."""

    # Nested relationships loaded on demand
    steps: Optional[list["ScreeningProcessStepResponse"]] = None
    required_documents: Optional[list["ScreeningRequiredDocumentResponse"]] = None


# Forward references
from src.modules.screening.domain.schemas.screening_process_step import (  # noqa: E402
    ScreeningProcessStepResponse,
)
from src.modules.screening.domain.schemas.screening_required_document import (  # noqa: E402
    ScreeningRequiredDocumentResponse,
)

ScreeningProcessDetailResponse.model_rebuild()
