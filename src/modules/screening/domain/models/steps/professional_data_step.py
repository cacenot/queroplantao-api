"""Professional data step - comprehensive professional information collection."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.screening.domain.models.enums import StepType
from src.modules.screening.domain.models.steps.base_step import ScreeningStepMixin
from src.shared.domain.models.base import BaseModel

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_version import (
        ProfessionalVersion,
    )
    from src.modules.screening.domain.models.screening_process import ScreeningProcess


class ProfessionalDataStepBase(BaseModel):
    """
    Professional data step fields.

    This step collects ALL professional data in one place:
    - Personal info (name, CPF, address, contact, etc.)
    - Qualification (council registration, professional type)
    - Specialties (medical specialties with RQE)
    - Education (degrees, courses, certifications)

    Flow:
    1. User enters CPF
    2. If professional exists: show current data for review/complement
    3. If professional doesn't exist: create new
    4. All changes are tracked via ProfessionalVersion
    """

    # Reference to the professional record (created/updated)
    professional_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the OrganizationProfessional record created/updated",
    )

    # Link to version history
    professional_version_id: Optional[UUID] = Field(
        default=None,
        nullable=True,
        description="ID of the ProfessionalVersion created for this step",
    )


class ProfessionalDataStep(ProfessionalDataStepBase, ScreeningStepMixin, table=True):
    """
    Professional data step table.

    Collects comprehensive professional information:
    - Personal info (CPF, name, address, phone, email, etc.)
    - Qualification (council type, number, state, professional type)
    - Specialties (specialty, RQE, primary flag)
    - Education (level, institution, dates)

    Workflow:
    1. Professional or escalista enters CPF
    2. If exists: load current data, allow complement/review
    3. If new: fill complete form
    4. On submit: create ProfessionalVersion with snapshot
    5. Apply changes to real professional records
    6. Store version_id for audit trail
    """

    __tablename__ = "screening_professional_data_steps"
    __table_args__ = (
        UniqueConstraint(
            "process_id",
            name="uq_screening_professional_data_steps_process_id",
        ),
        Index("ix_screening_professional_data_steps_process_id", "process_id"),
        Index("ix_screening_professional_data_steps_status", "status"),
    )

    step_type: StepType = Field(
        default=StepType.PROFESSIONAL_DATA,
        sa_type=SAEnum(StepType, name="step_type", create_constraint=False),
    )

    process_id: UUID = Field(
        foreign_key="screening_processes.id",
        nullable=False,
    )

    # Foreign key to ProfessionalVersion
    professional_version_id: Optional[UUID] = Field(
        default=None,
        foreign_key="professional_versions.id",
        nullable=True,
        description="Version snapshot created during this step",
    )

    # Relationships
    process: "ScreeningProcess" = Relationship(back_populates="professional_data_step")
    professional_version: Optional["ProfessionalVersion"] = Relationship()

    @property
    def has_professional(self) -> bool:
        """Check if a professional record was created/linked."""
        return self.professional_id is not None

    @property
    def has_version(self) -> bool:
        """Check if a version snapshot was created."""
        return self.professional_version_id is not None
