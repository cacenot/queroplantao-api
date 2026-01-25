"""Schemas for organization user (membership) management."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Role Info
# ============================================================================


class RoleInfo(BaseModel):
    """Role information."""

    id: UUID
    code: str
    name: str

    model_config = {"from_attributes": True}


# ============================================================================
# User Info (embedded in membership response)
# ============================================================================


class UserInfo(BaseModel):
    """User basic information."""

    id: UUID
    email: str
    full_name: str
    avatar_url: str | None = None
    is_active: bool = True

    model_config = {"from_attributes": True}


# ============================================================================
# Invite Schemas
# ============================================================================


class OrganizationUserInvite(BaseModel):
    """Schema for inviting a user to an organization."""

    email: EmailStr = Field(
        ...,
        description="Email address of the user to invite",
    )
    role_id: UUID = Field(
        ...,
        description="Role to assign to the user",
    )
    full_name: str | None = Field(
        default=None,
        max_length=255,
        description="Name of the invitee (optional, for new users)",
    )


class OrganizationUserAdd(BaseModel):
    """Schema for adding an existing user to an organization (without invitation)."""

    user_id: UUID = Field(
        ...,
        description="ID of the existing user to add",
    )
    role_id: UUID = Field(
        ...,
        description="Role to assign to the user",
    )


# ============================================================================
# Update Schema
# ============================================================================


class OrganizationUserUpdate(BaseModel):
    """Schema for updating a user's role in an organization."""

    role_id: UUID | None = Field(
        default=None,
        description="New role ID to assign",
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the membership is active",
    )


# ============================================================================
# Response Schemas
# ============================================================================


class OrganizationUserResponse(BaseModel):
    """Response schema for organization user (membership)."""

    id: UUID = Field(..., description="Membership ID")
    user: UserInfo = Field(..., description="User information")
    role: RoleInfo = Field(..., description="Assigned role")
    organization_id: UUID = Field(..., description="Organization ID")

    # Status
    is_active: bool = Field(..., description="Whether membership is active")
    is_pending: bool = Field(..., description="Whether invitation is pending")

    # Timestamps
    invited_at: datetime | None = Field(None, description="When invitation was sent")
    accepted_at: datetime | None = Field(
        None, description="When invitation was accepted"
    )
    granted_at: datetime = Field(..., description="When role was granted")
    expires_at: datetime | None = Field(None, description="When role expires")
    created_at: datetime = Field(..., description="Record creation timestamp")

    model_config = {"from_attributes": True}

    @classmethod
    def from_membership(cls, membership) -> "OrganizationUserResponse":
        """Create response from OrganizationMembership model."""
        return cls(
            id=membership.id,
            user=UserInfo.model_validate(membership.user),
            role=RoleInfo.model_validate(membership.role),
            organization_id=membership.organization_id,
            is_active=membership.is_active,
            is_pending=membership.is_pending,
            invited_at=membership.invited_at,
            accepted_at=membership.accepted_at,
            granted_at=membership.granted_at,
            expires_at=membership.expires_at,
            created_at=membership.created_at,
        )


class OrganizationUserListItem(BaseModel):
    """Simplified response for listing organization users."""

    id: UUID = Field(..., description="Membership ID")
    user_id: UUID = Field(..., description="User ID")
    full_name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email")
    avatar_url: str | None = Field(None, description="User's avatar URL")
    role_code: str = Field(..., description="Role code")
    role_name: str = Field(..., description="Role name")
    is_active: bool = Field(..., description="Whether membership is active")
    is_pending: bool = Field(..., description="Whether invitation is pending")
    created_at: datetime = Field(..., description="Membership creation timestamp")

    model_config = {"from_attributes": True}

    @classmethod
    def from_membership(cls, membership) -> "OrganizationUserListItem":
        """Create list item from OrganizationMembership model."""
        return cls(
            id=membership.id,
            user_id=membership.user_id,
            full_name=membership.user.full_name,
            email=membership.user.email,
            avatar_url=membership.user.avatar_url,
            role_code=membership.role.code,
            role_name=membership.role.name,
            is_active=membership.is_active,
            is_pending=membership.is_pending,
            created_at=membership.created_at,
        )


# ============================================================================
# Invitation Schemas
# ============================================================================


class InvitationAcceptRequest(BaseModel):
    """Request schema for accepting an invitation."""

    token: str = Field(
        ...,
        description="The invitation token from the email link",
    )


class InvitationAcceptResponse(BaseModel):
    """Response schema for accepting an invitation."""

    message: str = Field(..., description="Success message")
    organization_id: UUID = Field(..., description="Organization ID")
    organization_name: str = Field(..., description="Organization name")
    role_name: str = Field(..., description="Assigned role name")


class InvitationInfo(BaseModel):
    """Information about an invitation (for preview before accepting)."""

    email: str = Field(..., description="Invitee email")
    organization_name: str = Field(..., description="Organization name")
    role_name: str = Field(..., description="Role being assigned")
    inviter_name: str = Field(..., description="Name of person who sent invite")
    expires_at: datetime = Field(..., description="When invitation expires")
    is_expired: bool = Field(..., description="Whether invitation has expired")
