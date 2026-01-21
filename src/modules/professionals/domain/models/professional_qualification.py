"""ProfessionalQualification model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Index, UniqueConstraint, text
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import CouncilType, ProfessionalType
from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    SoftDeleteMixin,
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
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.modules.professionals.domain.models.professional_specialty import (
        ProfessionalSpecialty,
    )
    from src.modules.organizations.domain.models.organization import Organization


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
    SoftDeleteMixin,
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

    Multi-tenancy:
    - organization_id is denormalized for unique constraint on council registration
    - A council number + state must be unique within an organization
    """

    __tablename__ = "professional_qualifications"
    __table_args__ = (
        # Unique professional type per organization professional
        UniqueConstraint(
            "organization_professional_id",
            "professional_type",
            name="uq_professional_qualifications_org_professional_type",
        ),
        # Unique council registration per organization (when not soft-deleted)
        # The same professional can exist in multiple organizations
        Index(
            "uq_professional_qualifications_council_org",
            "organization_id",
            "council_number",
            "council_state",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # GIN trigram index for council number search
        Index(
            "idx_professional_qualifications_council_trgm",
            text("lower(council_number)"),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for professional type filtering
        Index(
            "idx_professional_qualifications_type",
            "professional_type",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for council type + state filtering
        Index(
            "idx_professional_qualifications_council",
            "council_type",
            "council_state",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree composite index for org + type filtering
        Index(
            "idx_professional_qualifications_org_type",
            "organization_id",
            "professional_type",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Organization reference (denormalized for unique constraint)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization ID (denormalized for unique constraint)",
    )

    organization_professional_id: UUID = Field(
        foreign_key="organization_professionals.id",
        nullable=False,
        description="Organization professional ID",
    )

    # Relationships
    organization: "Organization" = Relationship()
    professional: "OrganizationProfessional" = Relationship(
        back_populates="qualifications"
    )
    specialties: list["ProfessionalSpecialty"] = Relationship(
        back_populates="qualification"
    )
    educations: list["ProfessionalEducation"] = Relationship(
        back_populates="qualification"
    )
    documents: list["ProfessionalDocument"] = Relationship(
        back_populates="qualification"
    )
