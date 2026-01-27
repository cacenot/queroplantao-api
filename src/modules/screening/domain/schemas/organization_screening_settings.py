"""Schemas for OrganizationScreeningSettings."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrganizationScreeningSettingsCreate(BaseModel):
    """Schema for creating organization screening settings."""

    model_config = ConfigDict(from_attributes=True)

    requires_client_company: bool = Field(
        default=False,
        description="Whether screenings require a client company",
    )
    requires_client_validation_step: bool = Field(
        default=False,
        description="Whether client validation step is required",
    )
    auto_approve_existing_documents: bool = Field(
        default=False,
        description="Whether to auto-approve documents from previous screenings",
    )
    document_validity_check: bool = Field(
        default=True,
        description="Whether to check document expiration dates",
    )
    escalation_enabled: bool = Field(
        default=True,
        description="Whether escalation to supervisor is enabled",
    )
    auto_escalate_alerts: bool = Field(
        default=False,
        description="Whether to auto-escalate when documents have alerts",
    )
    token_expiry_hours: int = Field(
        default=72,
        ge=1,
        le=720,
        description="Hours until access token expires",
    )
    allow_professional_self_service: bool = Field(
        default=True,
        description="Whether professionals can access screening via token",
    )
    notify_on_submission: bool = Field(
        default=True,
        description="Notify assigned users when screening is submitted",
    )
    notify_on_expiration: bool = Field(
        default=True,
        description="Notify when screening is about to expire",
    )


class OrganizationScreeningSettingsUpdate(BaseModel):
    """Schema for updating organization screening settings (PATCH)."""

    model_config = ConfigDict(from_attributes=True)

    requires_client_company: Optional[bool] = None
    requires_client_validation_step: Optional[bool] = None
    auto_approve_existing_documents: Optional[bool] = None
    document_validity_check: Optional[bool] = None
    escalation_enabled: Optional[bool] = None
    auto_escalate_alerts: Optional[bool] = None
    token_expiry_hours: Optional[int] = Field(
        default=None,
        ge=1,
        le=720,
    )
    allow_professional_self_service: Optional[bool] = None
    notify_on_submission: Optional[bool] = None
    notify_on_expiration: Optional[bool] = None


class OrganizationScreeningSettingsResponse(BaseModel):
    """Schema for organization screening settings response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    requires_client_company: bool
    requires_client_validation_step: bool
    auto_approve_existing_documents: bool
    document_validity_check: bool
    escalation_enabled: bool
    auto_escalate_alerts: bool
    token_expiry_hours: int
    allow_professional_self_service: bool
    notify_on_submission: bool
    notify_on_expiration: bool
