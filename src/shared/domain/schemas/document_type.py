"""Schemas for DocumentType."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.shared.domain.models import DocumentCategory


class DocumentTypeCreate(BaseModel):
    """Schema for creating a document type configuration."""

    model_config = ConfigDict(from_attributes=True)

    name: str = Field(
        max_length=255,
        description="Display name in Portuguese",
    )
    category: DocumentCategory = Field(
        description="Document category (PROFILE, QUALIFICATION, SPECIALTY)",
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Brief description of this document",
    )
    help_text: Optional[str] = Field(
        default=None,
        description="Detailed help text on how to obtain this document",
    )
    validation_instructions: Optional[str] = Field(
        default=None,
        description="Instructions for reviewers on how to validate",
    )
    validation_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="URL where this document can be validated",
    )
    requires_expiration: bool = Field(
        default=False,
        description="Whether this document type has an expiration date",
    )
    default_validity_days: Optional[int] = Field(
        default=None,
        ge=1,
        description="Default validity period in days",
    )
    required_for_professional_types: Optional[list[str]] = Field(
        default=None,
        description="List of ProfessionalType values this doc is required for",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Order for displaying in lists",
    )


class DocumentTypeUpdate(BaseModel):
    """Schema for updating a document type configuration (PATCH)."""

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    help_text: Optional[str] = None
    validation_instructions: Optional[str] = None
    validation_url: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    requires_expiration: Optional[bool] = None
    default_validity_days: Optional[int] = Field(
        default=None,
        ge=1,
    )
    required_for_professional_types: Optional[list[str]] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(
        default=None,
        ge=0,
    )


class DocumentTypeResponse(BaseModel):
    """Schema for document type configuration response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: DocumentCategory
    description: Optional[str]
    help_text: Optional[str]
    validation_instructions: Optional[str]
    validation_url: Optional[str]
    requires_expiration: bool
    default_validity_days: Optional[int]
    required_for_professional_types: Optional[list[str]]
    is_active: bool
    display_order: int
    organization_id: UUID
    created_at: datetime
    updated_at: Optional[datetime]


class DocumentTypeListResponse(BaseModel):
    """Schema for document type list with minimal fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    category: DocumentCategory
    requires_expiration: bool
    is_active: bool
    display_order: int
