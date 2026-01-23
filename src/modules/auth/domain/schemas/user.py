"""User schemas for auth module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.shared.domain.value_objects import CPF, Phone


class RoleInfo(BaseModel):
    """Simplified role info for responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str


class PermissionInfo(BaseModel):
    """Simplified permission info for responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    module: str


class ParentOrganizationInfo(BaseModel):
    """Parent organization info."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class OrganizationMembershipInfo(BaseModel):
    """Organization membership info for user response.

    Roles are grouped by organization - a user can have multiple roles
    in the same organization.
    """

    model_config = ConfigDict(from_attributes=True)

    organization_id: UUID
    organization_name: str
    is_active: bool

    # Multiple roles per organization
    roles: list[RoleInfo] = []

    # Parent organization (if this is a child org)
    parent: Optional[ParentOrganizationInfo] = None


class UserMeResponse(BaseModel):
    """Response schema for GET /auth/me endpoint."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str
    phone: Optional[str] = None
    cpf: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    email_verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    # Global roles
    roles: list[RoleInfo] = []

    # Direct permissions (not from roles)
    permissions: list[PermissionInfo] = []

    # Organization memberships (roles grouped by organization)
    organizations: list[OrganizationMembershipInfo] = []


class UserMeUpdate(BaseModel):
    """Schema for updating current user's profile (PATCH - partial update).

    Email is not editable through this endpoint as it requires Firebase sync.
    """

    model_config = ConfigDict(from_attributes=True)

    full_name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[Phone] = Field(default=None)
    cpf: Optional[CPF] = Field(default=None)
    avatar_url: Optional[HttpUrl] = Field(default=None)
