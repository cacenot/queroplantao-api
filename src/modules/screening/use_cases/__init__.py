"""Screening module use cases."""

# Screening Process use cases
from src.modules.screening.use_cases.screening_process import (
    ApproveScreeningProcessUseCase,
    CancelScreeningProcessUseCase,
    CreateScreeningProcessUseCase,
    GetScreeningProcessByTokenUseCase,
    GetScreeningProcessUseCase,
    ListMyScreeningProcessesUseCase,
    ListScreeningProcessesUseCase,
    RejectScreeningProcessUseCase,
)

# Screening Step use cases (new specific use cases)
from src.modules.screening.use_cases.screening_step import (
    CompleteClientValidationStepUseCase,
    CompleteConversationStepUseCase,
    CompleteDocumentReviewStepUseCase,
    CompleteDocumentUploadStepUseCase,
    CompleteSimpleStepUseCase,
    GoBackToStepUseCase,
)

# Screening Document use cases
from src.modules.screening.use_cases.screening_document import (
    ApproveDocumentUseCase,
    KeepExistingDocumentUseCase,
    RejectDocumentUseCase,
    RemoveRequiredDocumentUseCase,
    ReviewDocumentUseCase,
    SelectDocumentsUseCase,
    UploadScreeningDocumentUseCase,
)

# Screening Client Validation use cases
from src.modules.screening.use_cases.screening_validation import (
    SkipClientValidationUseCase,
)

__all__ = [
    # Process
    "ApproveScreeningProcessUseCase",
    "CancelScreeningProcessUseCase",
    "CreateScreeningProcessUseCase",
    "GetScreeningProcessByTokenUseCase",
    "GetScreeningProcessUseCase",
    "ListMyScreeningProcessesUseCase",
    "ListScreeningProcessesUseCase",
    "RejectScreeningProcessUseCase",
    # Steps (specific use cases)
    "CompleteClientValidationStepUseCase",
    "CompleteConversationStepUseCase",
    "CompleteDocumentReviewStepUseCase",
    "CompleteDocumentUploadStepUseCase",
    "CompleteSimpleStepUseCase",
    "GoBackToStepUseCase",
    # Documents
    "ApproveDocumentUseCase",
    "KeepExistingDocumentUseCase",
    "RejectDocumentUseCase",
    "RemoveRequiredDocumentUseCase",
    "ReviewDocumentUseCase",
    "SelectDocumentsUseCase",
    "UploadScreeningDocumentUseCase",
    # Validation
    "SkipClientValidationUseCase",
]
