"""Screening module enums for PostgreSQL."""

from enum import Enum


class StepType(str, Enum):
    """
    Fixed screening step types.

    Each step corresponds to a specific data collection or review phase
    in the professional screening process.
    """

    # Initial conversation phase
    CONVERSATION = "CONVERSATION"  # Pre-screening phone call

    # Data collection phases (can be separate or grouped)
    PROFESSIONAL_DATA = "PROFESSIONAL_DATA"  # Personal data (CPF, address, etc.)
    QUALIFICATION = "QUALIFICATION"  # Professional license/council registration
    SPECIALTY = "SPECIALTY"  # Medical specialties
    EDUCATION = "EDUCATION"  # Complementary education
    DOCUMENT_UPLOAD = "DOCUMENT_UPLOAD"  # Document uploads by professional
    COMPANY = "COMPANY"  # PJ company data
    BANK_ACCOUNT = "BANK_ACCOUNT"  # Bank account data

    # Review phases
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"  # Document verification by reviewer
    SUPERVISOR_REVIEW = "SUPERVISOR_REVIEW"  # Escalated review by supervisor

    # Client validation (optional)
    CLIENT_VALIDATION = "CLIENT_VALIDATION"  # Client company approval step


class ScreeningStatus(str, Enum):
    """
    Status of a screening process throughout its lifecycle.

    Tracks the overall macro state of the screening from creation to completion.
    Detailed progress is tracked via current_step_type + StepStatus.
    """

    DRAFT = "DRAFT"  # Created but not started
    IN_PROGRESS = "IN_PROGRESS"  # Process is active (any step in progress)
    APPROVED = "APPROVED"  # Screening approved and completed
    REJECTED = "REJECTED"  # Screening rejected
    EXPIRED = "EXPIRED"  # Screening expired before completion
    CANCELLED = "CANCELLED"  # Screening cancelled by organization


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


class DocumentReviewStatus(str, Enum):
    """
    Status of an individual document review.

    Each uploaded document is reviewed individually with one of these statuses.
    """

    PENDING = "PENDING"  # Awaiting verification
    APPROVED = "APPROVED"  # Document approved
    REJECTED = "REJECTED"  # Document rejected, needs re-upload
    ALERT = "ALERT"  # Alert flag, requires supervisor attention


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


class RequiredDocumentStatus(str, Enum):
    """
    Status of a required document in the screening process.

    Tracks the lifecycle of each document from upload request to approval.
    """

    PENDING_UPLOAD = "PENDING_UPLOAD"  # Waiting for document upload
    UPLOADED = "UPLOADED"  # Document uploaded, awaiting review
    APPROVED = "APPROVED"  # Document approved by reviewer
    REJECTED = "REJECTED"  # Document rejected, needs re-upload
    CORRECTION_NEEDED = "CORRECTION_NEEDED"  # Returned for correction after rejection
