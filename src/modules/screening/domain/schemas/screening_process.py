"""Schemas for ScreeningProcess."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from src.modules.professionals.domain.schemas import SpecialtySummary
from src.modules.screening.domain.models.enums import (
    STEP_TYPE_METADATA,
    ScreeningStatus,
    StepStatus,
    StepType,
)
from src.modules.users.domain.schemas.organization_user import UserInfo
from src.shared.domain.value_objects import CPF, Phone

if TYPE_CHECKING:
    pass


class StepTypeInfo(BaseModel):
    """Summary for a screening step type with pt-BR labels."""

    model_config = ConfigDict(from_attributes=True)

    step_type: str
    title: str
    description: str
    status: StepStatus | None = None
    completed: bool = False
    current_step: bool = False


def _extract_step_type_value(step_type: StepType | StepTypeInfo | str) -> str:
    if isinstance(step_type, StepTypeInfo):
        return step_type.step_type
    if isinstance(step_type, StepType):
        return step_type.value
    return str(step_type)


def _build_step_type_payload(
    step_type: StepType | str,
    step_info: dict[str, dict[str, object]] | None = None,
    *,
    is_current: bool = False,
) -> StepTypeInfo:
    try:
        step_enum = (
            step_type if isinstance(step_type, StepType) else StepType(step_type)
        )
    except ValueError:
        step_type_value = str(step_type)
        step_state = step_info.get(step_type_value) if step_info else None
        return StepTypeInfo(
            step_type=step_type_value,
            title=step_type_value,
            description="",
            status=_coerce_step_status((step_state or {}).get("status")),
            completed=bool((step_state or {}).get("completed", False)),
            current_step=bool((step_state or {}).get("current_step", is_current)),
        )

    metadata = STEP_TYPE_METADATA[step_enum]
    step_state = step_info.get(step_enum.value) if step_info else None
    return StepTypeInfo(
        step_type=step_enum.value,
        title=metadata["title"],
        description=metadata["description"],
        status=_coerce_step_status((step_state or {}).get("status")),
        completed=bool((step_state or {}).get("completed", False)),
        current_step=bool((step_state or {}).get("current_step", is_current)),
    )


def _coerce_step_status(value: object | None) -> StepStatus | None:
    if value is None:
        return None
    if isinstance(value, StepStatus):
        return value
    try:
        return StepStatus(str(value))
    except ValueError:
        return None


class _StepTypeValidatorsMixin:
    """Mixin providing step type serializers and validators."""

    current_step_type: StepTypeInfo
    configured_step_types: list[StepTypeInfo]
    step_info: dict[str, dict[str, object]] | None

    @field_serializer("current_step_type")
    def _serialize_current_step_type(
        self, value: StepType | StepTypeInfo
    ) -> StepTypeInfo:
        if isinstance(value, StepTypeInfo):
            return value
        return _build_step_type_payload(value)

    @field_serializer("configured_step_types")
    def _serialize_configured_step_types(
        self, value: list[StepTypeInfo] | list[str]
    ) -> list[StepTypeInfo]:
        if not value:
            return []
        if isinstance(value[0], StepTypeInfo):
            return value  # type: ignore[return-value]
        return [_build_step_type_payload(step_type) for step_type in value]  # type: ignore[arg-type]

    @field_validator("current_step_type", mode="before")
    @classmethod
    def _parse_current_step_type(
        cls, value: StepType | StepTypeInfo | str
    ) -> StepTypeInfo:
        if isinstance(value, StepTypeInfo):
            return value
        return _build_step_type_payload(value)

    @field_validator("configured_step_types", mode="before")
    @classmethod
    def _parse_configured_step_types(
        cls, value: list[StepTypeInfo] | list[str]
    ) -> list[StepTypeInfo]:
        if not value:
            return []
        if isinstance(value[0], StepTypeInfo):
            return value  # type: ignore[return-value]
        return [_build_step_type_payload(step_type) for step_type in value]  # type: ignore[arg-type]

    @model_validator(mode="after")
    def _apply_step_info(self) -> Self:
        step_info = self.step_info or {}
        has_step_info = bool(step_info)
        current_type = _extract_step_type_value(self.current_step_type)
        configured_types = [
            _extract_step_type_value(step_type)
            for step_type in self.configured_step_types
        ]
        self.current_step_type = _build_step_type_payload(
            current_type,
            step_info,
            is_current=not has_step_info,
        )
        self.configured_step_types = [
            _build_step_type_payload(
                step_type,
                step_info,
                is_current=not has_step_info and step_type == current_type,
            )
            for step_type in configured_types
        ]
        return self


class ScreeningProcessCreate(BaseModel):
    """
    Schema for creating a screening process (Step 1 - Conversation).

    This creates the screening with initial professional data collected
    during the first phone call (conversation step).
    """

    model_config = ConfigDict(from_attributes=True)

    # Link to existing professional (optional)
    organization_professional_id: Optional[UUID] = Field(
        default=None,
        description="Existing organization professional ID. If provided, professional_cpf and professional_name may be omitted.",
    )

    # Professional identification (from conversation)
    professional_cpf: Optional[CPF] = Field(
        default=None,
        description="Professional's CPF (11 digits). Optional when organization_professional_id is provided.",
    )
    professional_name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's full name. Optional when organization_professional_id is provided.",
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

    # Client company (for outsourcing scenarios)
    client_company_id: Optional[UUID] = Field(
        default=None,
        description="Client company (empresa contratante)",
    )

    # Supervisor for alerts and document review
    supervisor_id: UUID = Field(
        description="Supervisor responsible for alert resolution and document review",
    )

    # Conversation notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes from the initial conversation",
    )

    @model_validator(mode="after")
    def _validate_identification(self) -> "ScreeningProcessCreate":
        if self.organization_professional_id is None:
            if self.professional_cpf is None:
                raise ValueError(
                    "professional_cpf is required when organization_professional_id is not provided"
                )
            if self.professional_name is None:
                raise ValueError(
                    "professional_name is required when organization_professional_id is not provided"
                )
        return self


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


class ScreeningProcessCancel(BaseModel):
    """Schema for cancelling a screening process."""

    model_config = ConfigDict(from_attributes=True)

    reason: str = Field(
        min_length=10,
        max_length=2000,
        description="Cancellation reason (required)",
    )


class OrganizationProfessionalSummary(BaseModel):
    """Summary of an organization professional for screening responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    cpf: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None


class ScreeningProcessResponse(_StepTypeValidatorsMixin, BaseModel):
    """Schema for screening process response (list and detail)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    status: ScreeningStatus

    # Step tracking (denormalized)
    current_step_type: StepTypeInfo
    configured_step_types: list[StepTypeInfo]
    step_info: dict[str, dict[str, object]] | None = Field(
        default=None,
        exclude=True,
    )

    # Professional data
    professional_cpf: Optional[str]
    professional_name: Optional[str]
    professional_phone: Optional[str]
    professional_email: Optional[str]
    organization_professional_id: Optional[UUID]
    professional: Optional[OrganizationProfessionalSummary] = None

    # Expected profile
    expected_professional_type: Optional[str]
    expected_specialty_id: Optional[UUID]
    expected_specialty: Optional[SpecialtySummary] = None

    # Assignment
    owner_id: Optional[UUID]
    current_actor_id: Optional[UUID]
    supervisor_id: UUID
    owner: Optional[UserInfo] = None
    current_actor: Optional[UserInfo] = None
    supervisor: Optional[UserInfo] = None

    # Client company
    client_company_id: Optional[UUID]

    # Contract bindings
    professional_contract_id: Optional[UUID]
    client_contract_id: Optional[UUID]

    # Status fields
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


# Alias for list - same schema, used for API clarity
ScreeningProcessListResponse = ScreeningProcessResponse


class ScreeningProcessDetailResponse(ScreeningProcessResponse):
    """Schema for detailed screening process response with nested data."""

    # Steps summary (ordered by order field)
    steps: Optional[list["StepSummaryResponse"]] = None

    # Documents (if needed for display)
    # NOTE: ScreeningRequiredDocumentResponse was renamed to ScreeningDocumentResponse
    required_documents: Optional[list["ScreeningDocumentResponse"]] = None


from src.modules.screening.domain.schemas.screening_document import (  # noqa: E402
    ScreeningDocumentResponse,
)
from src.modules.screening.domain.schemas.screening_process_step import (  # noqa: E402
    StepSummaryResponse,
)

ScreeningProcessDetailResponse.model_rebuild()
