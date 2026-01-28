"""Screening use case dependency injection."""

from typing import Annotated

from fastapi import Depends

from src.app.dependencies import SessionDep
from src.modules.screening.use_cases import (
    CancelScreeningProcessUseCase,
    CreateScreeningProcessUseCase,
    FinalizeScreeningProcessUseCase,
    GetScreeningProcessByTokenUseCase,
    GetScreeningProcessUseCase,
    ListMyScreeningProcessesUseCase,
    ListScreeningProcessesUseCase,
    ReuseDocumentUseCase,
    ReviewDocumentUseCase,
)

# =============================================================================
# NOTE: The following use cases don't exist and were never implemented:
# - ApproveDocumentUseCase
# - KeepExistingDocumentUseCase
# - RejectDocumentUseCase
# - RemoveRequiredDocumentUseCase
# - SelectDocumentsUseCase
# - UploadScreeningDocumentUseCase
# - SkipClientValidationUseCase
# =============================================================================


# Process use case factories
def get_create_screening_process_use_case(
    session: SessionDep,
) -> CreateScreeningProcessUseCase:
    return CreateScreeningProcessUseCase(session)


def get_get_screening_process_use_case(
    session: SessionDep,
) -> GetScreeningProcessUseCase:
    return GetScreeningProcessUseCase(session)


def get_get_screening_process_by_token_use_case(
    session: SessionDep,
) -> GetScreeningProcessByTokenUseCase:
    return GetScreeningProcessByTokenUseCase(session)


def get_list_screening_processes_use_case(
    session: SessionDep,
) -> ListScreeningProcessesUseCase:
    return ListScreeningProcessesUseCase(session)


def get_list_my_screening_processes_use_case(
    session: SessionDep,
) -> ListMyScreeningProcessesUseCase:
    return ListMyScreeningProcessesUseCase(session)


def get_cancel_screening_process_use_case(
    session: SessionDep,
) -> CancelScreeningProcessUseCase:
    return CancelScreeningProcessUseCase(session)


def get_finalize_screening_process_use_case(
    session: SessionDep,
) -> FinalizeScreeningProcessUseCase:
    return FinalizeScreeningProcessUseCase(session)


def get_reuse_document_use_case(
    session: SessionDep,
) -> ReuseDocumentUseCase:
    return ReuseDocumentUseCase(session)


def get_review_document_use_case(session: SessionDep) -> ReviewDocumentUseCase:
    return ReviewDocumentUseCase(session)


# Type aliases for dependency injection
CreateScreeningProcessUC = Annotated[
    CreateScreeningProcessUseCase, Depends(get_create_screening_process_use_case)
]
GetScreeningProcessUC = Annotated[
    GetScreeningProcessUseCase, Depends(get_get_screening_process_use_case)
]
GetScreeningProcessByTokenUC = Annotated[
    GetScreeningProcessByTokenUseCase,
    Depends(get_get_screening_process_by_token_use_case),
]
ListScreeningProcessesUC = Annotated[
    ListScreeningProcessesUseCase, Depends(get_list_screening_processes_use_case)
]
ListMyScreeningProcessesUC = Annotated[
    ListMyScreeningProcessesUseCase, Depends(get_list_my_screening_processes_use_case)
]
CancelScreeningProcessUC = Annotated[
    CancelScreeningProcessUseCase, Depends(get_cancel_screening_process_use_case)
]
FinalizeScreeningProcessUC = Annotated[
    FinalizeScreeningProcessUseCase, Depends(get_finalize_screening_process_use_case)
]
ReuseDocumentUC = Annotated[ReuseDocumentUseCase, Depends(get_reuse_document_use_case)]
ReviewDocumentUC = Annotated[
    ReviewDocumentUseCase, Depends(get_review_document_use_case)
]
