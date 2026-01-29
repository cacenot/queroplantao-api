"""Message keys for i18n support."""

from enum import StrEnum


class AuthMessages(StrEnum):
    """Authentication and authorization message keys."""

    # Token errors
    MISSING_TOKEN = "auth.missing_token"
    INVALID_TOKEN = "auth.invalid_token"
    EXPIRED_TOKEN = "auth.expired_token"
    REVOKED_TOKEN = "auth.revoked_token"

    # Firebase errors
    FIREBASE_ERROR = "auth.firebase_error"
    FIREBASE_INIT_ERROR = "auth.firebase_init_error"
    FIREBASE_SERVICE_UNAVAILABLE = "auth.firebase_service_unavailable"
    FIREBASE_INTERNAL_ERROR = "auth.firebase_internal_error"

    # User errors
    USER_NOT_FOUND = "auth.user_not_found"
    USER_INACTIVE = "auth.user_inactive"
    CPF_ALREADY_IN_USE = "auth.cpf_already_in_use"

    # Cache errors
    CACHE_ERROR = "auth.cache_error"

    # General
    AUTHENTICATION_FAILED = "auth.authentication_failed"
    INSUFFICIENT_PERMISSIONS = "auth.insufficient_permissions"


class OrganizationMessages(StrEnum):
    """Organization-related message keys."""

    # Organization errors
    MISSING_ID = "organization.missing_id"
    INVALID_ID = "organization.invalid_id"
    NOT_FOUND = "organization.not_found"
    INACTIVE = "organization.inactive"
    INTERNAL_ERROR = "organization.internal_error"

    # Membership errors
    USER_NOT_MEMBER = "organization.user_not_member"
    MEMBERSHIP_INACTIVE = "organization.membership_inactive"
    MEMBERSHIP_PENDING = "organization.membership_pending"
    MEMBERSHIP_EXPIRED = "organization.membership_expired"

    # Child organization errors
    INVALID_CHILD_ID = "organization.invalid_child_id"
    CHILD_NOT_FOUND = "organization.child_not_found"
    CHILD_INACTIVE = "organization.child_inactive"
    CHILD_NOT_ALLOWED = "organization.child_not_allowed"
    NOT_CHILD_OF_PARENT = "organization.not_child_of_parent"


class ResourceMessages(StrEnum):
    """Generic resource message keys."""

    NOT_FOUND = "resource.not_found"
    NOT_FOUND_WITH_ID = "resource.not_found_with_id"
    CONFLICT = "resource.conflict"
    VALIDATION_ERROR = "resource.validation_error"


class ProfessionalMessages(StrEnum):
    """Professional module message keys."""

    # Duplicate errors
    CPF_ALREADY_EXISTS = "professional.cpf_already_exists"
    EMAIL_ALREADY_EXISTS = "professional.email_already_exists"
    COUNCIL_REGISTRATION_EXISTS = "professional.council_registration_exists"
    COMPANY_ALREADY_LINKED = "professional.company_already_linked"
    SPECIALTY_ALREADY_ASSIGNED = "professional.specialty_already_assigned"
    DUPLICATE_SPECIALTY_IDS = "professional.duplicate_specialty_ids"
    BANK_NOT_FOUND = "professional.bank_not_found"

    # Validation errors
    INVALID_COUNCIL_TYPE = "professional.invalid_council_type"
    QUALIFICATION_ID_REQUIRED = "professional.qualification_id_required"
    QUALIFICATION_NOT_BELONGS = "professional.qualification_not_belongs"
    SPECIALTY_ID_REQUIRED = "professional.specialty_id_required"
    LEVEL_REQUIRED = "professional.level_required"
    COURSE_NAME_REQUIRED = "professional.course_name_required"
    INSTITUTION_REQUIRED = "professional.institution_required"

    # Document validation
    DOCUMENT_QUALIFICATION_CATEGORY = "professional.document_qualification_category"
    DOCUMENT_SPECIALTY_CATEGORY = "professional.document_specialty_category"

    # Not found
    PROFESSIONAL_NOT_FOUND = "professional.not_found"
    QUALIFICATION_NOT_FOUND = "professional.qualification_not_found"
    DOCUMENT_NOT_FOUND = "professional.document_not_found"
    SPECIALTY_NOT_FOUND = "professional.specialty_not_found"
    COMPANY_NOT_FOUND = "professional.company_not_found"
    EDUCATION_NOT_FOUND = "professional.education_not_found"

    # Version errors
    VERSION_NOT_FOUND = "professional.version_not_found"
    VERSION_ALREADY_APPLIED = "professional.version_already_applied"
    VERSION_ALREADY_REJECTED = "professional.version_already_rejected"
    VERSION_NOT_PENDING = "professional.version_not_pending"
    VERSION_FEATURE_NOT_SUPPORTED = "professional.version_feature_not_supported"


class ScreeningMessages(StrEnum):
    """Message keys for Screening module."""

    # Process messages
    PROCESS_NOT_FOUND = "screening.process.not_found"
    PROCESS_ACTIVE_EXISTS = "screening.process.active_exists"
    PROCESS_INVALID_STATUS = "screening.process.invalid_status"
    PROCESS_ALREADY_COMPLETED = "screening.process.already_completed"
    PROCESS_CANNOT_APPROVE = "screening.process.cannot_approve"
    PROCESS_CANNOT_REJECT = "screening.process.cannot_reject"
    PROCESS_CANNOT_CANCEL = "screening.process.cannot_cancel"
    PROCESS_HAS_REJECTED_DOCUMENTS = "screening.process.has_rejected_documents"
    PROCESS_INCOMPLETE_STEPS = "screening.process.incomplete_steps"

    # Step messages
    STEP_NOT_FOUND = "screening.step.not_found"
    STEP_ALREADY_COMPLETED = "screening.step.already_completed"
    STEP_SKIPPED = "screening.step.skipped"
    STEP_NOT_IN_PROGRESS = "screening.step.not_in_progress"
    STEP_NOT_PENDING = "screening.step.not_pending"
    STEP_INVALID_TYPE = "screening.step.invalid_type"
    STEP_CANNOT_GO_BACK = "screening.step.cannot_go_back"
    STEP_NOT_ASSIGNED_TO_USER = "screening.step.not_assigned_to_user"

    # Conversation messages
    CONVERSATION_REJECTED = "screening.conversation.rejected"

    # Professional data messages
    PROFESSIONAL_NOT_LINKED = "screening.professional_data.not_linked"
    PROFESSIONAL_NO_QUALIFICATION = "screening.professional_data.no_qualification"
    PROFESSIONAL_TYPE_MISMATCH = "screening.professional_data.type_mismatch"
    SPECIALTY_MISMATCH = "screening.professional_data.specialty_mismatch"

    # Document messages
    DOCUMENTS_NOT_UPLOADED = "screening.documents.not_uploaded"
    DOCUMENTS_MISSING_REQUIRED = "screening.documents.missing_required"
    DOCUMENTS_PENDING_REVIEW = "screening.documents.pending_review"

    # Alert messages
    ALERT_NOT_FOUND = "screening.alert.not_found"
    ALERT_ALREADY_EXISTS = "screening.alert.already_exists"
    ALERT_ALREADY_RESOLVED = "screening.alert.already_resolved"
    PROCESS_BLOCKED_BY_ALERT = "screening.process.blocked_by_alert"


class UserMessages(StrEnum):
    """User management message keys."""

    # User errors
    USER_NOT_FOUND = "user.not_found"
    USER_ALREADY_MEMBER = "user.already_member"
    USER_NOT_MEMBER = "user.not_member"

    # Invitation errors
    INVITATION_SENT = "user.invitation_sent"
    INVITATION_ALREADY_SENT = "user.invitation_already_sent"
    INVITATION_NOT_FOUND = "user.invitation_not_found"
    INVITATION_EXPIRED = "user.invitation_expired"
    INVITATION_ALREADY_ACCEPTED = "user.invitation_already_accepted"
    INVITATION_INVALID_TOKEN = "user.invitation_invalid_token"
    INVITATION_ACCEPTED = "user.invitation_accepted"

    # Membership errors
    MEMBERSHIP_NOT_FOUND = "user.membership_not_found"
    MEMBERSHIP_UPDATED = "user.membership_updated"
    MEMBERSHIP_REMOVED = "user.membership_removed"
    CANNOT_REMOVE_OWNER = "user.cannot_remove_owner"
    CANNOT_REMOVE_SELF = "user.cannot_remove_self"

    # Role errors
    ROLE_NOT_FOUND = "user.role_not_found"
    INVALID_ROLE = "user.invalid_role"


class ValidationMessages(StrEnum):
    """Value object validation message keys."""

    # CPF
    CPF_MUST_BE_STRING = "validation.cpf_must_be_string"
    CPF_INVALID_LENGTH = "validation.cpf_invalid_length"
    CPF_ALL_SAME_DIGITS = "validation.cpf_all_same_digits"
    CPF_INVALID_CHECK_DIGIT = "validation.cpf_invalid_check_digit"

    # CNPJ
    CNPJ_MUST_BE_STRING = "validation.cnpj_must_be_string"
    CNPJ_INVALID_LENGTH = "validation.cnpj_invalid_length"
    CNPJ_ALL_SAME_DIGITS = "validation.cnpj_all_same_digits"
    CNPJ_INVALID_CHECK_DIGIT = "validation.cnpj_invalid_check_digit"

    # CPF/CNPJ
    CPF_CNPJ_MUST_BE_STRING = "validation.cpf_cnpj_must_be_string"
    CPF_CNPJ_INVALID = "validation.cpf_cnpj_invalid"

    # Phone
    PHONE_MUST_BE_STRING = "validation.phone_must_be_string"
    PHONE_INVALID = "validation.phone_invalid"
    PHONE_INVALID_FORMAT = "validation.phone_invalid_format"
    PHONE_UNABLE_TO_EXTRACT_DDI = "validation.phone_unable_to_extract_ddi"
    PHONE_UNABLE_TO_EXTRACT_DDD = "validation.phone_unable_to_extract_ddd"
    PHONE_UNABLE_TO_FORMAT = "validation.phone_unable_to_format"

    # CEP
    CEP_MUST_BE_STRING = "validation.cep_must_be_string"
    CEP_INVALID_LENGTH = "validation.cep_invalid_length"
    CEP_ALL_ZEROS = "validation.cep_all_zeros"

    # UF (State)
    UF_MUST_BE_STRING = "validation.uf_must_be_string"
    UF_INVALID_LENGTH = "validation.uf_invalid_length"
    UF_INVALID_CODE = "validation.uf_invalid_code"
