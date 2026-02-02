"""DocumentType module exceptions."""

from typing import Any

from src.app.constants.error_codes import DocumentTypeErrorCodes
from src.app.exceptions.base import AppException
from src.app.i18n import DocumentTypeMessages, get_message


class DocumentTypeException(AppException):
    """Base exception for document type module errors."""

    def __init__(
        self,
        message: str,
        code: str = DocumentTypeErrorCodes.DOCUMENT_TYPE_NOT_FOUND,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


class DocumentTypeNotFoundError(DocumentTypeException):
    """Document type not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(DocumentTypeMessages.DOCUMENT_TYPE_NOT_FOUND),
            code=DocumentTypeErrorCodes.DOCUMENT_TYPE_NOT_FOUND,
            status_code=404,
            details=details,
        )


class DocumentTypeInUseError(DocumentTypeException):
    """Document type cannot be deleted because it is in use."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(DocumentTypeMessages.DOCUMENT_TYPE_IN_USE),
            code=DocumentTypeErrorCodes.DOCUMENT_TYPE_IN_USE,
            status_code=409,
            details=details,
        )
