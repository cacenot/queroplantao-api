"""ProfessionalEducation model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Index, text
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import EducationLevel
from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    TimestampMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_qualification import (
        ProfessionalQualification,
    )


class ProfessionalEducationBase(BaseModel):
    """Base fields for ProfessionalEducation."""

    level: EducationLevel = Field(
        sa_type=SAEnum(EducationLevel, name="education_level", create_constraint=True),
        description="Education level (undergraduate, masters, etc.)",
    )
    course_name: str = Field(
        max_length=255,
        description="Name of the course/degree",
    )
    institution: str = Field(
        max_length=255,
        description="Educational institution name",
    )
    start_year: Optional[int] = Field(
        default=None,
        description="Year started",
    )
    end_year: Optional[int] = Field(
        default=None,
        description="Year completed (null if ongoing)",
    )
    is_completed: bool = Field(
        default=False,
        description="Whether the education is completed",
    )
    workload_hours: Optional[int] = Field(
        default=None,
        description="Total workload in hours (for courses)",
    )
    certificate_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL to certificate/diploma",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes",
    )


class ProfessionalEducation(
    ProfessionalEducationBase,
    VerificationMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ProfessionalEducation table model.

    Tracks educational background related to a specific qualification.
    Includes: specializations, masters, doctorate, courses, fellowships, etc.

    Linked to ProfessionalQualification to associate education with
    the correct professional formation (e.g., a cardiology specialization
    belongs to the Doctor qualification, not the Nurse qualification).
    """

    __tablename__ = "professional_educations"
    __table_args__ = (
        # GIN trigram index for search (course_name + institution)
        Index(
            "idx_professional_educations_search_trgm",
            text(
                "(COALESCE(f_unaccent(lower(course_name)), '') || ' ' || "
                "COALESCE(f_unaccent(lower(institution)), ''))"
            ),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
        ),
        # B-tree index for organization scope
        Index(
            "idx_professional_educations_org",
            "organization_id",
        ),
        # B-tree index for level filtering
        Index(
            "idx_professional_educations_level",
            "level",
        ),
        # B-tree index for is_completed filtering
        Index(
            "idx_professional_educations_completed",
            "is_completed",
        ),
    )

    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization ID (denormalized for scope queries)",
    )

    qualification_id: UUID = Field(
        sa_column=Column(
            ForeignKey("professional_qualifications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        description="Professional qualification ID",
    )

    # Relationships
    qualification: "ProfessionalQualification" = Relationship(
        back_populates="educations"
    )
