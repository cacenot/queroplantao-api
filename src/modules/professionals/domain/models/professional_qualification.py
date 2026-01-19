"""ProfessionalQualification model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import CouncilType, ProfessionalType
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
    from src.modules.professionals.domain.models.professional_education import (
        ProfessionalEducation,
    )
    from src.modules.professionals.domain.models.professional_profile import (
        ProfessionalProfile,
    )
    from src.modules.professionals.domain.models.professional_specialty import (
        ProfessionalSpecialty,
    )


class ProfessionalQualificationBase(BaseModel):
    """Base fields for ProfessionalQualification."""

    professional_type: ProfessionalType = Field(
        sa_type=SAEnum(
            ProfessionalType, name="professional_type", create_constraint=True
        ),
        description="Type of healthcare professional (DOCTOR, NURSE, etc.)",
    )
    is_primary: bool = Field(
        default=False,
        description="Whether this is the primary qualification",
    )
    graduation_year: Optional[int] = Field(
        default=None,
        description="Year of graduation for this qualification",
    )

    # Council registration
    council_type: CouncilType = Field(
        sa_type=SAEnum(CouncilType, name="council_type", create_constraint=True),
        description="Council type (CRM, COREN, etc.)",
    )
    council_number: str = Field(
        max_length=20,
        description="Council registration number",
    )
    council_state: str = Field(
        max_length=2,
        description="State where the council registration is valid (2 chars)",
    )


class ProfessionalQualification(
    ProfessionalQualificationBase,
    VerificationMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ProfessionalQualification table model.

    Represents a professional formation/qualification (e.g., Doctor, Nurse).
    A professional can have multiple qualifications (rare but possible cases
    like someone who is both a Doctor and a Nurse).

    Each qualification includes:
    - Professional type and graduation year
    - Council registration (CRM, COREN, etc.) - only one per qualification
    - Related specialties
    - Complementary education (specializations, courses, etc.)
    """

    __tablename__ = "professional_qualifications"
    __table_args__ = (
        UniqueConstraint(
            "professional_id",
            "professional_type",
            name="uq_professional_qualifications_professional_type",
        ),
    )

    professional_id: UUID = Field(
        foreign_key="professional_profiles.id",
        nullable=False,
        description="Professional profile ID",
    )

    # Relationships
    professional: "ProfessionalProfile" = Relationship(back_populates="qualifications")
    specialties: list["ProfessionalSpecialty"] = Relationship(
        back_populates="qualification"
    )
    educations: list["ProfessionalEducation"] = Relationship(
        back_populates="qualification"
    )
    documents: list["ProfessionalDocument"] = Relationship(
        back_populates="qualification"
    )
