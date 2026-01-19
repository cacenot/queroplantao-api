"""ProfessionalProfile model."""

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.modules.professionals.domain.models.enums import Gender, MaritalStatus
from src.shared.domain.models import (
    AddressMixin,
    AwareDatetimeField,
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
    from src.modules.auth.domain.models import User
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


class ProfessionalProfileBase(BaseModel):
    """Base fields for ProfessionalProfile."""

    # Personal data (required even without user account)
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

    # Status timestamps
    profile_completed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Timestamp when profile was completed (UTC)",
    )
    claimed_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Timestamp when professional claimed pre-registered profile (UTC)",
    )


class ProfessionalProfile(
    ProfessionalProfileBase,
    AddressMixin,
    VerificationMixin,
    TrackingMixin,
    PrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
    table=True,
):
    """
    ProfessionalProfile table model.

    Stores healthcare professional data. Can exist without a user account
    (pre-registration by scale managers). When the professional creates
    an account, the system links it via email or CPF.
    """

    __tablename__ = "professional_profiles"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_professional_profiles_user_id"),
        UniqueConstraint("cpf", name="uq_professional_profiles_cpf"),
    )

    # User link (nullable for pre-registration)
    user_id: Optional[UUID] = Field(
        default=None,
        foreign_key="users.id",
        nullable=True,
        description="User ID (null for pre-registered profiles)",
    )

    # Relationships
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[ProfessionalProfile.user_id]",
            "lazy": "selectin",
        }
    )
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
