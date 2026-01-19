"""ProfessionalSpecialty junction model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import ResidencyStatus
from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    TimestampMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.professionals.domain.models.professional_qualification import (
        ProfessionalQualification,
    )
    from src.modules.professionals.domain.models.specialty import Specialty


class ProfessionalSpecialtyBase(BaseModel):
    """Base fields for ProfessionalSpecialty."""

    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary specialty",
    )

    # RQE (Registro de Qualificação de Especialista) - specific for doctors
    rqe_number: Optional[str] = Field(
        default=None,
        max_length=20,
        description="RQE number (for doctors)",
    )
    rqe_state: Optional[str] = Field(
        default=None,
        max_length=2,
        description="State where RQE is registered (2 chars)",
    )

    # Residency status (for professionals in training)
    residency_status: ResidencyStatus = Field(
        default=ResidencyStatus.COMPLETED,
        sa_type=SAEnum(
            ResidencyStatus, name="residency_status", create_constraint=True
        ),
        description="Current residency/training status",
    )
    residency_institution: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Institution where residency is being done",
    )
    residency_expected_completion: Optional[str] = Field(
        default=None,
        description="Expected residency completion date (YYYY-MM-DD)",
    )

    # Verification
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to specialty certificate",
    )


class ProfessionalSpecialty(
    ProfessionalSpecialtyBase,
    VerificationMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    Junction table for Professional-Specialty N:N relationship.

    Contains additional fields beyond a simple junction:
    - RQE (Registro de Qualificação de Especialista) for doctors
    - Residency status for professionals in training
    - Verification status
    """

    __tablename__ = "professional_specialties"
    __table_args__ = (
        UniqueConstraint(
            "qualification_id",
            "specialty_id",
            name="uq_professional_specialties_qualification_specialty",
        ),
    )

    qualification_id: UUID = Field(
        foreign_key="professional_qualifications.id",
        nullable=False,
        description="Professional qualification ID",
    )
    specialty_id: UUID = Field(
        foreign_key="specialties.id",
        nullable=False,
        description="Specialty ID",
    )

    # Relationships
    qualification: "ProfessionalQualification" = Relationship(
        back_populates="specialties"
    )
    specialty: "Specialty" = Relationship(back_populates="professionals")
    documents: list["ProfessionalDocument"] = Relationship(back_populates="specialty")
