"""ProfessionalCompany junction table for N:N relationship."""

from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    BaseModel,
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.organization_professional import (
        OrganizationProfessional,
    )
    from src.shared.domain.models.company import Company


class ProfessionalCompanyBase(BaseModel):
    """Base fields for ProfessionalCompany junction."""

    joined_at: AwareDatetime = AwareDatetimeField(
        sa_column_kwargs={"nullable": False},
        nullable=False,
        description="Timestamp when professional joined the company (UTC)",
    )
    left_at: AwareDatetime | None = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Timestamp when professional left the company (UTC)",
    )


class ProfessionalCompany(
    ProfessionalCompanyBase,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    table=True,
):
    """
    ProfessionalCompany junction table.

    Links professionals to companies in a N:N relationship.
    Multiple professionals can be associated with the same company
    (e.g., partners, associates).
    """

    __tablename__ = "professional_companies"
    __table_args__ = (
        UniqueConstraint(
            "organization_professional_id",
            "company_id",
            name="uq_professional_companies_org_professional_company",
        ),
    )

    # Foreign keys
    organization_professional_id: UUID = Field(
        foreign_key="organization_professionals.id",
        nullable=False,
        description="Organization professional ID",
    )
    company_id: UUID = Field(
        foreign_key="companies.id",
        nullable=False,
        description="Company ID",
    )

    # Relationships
    professional: "OrganizationProfessional" = Relationship(
        back_populates="professional_companies"
    )
    company: "Company" = Relationship(back_populates="professional_companies")
