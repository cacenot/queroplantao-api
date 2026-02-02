"""Step-specific response schemas."""

from src.modules.screening.domain.schemas.steps.base import StepResponseBase
from src.modules.screening.domain.schemas.steps.conversation_step import (
    ConversationStepResponse,
)
from src.modules.screening.domain.schemas.steps.document_review_step import (
    DocumentForReview,
    DocumentReviewStepCompleteRequest,
    DocumentReviewStepResponse,
    ReviewDocumentRequest,
)
from src.modules.screening.domain.schemas.steps.document_upload_step import (
    ConfigureDocumentsRequest,
    DocumentConfigItem,
    DocumentUploadStepCompleteRequest,
    DocumentUploadStepResponse,
    ScreeningDocumentSummary,
    UploadDocumentFormData,
)
from src.modules.screening.domain.schemas.steps.professional_data_step import (
    ProfessionalDataStepCompleteRequest,
    ProfessionalDataStepResponse,
)

__all__ = [
    # Base
    "StepResponseBase",
    # Conversation
    "ConversationStepResponse",
    # Professional Data
    "ProfessionalDataStepCompleteRequest",
    "ProfessionalDataStepResponse",
    # Document Upload
    "ConfigureDocumentsRequest",
    "DocumentConfigItem",
    "DocumentUploadStepCompleteRequest",
    "DocumentUploadStepResponse",
    "ScreeningDocumentSummary",
    "UploadDocumentFormData",
    # Document Review
    "DocumentForReview",
    "DocumentReviewStepCompleteRequest",
    "DocumentReviewStepResponse",
    "ReviewDocumentRequest",
]
