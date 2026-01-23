"""User model."""

from typing import TYPE_CHECKING, Optional

from pydantic import AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    AwareDatetimeField,
    BaseModel,
    CPFField,
    PhoneField,
    PrimaryKeyMixin,
    TimestampMixin,
    TrackingMixin,
)

if TYPE_CHECKING:
    from src.modules.auth.domain.models.user_permission import UserPermission
    from src.modules.auth.domain.models.user_role import UserRole


class UserBase(BaseModel):
    """Base fields for User."""

    firebase_uid: str = Field(
        max_length=128,
        description="Firebase Auth UID",
    )
    email: str = Field(
        max_length=255,
        description="User email address",
    )
    full_name: str = Field(
        max_length=255,
        description="User's full name",
    )
    phone: Optional[str] = PhoneField(
        default=None,
        nullable=True,
        description="Phone number (E.164 format)",
    )
    cpf: Optional[str] = CPFField(
        default=None,
        nullable=True,
        description="Brazilian CPF number (11 digits, unique)",
    )
    avatar_url: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Profile picture URL",
    )
    is_active: bool = Field(
        default=True,
        description="Whether user account is active",
    )
    email_verified_at: Optional[AwareDatetime] = AwareDatetimeField(
        default=None,
        nullable=True,
        description="Email verification timestamp (UTC)",
    )


class User(UserBase, PrimaryKeyMixin, TimestampMixin, TrackingMixin, table=True):
    """
    User table model.

    Stores user account data complementary to Firebase Auth.
    Firebase handles authentication; this table handles authorization and profile data.
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("firebase_uid", name="uq_users_firebase_uid"),
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("cpf", name="uq_users_cpf"),
    )

    # Relationships
    roles: list["UserRole"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserRole.user_id"},
    )
    permissions: list["UserPermission"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "UserPermission.user_id"},
    )
