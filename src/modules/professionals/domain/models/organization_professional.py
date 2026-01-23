"""OrganizationProfessional model - tenant-scoped professional data."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Enum as SAEnum, Index, text
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import Gender, MaritalStatus
from src.shared.domain.models import (
    AddressMixin,
    BaseModel,
    CPFField,
    PhoneField,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VerificationMixin,
)

if TYPE_CHECKING:
    from src.modules.organizations.domain.models.organization import Organization
    from src.modules.professionals.domain.models.professional_company import (
        ProfessionalCompany,
    )
    from src.modules.professionals.domain.models.professional_document import (
        ProfessionalDocument,
    )
    from src.modules.professionals.domain.models.professional_qualification import (
        ProfessionalQualification,
    )
    from src.shared.domain.models.bank_account import BankAccount


class OrganizationProfessionalBase(BaseModel):
    """Base fields for OrganizationProfessional."""

    # Personal data
    full_name: str = Field(
        max_length=255,
        description="Professional's full name",
    )
    email: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Professional's email address",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[str] = CPFField(
        default=None,
        nullable=True,
        description="Brazilian CPF (11 digits, no formatting)",
    )
    birth_date: Optional[str] = Field(
        default=None,
        description="Date of birth (YYYY-MM-DD)",
    )
    nationality: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Nationality (e.g., 'Brasileiro', 'Portuguesa')",
    )
    gender: Optional[Gender] = Field(
        default=None,
        sa_type=SAEnum(Gender, name="gender", create_constraint=True),
        description="Gender: MALE or FEMALE",
    )
    marital_status: Optional[MaritalStatus] = Field(
        default=None,
        sa_type=SAEnum(MaritalStatus, name="marital_status", create_constraint=True),
        description="Marital status",
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=2048,
        description="Profile picture URL",
    )


class OrganizationProfessional(
    OrganizationProfessionalBase,
    AddressMixin,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    OrganizationProfessional table model.

    Stores professional data scoped to a specific organization.
    Each organization maintains its own professional records, isolated from others.
    The same person (by CPF) can exist in multiple organizations with different data.

    Multi-tenancy:
    - Data is isolated per organization_id
    - Unique constraint on (organization_id, cpf) ensures no duplicate CPFs within an org
    - Organizations cannot see or access other organizations' professionals
    """

    __tablename__ = "organization_professionals"
    __table_args__ = (
        # Unique CPF per organization (when CPF is set and not soft-deleted)
        Index(
            "uq_organization_professionals_org_cpf",
            "organization_id",
            "cpf",
            unique=True,
            postgresql_where=text("cpf IS NOT NULL AND deleted_at IS NULL"),
        ),
        # Unique email per organization (when email is set and not soft-deleted)
        Index(
            "uq_organization_professionals_org_email",
            "organization_id",
            "email",
            unique=True,
            postgresql_where=text("email IS NOT NULL AND deleted_at IS NULL"),
        ),
        # GIN trigram index for full-text search (name + email + cpf)
        Index(
            "idx_organization_professionals_search_trgm",
            text(
                "(COALESCE(f_unaccent(lower(full_name)), '') || ' ' || "
                "COALESCE(f_unaccent(lower(email)), '') || ' ' || "
                "COALESCE(cpf, ''))"
            ),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # GIN trigram index for name search
        Index(
            "idx_organization_professionals_full_name_trgm",
            text("f_unaccent(lower(full_name))"),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for created_at sorting
        Index(
            "idx_organization_professionals_created_at",
            "created_at",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Organization reference (required - tenant isolation)
    organization_id: UUID = Field(
        foreign_key="organizations.id",
        nullable=False,
        description="Organization that owns this professional record",
    )

    # Relationships
    organization: "Organization" = Relationship(back_populates="professionals")
    qualifications: list["ProfessionalQualification"] = Relationship(
        back_populates="professional"
    )
    documents: list["ProfessionalDocument"] = Relationship(
        back_populates="professional"
    )
    professional_companies: list["ProfessionalCompany"] = Relationship(
        back_populates="professional"
    )
    bank_accounts: list["BankAccount"] = Relationship(back_populates="professional")
    # Note: contracts and screening_processes relationships are defined on ProfessionalContract and ScreeningProcess
    # to avoid circular import issues
