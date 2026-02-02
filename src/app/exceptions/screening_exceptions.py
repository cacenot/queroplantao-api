"""Domain-specific exceptions for Screening module."""

from starlette import status

from src.app.constants.error_codes import ScreeningErrorCodes
from src.app.exceptions.base import AppException
from src.app.i18n import ScreeningMessages, get_message


# =============================================================================
# PROCESS EXCEPTIONS
# =============================================================================


class ScreeningProcessNotFoundError(AppException):
    """Raised when screening process is not found."""

    def __init__(self, screening_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROCESS_NOT_FOUND),
            code=ScreeningErrorCodes.SCREENING_PROCESS_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"screening_id": screening_id},
        )


class ScreeningProcessActiveExistsError(AppException):
    """Raised when trying to create screening for professional with active screening."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROCESS_ACTIVE_EXISTS),
            code=ScreeningErrorCodes.SCREENING_PROCESS_ACTIVE_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
        )


class ScreeningProcessInvalidStatusError(AppException):
    """Raised when operation is invalid for current process status."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.PROCESS_INVALID_STATUS, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_PROCESS_INVALID_STATUS,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_status": current_status},
        )


class ScreeningProcessCannotApproveError(AppException):
    """Raised when screening cannot be approved in current status."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.PROCESS_CANNOT_APPROVE, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_PROCESS_CANNOT_APPROVE,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_status": current_status},
        )


class ScreeningProcessCannotRejectError(AppException):
    """Raised when screening cannot be rejected in current status."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.PROCESS_CANNOT_REJECT, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_PROCESS_CANNOT_REJECT,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_status": current_status},
        )


class ScreeningProcessCannotCancelError(AppException):
    """Raised when screening cannot be cancelled in current status."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.PROCESS_CANNOT_CANCEL, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_PROCESS_CANNOT_CANCEL,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_status": current_status},
        )


class ScreeningProcessIncompleteStepsError(AppException):
    """Raised when trying to complete screening with incomplete required steps."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROCESS_INCOMPLETE_STEPS),
            code=ScreeningErrorCodes.SCREENING_PROCESS_INCOMPLETE_STEPS,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


# =============================================================================
# STEP EXCEPTIONS
# =============================================================================


class ScreeningStepNotFoundError(AppException):
    """Raised when screening step is not found."""

    def __init__(self, step_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.STEP_NOT_FOUND),
            code=ScreeningErrorCodes.SCREENING_STEP_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"step_id": step_id},
        )


class ScreeningStepAlreadyCompletedError(AppException):
    """Raised when step is already completed."""

    def __init__(self, step_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.STEP_ALREADY_COMPLETED),
            code=ScreeningErrorCodes.SCREENING_STEP_ALREADY_COMPLETED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"step_id": step_id},
        )


class ScreeningStepSkippedError(AppException):
    """Raised when trying to modify a skipped step."""

    def __init__(self, step_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.STEP_SKIPPED),
            code=ScreeningErrorCodes.SCREENING_STEP_SKIPPED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"step_id": step_id},
        )


class ScreeningStepNotInProgressError(AppException):
    """Raised when step is not in progress."""

    def __init__(self, step_id: str, current_status: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.STEP_NOT_IN_PROGRESS),
            code=ScreeningErrorCodes.SCREENING_STEP_NOT_IN_PROGRESS,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"step_id": step_id, "current_status": current_status},
        )


class ScreeningStepNotPendingError(AppException):
    """Raised when step is not pending (expected PENDING status)."""

    def __init__(self, step_id: str, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.STEP_NOT_PENDING, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_STEP_NOT_PENDING,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"step_id": step_id, "current_status": current_status},
        )


class ScreeningStepInvalidTypeError(AppException):
    """Raised when step type doesn't match expected type for operation."""

    def __init__(self, expected: str, received: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.STEP_INVALID_TYPE,
                expected=expected,
                received=received,
            ),
            code=ScreeningErrorCodes.SCREENING_STEP_INVALID_TYPE,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"expected": expected, "received": received},
        )


class ScreeningStepCannotGoBackError(AppException):
    """Raised when cannot go back to a specific step."""

    def __init__(self, step_type: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.STEP_CANNOT_GO_BACK, step_type=step_type
            ),
            code=ScreeningErrorCodes.SCREENING_STEP_CANNOT_GO_BACK,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"step_type": step_type},
        )


# =============================================================================
# CONVERSATION STEP EXCEPTIONS
# =============================================================================


class ScreeningConversationRejectedError(AppException):
    """Raised when professional is rejected during conversation step."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.CONVERSATION_REJECTED),
            code=ScreeningErrorCodes.SCREENING_CONVERSATION_REJECTED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ScreeningStepNotAssignedToUserError(AppException):
    """Raised when step is not assigned to the user trying to complete it."""

    def __init__(self, step_id: str, user_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.STEP_NOT_ASSIGNED_TO_USER),
            code=ScreeningErrorCodes.SCREENING_STEP_NOT_ASSIGNED_TO_USER,
            status_code=status.HTTP_403_FORBIDDEN,
            details={"step_id": step_id, "user_id": user_id},
        )


# =============================================================================
# PROFESSIONAL DATA STEP EXCEPTIONS
# =============================================================================


class ScreeningProfessionalNotLinkedError(AppException):
    """Raised when no professional is linked to the screening process."""

    def __init__(self, screening_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROFESSIONAL_NOT_LINKED),
            code=ScreeningErrorCodes.SCREENING_PROFESSIONAL_NOT_LINKED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"screening_id": screening_id},
        )


class ScreeningProfessionalNoQualificationError(AppException):
    """Raised when professional has no qualification registered."""

    def __init__(self, professional_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROFESSIONAL_NO_QUALIFICATION),
            code=ScreeningErrorCodes.SCREENING_PROFESSIONAL_NO_QUALIFICATION,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"professional_id": professional_id},
        )


class ScreeningProfessionalTypeMismatchError(AppException):
    """Raised when professional type doesn't match expected type."""

    def __init__(self, expected: str, found: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.PROFESSIONAL_TYPE_MISMATCH,
                expected=expected,
                found=found,
            ),
            code=ScreeningErrorCodes.SCREENING_PROFESSIONAL_TYPE_MISMATCH,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"expected": expected, "found": found},
        )


class ScreeningSpecialtyMismatchError(AppException):
    """Raised when professional doesn't have the required specialty."""

    def __init__(self, specialty_id: str, professional_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.SPECIALTY_MISMATCH),
            code=ScreeningErrorCodes.SCREENING_SPECIALTY_MISMATCH,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"specialty_id": specialty_id, "professional_id": professional_id},
        )


# =============================================================================
# DOCUMENT STEP EXCEPTIONS
# =============================================================================


class ScreeningDocumentNotFoundError(AppException):
    """Raised when screening document is not found."""

    def __init__(self, document_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.DOCUMENT_NOT_FOUND),
            code=ScreeningErrorCodes.SCREENING_DOCUMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"document_id": document_id},
        )


class ScreeningDocumentInvalidStatusError(AppException):
    """Raised when document status does not allow an operation."""

    def __init__(self, current_status: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.DOCUMENT_INVALID_STATUS, status=current_status
            ),
            code=ScreeningErrorCodes.SCREENING_DOCUMENT_INVALID_STATUS,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"current_status": current_status},
        )


class ScreeningDocumentTypeMismatchError(AppException):
    """Raised when document type does not match expected type."""

    def __init__(self, expected: str, found: str) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.DOCUMENT_TYPE_MISMATCH,
                expected=expected,
                found=found,
            ),
            code=ScreeningErrorCodes.SCREENING_DOCUMENT_TYPE_MISMATCH,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"expected": expected, "found": found},
        )


class ScreeningDocumentReusePendingError(AppException):
    """Raised when trying to reuse a pending professional document."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.DOCUMENT_REUSE_PENDING),
            code=ScreeningErrorCodes.SCREENING_DOCUMENT_REUSE_PENDING,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ScreeningDocumentsNotUploadedError(AppException):
    """Raised when required documents are still pending upload."""

    def __init__(self, document_names: list[str] | None = None) -> None:
        docs = (
            ", ".join(document_names) if document_names else "Documentos obrigatórios"
        )
        super().__init__(
            message=get_message(
                ScreeningMessages.DOCUMENTS_NOT_UPLOADED, documents=docs
            ),
            code=ScreeningErrorCodes.SCREENING_DOCUMENTS_NOT_UPLOADED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"pending_documents": document_names} if document_names else None,
        )


class ScreeningDocumentsMissingRequiredError(AppException):
    """Raised when required documents are missing."""

    def __init__(self, missing_documents: list[str]) -> None:
        super().__init__(
            message=get_message(
                ScreeningMessages.DOCUMENTS_MISSING_REQUIRED,
                missing=", ".join(missing_documents),
            ),
            code=ScreeningErrorCodes.SCREENING_DOCUMENTS_MISSING_REQUIRED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"missing_documents": missing_documents},
        )


class ScreeningDocumentsPendingReviewError(AppException):
    """Raised when documents are still pending review."""

    def __init__(self, document_names: list[str] | None = None) -> None:
        docs = ", ".join(document_names) if document_names else "Documentos"
        super().__init__(
            message=get_message(
                ScreeningMessages.DOCUMENTS_PENDING_REVIEW, documents=docs
            ),
            code=ScreeningErrorCodes.SCREENING_DOCUMENTS_PENDING_REVIEW,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"pending_documents": document_names} if document_names else None,
        )


class ScreeningProcessHasRejectedDocumentsError(AppException):
    """Raised when process has rejected documents that need correction."""

    def __init__(self, document_names: list[str] | None = None) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROCESS_HAS_REJECTED_DOCUMENTS),
            code=ScreeningErrorCodes.SCREENING_PROCESS_HAS_REJECTED_DOCUMENTS,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"rejected_documents": document_names} if document_names else None,
        )


# =============================================================================
# ALERT EXCEPTIONS
# =============================================================================


class ScreeningAlertNotFoundError(AppException):
    """Raised when screening alert is not found."""

    def __init__(self, alert_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.ALERT_NOT_FOUND),
            code=ScreeningErrorCodes.SCREENING_ALERT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"alert_id": alert_id},
        )


class ScreeningAlertAlreadyExistsError(AppException):
    """Raised when trying to create alert but one already exists."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.ALERT_ALREADY_EXISTS),
            code=ScreeningErrorCodes.SCREENING_ALERT_ALREADY_EXISTS,
            status_code=status.HTTP_409_CONFLICT,
        )


class ScreeningAlertAlreadyResolvedError(AppException):
    """Raised when trying to resolve/reject an already resolved alert."""

    def __init__(self, alert_id: str) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.ALERT_ALREADY_RESOLVED),
            code=ScreeningErrorCodes.SCREENING_ALERT_ALREADY_RESOLVED,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={"alert_id": alert_id},
        )


class ScreeningProcessBlockedByAlertError(AppException):
    """Raised when trying to perform action on process blocked by alert."""

    def __init__(self) -> None:
        super().__init__(
            message=get_message(ScreeningMessages.PROCESS_BLOCKED_BY_ALERT),
            code=ScreeningErrorCodes.SCREENING_PROCESS_BLOCKED_BY_ALERT,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


# =============================================================================
# CLIENT VALIDATION EXCEPTIONS
# =============================================================================
