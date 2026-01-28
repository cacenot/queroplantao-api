"""ProfessionalChangeDiff model - granular change tracking.

Stores individual field-level changes between professional versions.
Each diff represents a single field change with old and new values.

This enables:
- Detailed audit trails
- Easy diff visualization in UI
- Efficient querying of specific field changes
- Rollback capability (theoretically)
"""

from typing import TYPE_CHECKING, Any, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import ChangeType
from src.shared.domain.models.base import BaseModel
from src.shared.domain.models.mixins import PrimaryKeyMixin

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_version import (
        ProfessionalVersion,
    )


class ProfessionalChangeDiffBase(BaseModel):
    """Base fields for ProfessionalChangeDiff."""

    # Path to the changed field (JSON path notation)
    # Examples:
    #   "personal_info.full_name"
    #   "qualifications[0].council_number"
    #   "qualifications[0].specialties[1].rqe_number"
    #   "bank_accounts[0]" (for added/removed array items)
    field_path: str = Field(
        max_length=500,
        description="JSON path to the changed field (e.g., 'personal_info.email', 'qualifications[0].council_number')",
    )

    # Type of change
    change_type: ChangeType = Field(
        sa_type=SAEnum(ChangeType, name="change_type", create_constraint=False),
        description="Type of change: ADDED, MODIFIED, or REMOVED",
    )

    # Old value (null for ADDED changes)
    old_value: Optional[Any] = Field(
        default=None,
        sa_type=JSONB,
        description="Previous value (null for ADDED)",
    )

    # New value (null for REMOVED changes)
    new_value: Optional[Any] = Field(
        default=None,
        sa_type=JSONB,
        description="New value (null for REMOVED)",
    )


class ProfessionalChangeDiff(ProfessionalChangeDiffBase, PrimaryKeyMixin, table=True):
    """
    ProfessionalChangeDiff table model.

    Stores granular field-level changes for each version.
    Generated automatically by the use case when creating a new version.

    Field path examples:
    - "personal_info.full_name" → simple field change
    - "personal_info.phone" → contact change
    - "qualifications[0].council_number" → qualification field change
    - "qualifications[0].specialties[0].rqe_number" → nested entity change
    - "qualifications[1]" → added/removed qualification (whole object)
    - "bank_accounts[0].pix_key" → bank account field change

    Change type semantics:
    - ADDED: new_value is set, old_value is null
    - MODIFIED: both old_value and new_value are set
    - REMOVED: old_value is set, new_value is null
    """

    __tablename__ = "professional_change_diffs"
    __table_args__ = (
        # Index for finding diffs by version
        Index("ix_professional_change_diffs_version_id", "version_id"),
        # Index for finding changes to specific fields
        Index("ix_professional_change_diffs_field_path", "field_path"),
        # Composite index for field change queries
        Index(
            "ix_professional_change_diffs_version_field",
            "version_id",
            "field_path",
        ),
    )

    # Reference to the version this diff belongs to
    version_id: UUID = Field(
        foreign_key="professional_versions.id",
        nullable=False,
        description="Version this diff belongs to",
    )

    # Relationship back to version
    version: "ProfessionalVersion" = Relationship(back_populates="diffs")

    # === Properties ===

    @property
    def is_addition(self) -> bool:
        """Check if this is an addition change."""
        return self.change_type == ChangeType.ADDED

    @property
    def is_modification(self) -> bool:
        """Check if this is a modification change."""
        return self.change_type == ChangeType.MODIFIED

    @property
    def is_removal(self) -> bool:
        """Check if this is a removal change."""
        return self.change_type == ChangeType.REMOVED

    @property
    def is_nested_change(self) -> bool:
        """Check if this change is in a nested entity (contains array notation)."""
        return "[" in self.field_path

    @property
    def root_field(self) -> str:
        """Get the root field name (first part of path)."""
        if "." in self.field_path:
            return self.field_path.split(".")[0]
        if "[" in self.field_path:
            return self.field_path.split("[")[0]
        return self.field_path

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<ChangeDiff {self.change_type.value}: {self.field_path}>"
