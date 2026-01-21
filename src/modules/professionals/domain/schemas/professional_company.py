"""Schemas for ProfessionalCompany."""

from typing import Optional
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


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
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
