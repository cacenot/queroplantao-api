"""Schemas for ProfessionalCompany."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from src.shared.domain.schemas.bank_account import BankAccountResponse


class ProfessionalCompanyCreate(BaseModel):
    """Schema for creating a professional-company link."""

    model_config = ConfigDict(from_attributes=True)

    company_id: UUID = Field(
        description="The company UUID",
    )
    joined_at: AwareDatetime = Field(
        description="Timestamp when professional joined the company",
    )
    left_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Timestamp when professional left the company",
    )


class ProfessionalCompanyUpdate(BaseModel):
    """Schema for updating a professional-company link (PATCH - partial update)."""

    model_config = ConfigDict(from_attributes=True)

    joined_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Timestamp when professional joined the company",
    )
    left_at: Optional[AwareDatetime] = Field(
        default=None,
        description="Timestamp when professional left the company",
    )


class CompanyInfo(BaseModel):
    """Embedded company information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cnpj: Optional[str] = None
    legal_name: str
    trade_name: Optional[str] = None


class CompanyDetailInfo(BaseModel):
    """Detailed company information with bank accounts."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cnpj: Optional[str] = None
    legal_name: str
    trade_name: Optional[str] = None

    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None

    # Address
    street: Optional[str] = None
    street_number: Optional[str] = None
    complement: Optional[str] = None
    neighborhood: Optional[str] = None
    city: Optional[str] = None
    state_code: Optional[str] = None
    state_name: Optional[str] = None
    postal_code: Optional[str] = None

    # Nested bank accounts
    bank_accounts: list["BankAccountResponse"] = []


class ProfessionalCompanyResponse(BaseModel):
    """Schema for professional-company link response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_professional_id: UUID
    company_id: UUID
    joined_at: str
    left_at: Optional[str] = None

    # Embedded company info
    company: Optional[CompanyInfo] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfessionalCompanyDetailResponse(BaseModel):
    """Schema for professional-company link with full company details."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_professional_id: UUID
    company_id: UUID
    joined_at: str
    left_at: Optional[str] = None

    # Embedded company info with bank accounts
    company: Optional[CompanyDetailInfo] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Deferred import to avoid circular imports
from src.shared.domain.schemas.bank_account import BankAccountResponse  # noqa: E402

CompanyDetailInfo.model_rebuild()
ProfessionalCompanyDetailResponse.model_rebuild()
