"""Screening module enums for PostgreSQL."""

from enum import Enum


class StepType(str, Enum):
    """
    Fixed screening step types.

    Each step corresponds to a specific data collection or review phase
    in the professional screening process.

    Order (fixed for MVP):
    1. CONVERSATION - Initial phone call (required)
    2. PROFESSIONAL_DATA - Personal + qualification + specialties + education (required)
    3. DOCUMENT_UPLOAD - Upload documents (required)
    4. DOCUMENT_REVIEW - Review uploaded documents (required)
    5. PAYMENT_INFO - Bank account + company if PJ (optional)
    6. SUPERVISOR_REVIEW - Escalated review (optional)
    7. CLIENT_VALIDATION - Client approval (optional)
    """

    # Initial conversation phase (required)
    CONVERSATION = "CONVERSATION"

    # Professional data collection (required)
    # Includes: personal info, qualification, specialties, education
    PROFESSIONAL_DATA = "PROFESSIONAL_DATA"

    # Document phases (required)
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"

    # Payment info (optional)
    # Includes: bank account + company (if PJ)
    PAYMENT_INFO = "PAYMENT_INFO"

    # Review phases (optional)
    SUPERVISOR_REVIEW = "SUPERVISOR_REVIEW"
    CLIENT_VALIDATION = "CLIENT_VALIDATION"


class SourceType(str, Enum):
    """
    Source of a professional version change.

    Tracks how/where the change originated for audit purposes.
    """

    DIRECT = "DIRECT"  # Direct API call (update endpoint)
    SCREENING = "SCREENING"  # Change via screening process
    IMPORT = "IMPORT"  # Bulk import
    API = "API"  # External API integration


class ChangeType(str, Enum):
    """
    Type of change in a professional version diff.

    Used in ProfessionalChangeDiff to categorize field changes.
    """

    ADDED = "ADDED"  # New field/entity added
    MODIFIED = "MODIFIED"  # Existing field/entity modified
    REMOVED = "REMOVED"  # Field/entity removed


class DocumentReviewStatus(str, Enum):
    """
    Status of an individual document review.

    Tracks the review outcome for a specific document.
    """

    PENDING = "PENDING"  # Not yet reviewed
    APPROVED = "APPROVED"  # Document approved
    REJECTED = "REJECTED"  # Document rejected, needs re-upload
    ALERT = "ALERT"  # Requires supervisor attention


class ScreeningStatus(str, Enum):
    """
    Status of a screening process throughout its lifecycle.

    Tracks the overall macro state of the screening from creation to completion.
    Detailed progress is tracked via the status of each configured step.
    """

    DRAFT = "DRAFT"  # Created but not started
    IN_PROGRESS = "IN_PROGRESS"  # Process is active (any step in progress)
    APPROVED = "APPROVED"  # Screening approved and completed
    REJECTED = "REJECTED"  # Screening rejected
    EXPIRED = "EXPIRED"  # Screening expired before completion
    CANCELLED = "CANCELLED"  # Screening cancelled by organization


class RequiredDocumentStatus(str, Enum):
    """
    Status of a required document in the screening workflow.

    Tracks document upload and review lifecycle.
    """

    PENDING_UPLOAD = "PENDING_UPLOAD"  # Waiting for professional to upload
    UPLOADED = "UPLOADED"  # Uploaded, waiting for review
    APPROVED = "APPROVED"  # Document approved
    REJECTED = "REJECTED"  # Document rejected, needs re-upload
    CORRECTION_NEEDED = "CORRECTION_NEEDED"  # Needs correction after review


class StepStatus(str, Enum):
    """
    Status of an individual screening step.

    Tracks the progress of a single step within the screening process.
    """

    PENDING = "PENDING"  # Not yet started
    IN_PROGRESS = "IN_PROGRESS"  # Currently being filled
    COMPLETED = "COMPLETED"  # Submitted, awaiting review
    APPROVED = "APPROVED"  # Validated and approved
    REJECTED = "REJECTED"  # Rejected, needs correction
    SKIPPED = "SKIPPED"  # Skipped (for optional steps)
    CORRECTION_NEEDED = "CORRECTION_NEEDED"  # Needs correction after review


class ScreeningDocumentStatus(str, Enum):
    """
    Status of a document in the screening workflow.

    Tracks the full lifecycle from requirement to approval.
    """

    # Initial state - waiting for professional to upload
    PENDING_UPLOAD = "PENDING_UPLOAD"

    # Uploaded, waiting for review
    PENDING_REVIEW = "PENDING_REVIEW"

    # Review outcomes
    APPROVED = "APPROVED"  # Document approved
    REJECTED = "REJECTED"  # Document rejected, needs re-upload
    ALERT = "ALERT"  # Requires supervisor attention

    # Special states
    REUSED = "REUSED"  # Document reused from a previous screening
    SKIPPED = "SKIPPED"  # Optional document explicitly skipped


class ConversationOutcome(str, Enum):
    """
    Outcome of the initial conversation step.

    Determines whether the screening proceeds or is rejected early.
    """

    PROCEED = "PROCEED"  # Continue to next steps
    REJECT = "REJECT"  # Reject and end screening


class ClientValidationOutcome(str, Enum):
    """
    Outcome of client company validation.

    Final decision from the contracting client.
    """

    APPROVED = "APPROVED"  # Client approved the professional
    REJECTED = "REJECTED"  # Client rejected the professional
