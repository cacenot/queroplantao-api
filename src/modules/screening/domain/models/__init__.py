"""Screening module domain models."""

from src.modules.screening.domain.models.enums import (
    ChangeType,
    ClientValidationOutcome,
    ConversationOutcome,
    DocumentReviewStatus,
    RequiredDocumentStatus,
    ScreeningDocumentStatus,
    ScreeningStatus,
    SourceType,
    StepStatus,
    StepType,
)
from src.modules.screening.domain.models.organization_screening_settings import (
    OrganizationScreeningSettings,
    OrganizationScreeningSettingsBase,
)
from src.modules.screening.domain.models.screening_document import (
    ScreeningDocument,
    ScreeningDocumentBase,
)
from src.modules.screening.domain.models.screening_process import (
    ScreeningProcess,
    ScreeningProcessBase,
)
from src.modules.screening.domain.models.steps import (
    ClientValidationStep,
    ClientValidationStepBase,
    ConversationStep,
    ConversationStepBase,
    DocumentReviewStep,
    DocumentReviewStepBase,
    DocumentUploadStep,
    DocumentUploadStepBase,
    PaymentInfoStep,
    PaymentInfoStepBase,
    ProfessionalDataStep,
    ProfessionalDataStepBase,
    ScreeningStepMixin,
    SupervisorReviewStep,
    SupervisorReviewStepBase,
)

__all__ = [
    # Enums
    "ChangeType",
    "ClientValidationOutcome",
    "ConversationOutcome",
    "DocumentReviewStatus",
    "RequiredDocumentStatus",
    "ScreeningDocumentStatus",
    "ScreeningStatus",
    "SourceType",
    "StepStatus",
    "StepType",
    # Configuration models
    "OrganizationScreeningSettings",
    "OrganizationScreeningSettingsBase",
    # Process model
    "ScreeningProcess",
    "ScreeningProcessBase",
    # Document model (unified requirement + review)
    "ScreeningDocument",
    "ScreeningDocumentBase",
    # Step base mixin
    "ScreeningStepMixin",
    # Conversation step (required)
    "ConversationStep",
    "ConversationStepBase",
    # Professional data step (required) - includes qualification, specialties, education
    "ProfessionalDataStep",
    "ProfessionalDataStepBase",
    # Document steps (required)
    "DocumentUploadStep",
    "DocumentUploadStepBase",
    "DocumentReviewStep",
    "DocumentReviewStepBase",
    # Payment info step (optional) - includes bank account and company
    "PaymentInfoStep",
    "PaymentInfoStepBase",
    # Review step (optional)
    "SupervisorReviewStep",
    "SupervisorReviewStepBase",
    # Validation step (optional)
    "ClientValidationStep",
    "ClientValidationStepBase",
]
