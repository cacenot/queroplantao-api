"""Professional module exceptions."""

from typing import Any

from src.app.constants.error_codes import ProfessionalErrorCodes
from src.app.exceptions import AppException
from src.app.i18n import ProfessionalMessages, get_message


class ProfessionalException(AppException):
    """Base exception for professional module errors."""

    def __init__(
        self,
        message: str,
        code: str = ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            details=details,
        )


# =============================================================================
# Professional (OrganizationProfessional) Exceptions
# =============================================================================


class ProfessionalNotFoundError(ProfessionalException):
    """Professional not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.PROFESSIONAL_NOT_FOUND),
            code=ProfessionalErrorCodes.PROFESSIONAL_NOT_FOUND,
            status_code=404,
            details=details,
        )


class ProfessionalCpfExistsError(ProfessionalException):
    """Professional with this CPF already exists in organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.CPF_ALREADY_EXISTS),
            code=ProfessionalErrorCodes.CPF_ALREADY_EXISTS,
            status_code=409,
            details=details,
        )


class ProfessionalEmailExistsError(ProfessionalException):
    """Professional with this email already exists in organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.EMAIL_ALREADY_EXISTS),
            code=ProfessionalErrorCodes.EMAIL_ALREADY_EXISTS,
            status_code=409,
            details=details,
        )


# =============================================================================
# Qualification Exceptions
# =============================================================================


class QualificationNotFoundError(ProfessionalException):
    """Professional qualification not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.QUALIFICATION_NOT_FOUND),
            code=ProfessionalErrorCodes.QUALIFICATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class QualificationNotBelongsError(ProfessionalException):
    """Qualification does not belong to the professional."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.QUALIFICATION_NOT_BELONGS),
            code=ProfessionalErrorCodes.QUALIFICATION_NOT_BELONGS,
            status_code=422,
            details=details,
        )


class CouncilRegistrationExistsError(ProfessionalException):
    """Council registration already exists in organization."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.COUNCIL_REGISTRATION_EXISTS),
            code=ProfessionalErrorCodes.COUNCIL_REGISTRATION_EXISTS,
            status_code=409,
            details=details,
        )


class InvalidCouncilTypeError(ProfessionalException):
    """Invalid council type for professional type."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.INVALID_COUNCIL_TYPE),
            code=ProfessionalErrorCodes.INVALID_COUNCIL_TYPE,
            status_code=422,
            details=details,
        )


# =============================================================================
# Specialty Exceptions
# =============================================================================


class SpecialtyNotFoundError(ProfessionalException):
    """Professional specialty link not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.SPECIALTY_NOT_FOUND),
            code=ProfessionalErrorCodes.SPECIALTY_NOT_FOUND,
            status_code=404,
            details=details,
        )


class GlobalSpecialtyNotFoundError(ProfessionalException):
    """Global specialty reference not found."""

    def __init__(
        self,
        specialty_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        message = get_message(ProfessionalMessages.SPECIALTY_NOT_FOUND)
        if specialty_id:
            details = details or {}
            details["specialty_id"] = specialty_id
        super().__init__(
            message=message,
            code=ProfessionalErrorCodes.GLOBAL_SPECIALTY_NOT_FOUND,
            status_code=404,
            details=details,
        )


class SpecialtyAlreadyAssignedError(ProfessionalException):
    """Specialty is already assigned to the qualification."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.SPECIALTY_ALREADY_ASSIGNED),
            code=ProfessionalErrorCodes.SPECIALTY_ALREADY_ASSIGNED,
            status_code=409,
            details=details,
        )


class DuplicateSpecialtyIdsError(ProfessionalException):
    """Duplicate specialty IDs in request."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.DUPLICATE_SPECIALTY_IDS),
            code=ProfessionalErrorCodes.DUPLICATE_SPECIALTY_IDS,
            status_code=422,
            details=details,
        )


# =============================================================================
# Education Exceptions
# =============================================================================


class EducationNotFoundError(ProfessionalException):
    """Professional education not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.EDUCATION_NOT_FOUND),
            code=ProfessionalErrorCodes.EDUCATION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class QualificationIdRequiredError(ProfessionalException):
    """Qualification ID is required."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.QUALIFICATION_ID_REQUIRED),
            code=ProfessionalErrorCodes.QUALIFICATION_ID_REQUIRED,
            status_code=422,
            details=details,
        )


class LevelRequiredError(ProfessionalException):
    """Education level is required."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.LEVEL_REQUIRED),
            code=ProfessionalErrorCodes.LEVEL_REQUIRED,
            status_code=422,
            details=details,
        )


class CourseNameRequiredError(ProfessionalException):
    """Course name is required."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.COURSE_NAME_REQUIRED),
            code=ProfessionalErrorCodes.COURSE_NAME_REQUIRED,
            status_code=422,
            details=details,
        )


class InstitutionRequiredError(ProfessionalException):
    """Institution is required."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.INSTITUTION_REQUIRED),
            code=ProfessionalErrorCodes.INSTITUTION_REQUIRED,
            status_code=422,
            details=details,
        )


# =============================================================================
# Document Exceptions
# =============================================================================


class DocumentNotFoundError(ProfessionalException):
    """Professional document not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.DOCUMENT_NOT_FOUND),
            code=ProfessionalErrorCodes.DOCUMENT_NOT_FOUND,
            status_code=404,
            details=details,
        )


class DocumentQualificationCategoryError(ProfessionalException):
    """Document category is not valid for qualification-level documents."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.DOCUMENT_QUALIFICATION_CATEGORY),
            code=ProfessionalErrorCodes.DOCUMENT_QUALIFICATION_CATEGORY,
            status_code=422,
            details=details,
        )


class DocumentSpecialtyCategoryError(ProfessionalException):
    """Document category is not valid for specialty-level documents."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.DOCUMENT_SPECIALTY_CATEGORY),
            code=ProfessionalErrorCodes.DOCUMENT_SPECIALTY_CATEGORY,
            status_code=422,
            details=details,
        )


# =============================================================================
# Company Exceptions
# =============================================================================


class CompanyNotFoundError(ProfessionalException):
    """Professional company link not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.COMPANY_NOT_FOUND),
            code=ProfessionalErrorCodes.COMPANY_NOT_FOUND,
            status_code=404,
            details=details,
        )


class CompanyAlreadyLinkedError(ProfessionalException):
    """Company is already linked to the professional."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.COMPANY_ALREADY_LINKED),
            code=ProfessionalErrorCodes.COMPANY_ALREADY_LINKED,
            status_code=409,
            details=details,
        )


class BankNotFoundError(ProfessionalException):
    """Bank not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
        *,
        bank_code: str | None = None,
    ) -> None:
        if details is None and bank_code is not None:
            details = {"bank_code": bank_code}
        super().__init__(
            message=message or get_message(ProfessionalMessages.BANK_NOT_FOUND),
            code=ProfessionalErrorCodes.BANK_NOT_FOUND,
            status_code=404,
            details=details,
        )


# =============================================================================
# Version Exceptions
# =============================================================================


class VersionNotFoundError(ProfessionalException):
    """Professional version not found."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.VERSION_NOT_FOUND),
            code=ProfessionalErrorCodes.VERSION_NOT_FOUND,
            status_code=404,
            details=details,
        )


class VersionAlreadyAppliedError(ProfessionalException):
    """Version has already been applied."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.VERSION_ALREADY_APPLIED),
            code=ProfessionalErrorCodes.VERSION_ALREADY_APPLIED,
            status_code=409,
            details=details,
        )


class VersionAlreadyRejectedError(ProfessionalException):
    """Version has already been rejected."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message
            or get_message(ProfessionalMessages.VERSION_ALREADY_REJECTED),
            code=ProfessionalErrorCodes.VERSION_ALREADY_REJECTED,
            status_code=409,
            details=details,
        )


class VersionNotPendingError(ProfessionalException):
    """Version is not in pending state."""

    def __init__(
        self,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message or get_message(ProfessionalMessages.VERSION_NOT_PENDING),
            code=ProfessionalErrorCodes.VERSION_NOT_PENDING,
            status_code=422,
            details=details,
        )


class VersionFeatureNotSupportedError(ProfessionalException):
    """Snapshot feature is not yet supported."""

    def __init__(
        self,
        feature: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=get_message(
                ProfessionalMessages.VERSION_FEATURE_NOT_SUPPORTED, feature=feature
            ),
            code=ProfessionalErrorCodes.VERSION_FEATURE_NOT_SUPPORTED,
            status_code=501,
            details=details,
        )
