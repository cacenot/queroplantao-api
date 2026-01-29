"""ScreeningAlert model - alerts raised during screening process."""

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, TypedDict
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Index
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship

from src.modules.screening.domain.models.enums import AlertCategory
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


# =============================================================================
# AlertNote TypedDict
# =============================================================================


class AlertNote(TypedDict):
    """
    Typed dictionary for alert notes.

    Each note represents a message/action in the alert history.
    """

    timestamp: str  # ISO datetime string
    user_id: str  # UUID as string
    user_name: str  # Name of the user who added the note
    user_role: str  # Role display name from database (e.g., 'Escalista')
    content: str  # Note content


def create_alert_note(
    user_id: UUID,
    user_name: str,
    user_role_name: str,
    content: str,
) -> AlertNote:
    """
    Create a new alert note with current timestamp.

    Args:
        user_id: The UUID of the user adding the note.
        user_name: The name of the user.
        user_role_name: The role display name (from database, already translated).
        content: The note content.

    Returns:
        AlertNote with all fields populated.
    """
    return AlertNote(
        timestamp=datetime.now(timezone.utc).isoformat(),
        user_id=str(user_id),
        user_name=user_name,
        user_role=user_role_name,
        content=content,
    )


# =============================================================================
# ScreeningAlert Model
# =============================================================================


class ScreeningAlertBase(BaseModel):
    """Base fields for ScreeningAlert."""

    reason: str = Field(
        max_length=2000,
        description="Reason for raising the alert",
    )
    category: AlertCategory = Field(
        sa_type=SAEnum(AlertCategory, name="alert_category", create_constraint=True),
        description="Category of the alert",
    )
    notes: list[AlertNote] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False, default=[]),
        description="History of notes added to this alert",
    )
    is_resolved: bool = Field(
        default=False,
        description="Whether the alert has been resolved",
    )


class ScreeningAlert(
    ScreeningAlertBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ScreeningAlert table model.

    Represents an alert raised during a screening process.
    Alerts can be created at any point during the screening workflow.

    Key behaviors:
    - Only one unresolved alert per process at a time
    - When created, process status changes to PENDING_SUPERVISOR
    - Process is blocked until alert is resolved or rejected
    - Resolving returns process to IN_PROGRESS
    - Rejecting sets process status to REJECTED

    Workflow:
    1. Escalista identifies risk during screening
    2. Creates alert with reason and category
    3. Process.status = PENDING_SUPERVISOR
    4. Process.current_actor_id = Process.supervisor_id
    5. Supervisor reviews and either:
       - Resolves: is_resolved=True, process continues
       - Rejects: is_resolved=True, process.status=REJECTED
    """

    __tablename__ = "screening_alerts"
    __table_args__ = (
        # Index for listing alerts by process
        Index("ix_screening_alerts_process_id", "process_id"),
        # Index for filtering unresolved alerts
        Index(
            "ix_screening_alerts_unresolved",
            "process_id",
            "is_resolved",
            postgresql_where="is_resolved = FALSE",
        ),
        # Index for filtering by category
        Index("ix_screening_alerts_category", "category"),
    )

    # Process reference
    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
        description="Screening process this alert belongs to",
    )

    # Resolution tracking
    resolved_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When the alert was resolved",
    )
    resolved_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who resolved the alert",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="alerts")

    # === Properties ===

    @property
    def is_pending(self) -> bool:
        """Check if alert is still pending resolution."""
        return not self.is_resolved

    def add_note(
        self,
        user_id: UUID,
        user_name: str,
        user_role_name: str,
        content: str,
    ) -> None:
        """
        Add a note to the alert history.

        Args:
            user_id: The UUID of the user adding the note.
            user_name: The name of the user.
            user_role_name: The role display name (from database, already translated).
            content: The note content.
        """
        note = create_alert_note(
            user_id=user_id,
            user_name=user_name,
            user_role_name=user_role_name,
            content=content,
        )
        # Create new list to trigger SQLAlchemy change detection
        self.notes = [*self.notes, note]
