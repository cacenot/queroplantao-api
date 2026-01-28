"""ProfessionalVersion model - version history for professional data.

Implements a simplified Event Sourcing pattern for tracking all changes
to professional data. Each version contains a complete snapshot of the
professional's state at that point in time.

Key features:
- Complete data snapshot (not just diffs)
- Source tracking (DIRECT, SCREENING, IMPORT, API)
- Pending vs applied state for approval workflows
- Version numbering via database sequence
"""

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum, Index, Sequence, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import SourceType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.fields import AwareDatetimeField
from src.shared.domain.models.mixins import (
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.professionals.domain.models.professional_change_diff import (
        ProfessionalChangeDiff,
    )


# Database sequence for version numbers
professional_version_seq = Sequence("professional_version_number_seq")


class ProfessionalVersionBase(BaseModel):
    """Base fields for ProfessionalVersion."""

    # Version number (auto-incremented via DB sequence)
    version_number: int = Field(
        sa_column_kwargs={
            "server_default": professional_version_seq.next_value(),
            "nullable": False,
        },
        description="Sequential version number (auto-generated)",
    )

    # Complete snapshot of professional data at this version
    data_snapshot: dict[str, Any] = Field(
        default_factory=dict,
        sa_type=JSONB,
        description="Complete snapshot of professional data (ProfessionalDataSnapshot structure)",
    )

    # Is this the current/active version?
    is_current: bool = Field(
        default=False,
        description="Whether this is the currently active version",
    )

    # Source of this version change
    source_type: SourceType = Field(
        default=SourceType.DIRECT,
        sa_type=SAEnum(SourceType, name="source_type", create_constraint=False),
        description="How this version was created (DIRECT, SCREENING, IMPORT, API)",
    )

    # Reference to the source entity (e.g., screening_process_id)
    source_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the source entity (e.g., ScreeningProcess ID if source_type=SCREENING)",
    )

    # Application status
    applied_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this version was applied to the professional record",
    )
    applied_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who applied this version",
    )

    # Rejection info (if version was rejected)
    rejected_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="When this version was rejected",
    )
    rejected_by: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="User who rejected this version",
    )
    rejection_reason: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Reason for rejection",
    )

    # Notes
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notes about this version change",
    )


class ProfessionalVersion(
    ProfessionalVersionBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ProfessionalVersion table model.

    Stores complete snapshots of professional data for version history.
    Each change to professional data creates a new version with a full snapshot.

    Workflow:
    1. Before any change, current state is captured in a new version
    2. Changes are applied to the professional record
    3. New version is marked as is_current=True, previous is_current=False
    4. Diffs are calculated and stored in ProfessionalChangeDiff

    For screening:
    1. Version is created with is_current=False, applied_at=None
    2. Data is stored in snapshot but NOT applied to professional
    3. When screening step completes, version is applied
    4. applied_at, applied_by are set, is_current=True

    Query patterns:
    - Current version: WHERE professional_id = X AND is_current = TRUE
    - Version history: WHERE professional_id = X ORDER BY version_number DESC
    - Pending versions: WHERE applied_at IS NULL AND rejected_at IS NULL
    """

    __tablename__ = "professional_versions"
    __table_args__ = (
        # Index for finding current version of a professional
        Index(
            "ix_professional_versions_current",
            "professional_id",
            "is_current",
            postgresql_where=text("is_current = TRUE"),
        ),
        # Index for version history queries
        Index(
            "ix_professional_versions_professional_id",
            "professional_id",
        ),
        # Index for organization queries
        Index(
            "ix_professional_versions_organization_id",
            "organization_id",
        ),
        # Index for pending versions (not applied, not rejected)
        Index(
            "ix_professional_versions_pending",
            "organization_id",
            postgresql_where=text("applied_at IS NULL AND rejected_at IS NULL"),
        ),
        # Index for source tracking
        Index(
            "ix_professional_versions_source",
            "source_type",
            "source_id",
        ),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this version",
    )

    # Professional reference (nullable for CREATE operations where professional doesn't exist yet)
    professional_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organization_professionals.id",
        nullable=True,
        description="Professional this version belongs to (null for CREATE before professional exists)",
    )

    # Relationships
    professional: Optional["OrganizationProfessional"] = Relationship(
        back_populates="versions",
    )
    diffs: list["ProfessionalChangeDiff"] = Relationship(
        back_populates="version",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # === Properties ===

    @property
    def is_applied(self) -> bool:
        """Check if this version has been applied."""
        return self.applied_at is not None

    @property
    def is_rejected(self) -> bool:
        """Check if this version was rejected."""
        return self.rejected_at is not None

    @property
    def is_pending(self) -> bool:
        """Check if this version is pending application."""
        return not self.is_applied and not self.is_rejected

    @property
    def is_from_screening(self) -> bool:
        """Check if this version originated from a screening process."""
        return self.source_type == SourceType.SCREENING

    @property
    def has_diffs(self) -> bool:
        """Check if this version has associated diffs."""
        return len(self.diffs) > 0 if self.diffs else False
