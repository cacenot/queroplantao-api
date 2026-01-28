"""Dependencies for screening step routes."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.screening.use_cases.screening_step import (
    # CompleteClientValidationStepUseCase,  # BROKEN - commented out
    CompleteDocumentReviewStepUseCase,
    CompleteDocumentUploadStepUseCase,
    GoBackToStepUseCase,
)
from src.modules.screening.use_cases.screening_step.conversation import (
    CompleteConversationStepUseCase,
)
from src.modules.screening.use_cases.screening_step.professional_data import (
    CompleteProfessionalDataStepUseCase,
)


def get_complete_conversation_step_use_case(
    session: SessionDep,
) -> CompleteConversationStepUseCase:
    """Factory for CompleteConversationStepUseCase."""
    return CompleteConversationStepUseCase(session)


def get_complete_professional_data_step_use_case(
    session: SessionDep,
) -> CompleteProfessionalDataStepUseCase:
    """Factory for CompleteProfessionalDataStepUseCase."""
    return CompleteProfessionalDataStepUseCase(session)


def get_complete_document_upload_step_use_case(
    session: SessionDep,
) -> CompleteDocumentUploadStepUseCase:
    """Factory for CompleteDocumentUploadStepUseCase."""
    return CompleteDocumentUploadStepUseCase(session)


def get_complete_document_review_step_use_case(
    session: SessionDep,
) -> CompleteDocumentReviewStepUseCase:
    """Factory for CompleteDocumentReviewStepUseCase."""
    return CompleteDocumentReviewStepUseCase(session)


# =============================================================================
# COMMENTED OUT - BROKEN DUE TO REFACTORING
# CompleteClientValidationStepUseCase needs reimplementation
# =============================================================================
# def get_complete_client_validation_step_use_case(
#     session: SessionDep,
# ) -> CompleteClientValidationStepUseCase:
#     """Factory for CompleteClientValidationStepUseCase."""
#     return CompleteClientValidationStepUseCase(session)
# =============================================================================


def get_go_back_to_step_use_case(session: SessionDep) -> GoBackToStepUseCase:
    """Factory for GoBackToStepUseCase."""
    return GoBackToStepUseCase(session)


# Type aliases for cleaner route signatures
CompleteConversationStepUC = Annotated[
    CompleteConversationStepUseCase,
    Depends(get_complete_conversation_step_use_case),
]

CompleteProfessionalDataStepUC = Annotated[
    CompleteProfessionalDataStepUseCase,
    Depends(get_complete_professional_data_step_use_case),
]

CompleteDocumentUploadStepUC = Annotated[
    CompleteDocumentUploadStepUseCase,
    Depends(get_complete_document_upload_step_use_case),
]

CompleteDocumentReviewStepUC = Annotated[
    CompleteDocumentReviewStepUseCase,
    Depends(get_complete_document_review_step_use_case),
]

# =============================================================================
# COMMENTED OUT - BROKEN DUE TO REFACTORING
# =============================================================================
# CompleteClientValidationStepUC = Annotated[
#     CompleteClientValidationStepUseCase,
#     Depends(get_complete_client_validation_step_use_case),
# ]
# =============================================================================

GoBackToStepUC = Annotated[
    GoBackToStepUseCase,
    Depends(get_go_back_to_step_use_case),
]
