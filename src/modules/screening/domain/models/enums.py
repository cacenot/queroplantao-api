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
    DOCUMENTS = "DOCUMENTS"  # Document uploads
    COMPANY = "COMPANY"  # PJ company data
    BANK_ACCOUNT = "BANK_ACCOUNT"  # Bank account data

    # Review phases
    DOCUMENT_REVIEW = "DOCUMENT_REVIEW"  # Document verification by reviewer
    SUPERVISOR_REVIEW = "SUPERVISOR_REVIEW"  # Escalated review by supervisor


class ScreeningStatus(str, Enum):
    """
    Status of a screening process throughout its lifecycle.

    Tracks the overall state of the screening from creation to completion.
    """

    DRAFT = "DRAFT"  # Created but not started
    CONVERSATION = "CONVERSATION"  # In initial conversation phase
    IN_PROGRESS = "IN_PROGRESS"  # Collecting data
    PENDING_REVIEW = "PENDING_REVIEW"  # Waiting for document review
    UNDER_REVIEW = "UNDER_REVIEW"  # Documents being reviewed
    PENDING_CORRECTION = "PENDING_CORRECTION"  # Waiting for data/document correction
    ESCALATED = "ESCALATED"  # Escalated to supervisor for alert review
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
