"""Dependencies for screening step routes."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.screening.use_cases.screening_step import (
    CompleteClientValidationStepUseCase,
    CompleteConversationStepUseCase,
    CompleteDocumentReviewStepUseCase,
    CompleteDocumentUploadStepUseCase,
    CompleteSimpleStepUseCase,
    GoBackToStepUseCase,
)


def get_complete_conversation_step_use_case(
    session: SessionDep,
) -> CompleteConversationStepUseCase:
    """Factory for CompleteConversationStepUseCase."""
    return CompleteConversationStepUseCase(session)


def get_complete_simple_step_use_case(session: SessionDep) -> CompleteSimpleStepUseCase:
    """Factory for CompleteSimpleStepUseCase."""
    return CompleteSimpleStepUseCase(session)


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


def get_complete_client_validation_step_use_case(
    session: SessionDep,
) -> CompleteClientValidationStepUseCase:
    """Factory for CompleteClientValidationStepUseCase."""
    return CompleteClientValidationStepUseCase(session)


def get_go_back_to_step_use_case(session: SessionDep) -> GoBackToStepUseCase:
    """Factory for GoBackToStepUseCase."""
    return GoBackToStepUseCase(session)


# Type aliases for cleaner route signatures
CompleteConversationStepUC = Annotated[
    CompleteConversationStepUseCase,
    Depends(get_complete_conversation_step_use_case),
]

CompleteSimpleStepUC = Annotated[
    CompleteSimpleStepUseCase,
    Depends(get_complete_simple_step_use_case),
]

CompleteDocumentUploadStepUC = Annotated[
    CompleteDocumentUploadStepUseCase,
    Depends(get_complete_document_upload_step_use_case),
]

CompleteDocumentReviewStepUC = Annotated[
    CompleteDocumentReviewStepUseCase,
    Depends(get_complete_document_review_step_use_case),
]

CompleteClientValidationStepUC = Annotated[
    CompleteClientValidationStepUseCase,
    Depends(get_complete_client_validation_step_use_case),
]

GoBackToStepUC = Annotated[
    GoBackToStepUseCase,
    Depends(get_go_back_to_step_use_case),
]
