"""Screening step models - specific models for each step type."""

from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.modules.screening.domain.models.steps.client_validation_step import (
    ClientValidationStep,
    ClientValidationStepBase,
)
from src.modules.screening.domain.models.steps.conversation_step import (
    ConversationStep,
    ConversationStepBase,
)
from src.modules.screening.domain.models.steps.document_review_step import (
    DocumentReviewStep,
    DocumentReviewStepBase,
)
from src.modules.screening.domain.models.steps.document_upload_step import (
    DocumentUploadStep,
    DocumentUploadStepBase,
)
from src.modules.screening.domain.models.steps.payment_info_step import (
    PaymentInfoStep,
    PaymentInfoStepBase,
)
from src.modules.screening.domain.models.steps.professional_data_step import (
    ProfessionalDataStep,
    ProfessionalDataStepBase,
)
from src.modules.screening.domain.models.steps.supervisor_review_step import (
    SupervisorReviewStep,
    SupervisorReviewStepBase,
)

__all__ = [
    # Base mixin
    "ScreeningStepMixin",
    # Conversation (required)
    "ConversationStep",
    "ConversationStepBase",
    # Professional data (required) - includes qualification, specialties, education
    "ProfessionalDataStep",
    "ProfessionalDataStepBase",
    # Documents (required)
    "DocumentUploadStep",
    "DocumentUploadStepBase",
    "DocumentReviewStep",
    "DocumentReviewStepBase",
    # Payment info (optional) - includes bank account and company
    "PaymentInfoStep",
    "PaymentInfoStepBase",
    # Review (optional)
    "SupervisorReviewStep",
    "SupervisorReviewStepBase",
    # Validation (optional)
    "ClientValidationStep",
    "ClientValidationStepBase",
]
