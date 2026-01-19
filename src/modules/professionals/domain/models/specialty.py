"""Specialty model."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SAEnum
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import ProfessionalType
from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_specialty import (
        ProfessionalSpecialty,
    )


class SpecialtyBase(BaseModel):
    """Base fields for Specialty."""

    code: str = Field(
        max_length=20,
        description="Specialty code from the council (e.g., CFM code for doctors)",
    )
    name: str = Field(
        max_length=100,
        description="Specialty name",
    )
    description: Optional[str] = Field(
        default=None,
        description="Specialty description",
    )
    professional_type: ProfessionalType = Field(
        sa_type=SAEnum(
            ProfessionalType, name="professional_type", create_constraint=True
        ),
        description="Type of professional that can have this specialty",
    )
    is_generalist: bool = Field(
        default=False,
        description="TRUE for 'General Practitioner', 'General Nurse', etc.",
    )
    requires_residency: bool = Field(
        default=False,
        description="Whether this specialty requires residency/specialization",
    )
    is_active: bool = Field(
        default=True,
        description="Whether this specialty is active",
    )


class Specialty(SpecialtyBase, PrimaryKeyMixin, TimestampMixin, table=True):
    """
    Specialty table model.

    Defines medical and healthcare specialties for professionals.
    Each specialty is associated with a professional type.
    """

    __tablename__ = "specialties"
    __table_args__ = (UniqueConstraint("code", name="uq_specialties_code"),)

    # Relationships
    professionals: list["ProfessionalSpecialty"] = Relationship(
        back_populates="specialty"
    )
