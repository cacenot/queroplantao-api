"""Specialty model."""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, text
from sqlmodel import Field, Relationship

from src.shared.domain.models import (
    BaseModel,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
)

if TYPE_CHECKING:
    from src.modules.professionals.domain.models.professional_specialty import (
        ProfessionalSpecialty,
    )


class SpecialtyBase(BaseModel):
    """Base fields for Specialty.

    Specialties are medical specialties recognized by CFM (Conselho Federal de Medicina).
    All specialties require residency and are specific to doctors.
    """

    code: str = Field(
        max_length=50,
        description="Specialty code (e.g., 'CARDIOLOGIA', 'ANESTESIOLOGIA')",
    )
    name: str = Field(
        max_length=150,
        description="Specialty name in Portuguese",
    )
    description: Optional[str] = Field(
        default=None,
        description="Specialty description",
    )


class Specialty(
    SpecialtyBase, PrimaryKeyMixin, TimestampMixin, SoftDeleteMixin, table=True
):
    """
    Specialty table model.

    Defines medical specialties recognized by CFM (Conselho Federal de Medicina).
    This is a global reference table - all specialties require residency and are
    specific to doctors (physicians).

    Note: This is a global entity, not tenant-scoped. Organizations can only
    read specialties, not create or modify them.
    """

    __tablename__ = "specialties"
    __table_args__ = (
        # Unique code when not soft-deleted
        Index(
            "uq_specialties_code",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # GIN trigram index for search (code + name)
        Index(
            "idx_specialties_search_trgm",
            text(
                "(COALESCE(lower(code), '') || ' ' || "
                "COALESCE(f_unaccent(lower(name)), ''))"
            ),
            postgresql_using="gin",
            postgresql_ops={"": "gin_trgm_ops"},
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # B-tree index for name sorting
        Index(
            "idx_specialties_name",
            "name",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    # Relationships
    professionals: list["ProfessionalSpecialty"] = Relationship(
        back_populates="specialty"
    )
