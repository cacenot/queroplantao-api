"""Screening step use cases."""

# =============================================================================
# COMMENTED OUT - BROKEN DUE TO REFACTORING
# CompleteClientValidationStepUseCase requires reimplementation
# =============================================================================
# from src.modules.screening.use_cases.screening_step.client_validation_step_complete_use_case import (
#     CompleteClientValidationStepUseCase,
# )
# =============================================================================

from src.modules.screening.use_cases.screening_step.conversation import (
    CompleteConversationStepUseCase,
)
from src.modules.screening.use_cases.screening_step.document_review import (
    CompleteDocumentReviewStepUseCase,
    ReviewDocumentUseCase,
)
from src.modules.screening.use_cases.screening_step.document_upload import (
    CompleteDocumentUploadStepUseCase,
    ConfigureDocumentsUseCase,
    ReuseDocumentUseCase,
    UploadDocumentUseCase,
)
from src.modules.screening.use_cases.screening_step.professional_data import (
    CompleteProfessionalDataStepUseCase,
)
from src.modules.screening.use_cases.screening_step.step_go_back_use_case import (
    GoBackToStepUseCase,
)

# Re-export simple step use case for backward compatibility
CompleteSimpleStepUseCase = CompleteProfessionalDataStepUseCase

__all__ = [
    # Client Validation - COMMENTED OUT (broken)
    # "CompleteClientValidationStepUseCase",
    # Conversation
    "CompleteConversationStepUseCase",
    # Document Review
    "CompleteDocumentReviewStepUseCase",
    "ReviewDocumentUseCase",
    # Document Upload
    "CompleteDocumentUploadStepUseCase",
    "ConfigureDocumentsUseCase",
    "ReuseDocumentUseCase",
    "UploadDocumentUseCase",
    # Professional Data
    "CompleteProfessionalDataStepUseCase",
    "CompleteSimpleStepUseCase",
    # Navigation
    "GoBackToStepUseCase",
]
