"""make_document_type_org_required_and_remove_code

Revision ID: 000000000014
Revises: 000000000013
Create Date: 2026-02-02 14:00:00.000000

This migration:
1. Makes organization_id NOT NULL on document_types table
2. Removes the 'code' column (no longer needed with org-scoped types)
3. Removes the partial unique index for global types (ix_document_types_code_global_active)
4. Removes the composite unique constraint for code+org (uq_document_types_code_org)

Note: Before running this migration, ensure all existing document_types
have a valid organization_id. Global types (org_id=NULL) must be either
deleted or assigned to an organization.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000014"
down_revision: Union[str, Sequence[str], None] = "000000000013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make organization_id required and remove code column."""
    # Drop the partial unique index for global types
    # This index was: UNIQUE(code) WHERE deleted_at IS NULL AND organization_id IS NULL
    op.drop_index(
        "ix_document_types_code_global_active",
        table_name="document_types",
        if_exists=True,
    )

    # Drop the unique constraint for code+org
    op.drop_constraint(
        "uq_document_types_code_org",
        table_name="document_types",
        type_="unique",
    )

    # Remove the code column
    op.drop_column("document_types", "code")

    # Make organization_id NOT NULL
    op.alter_column(
        "document_types",
        "organization_id",
        existing_type=sa.Uuid(),
        nullable=False,
    )


def downgrade() -> None:
    """Revert organization_id to nullable and restore code column."""
    # Make organization_id nullable again
    op.alter_column(
        "document_types",
        "organization_id",
        existing_type=sa.Uuid(),
        nullable=True,
    )

    # Restore the code column
    op.add_column(
        "document_types",
        sa.Column("code", sa.String(50), nullable=True),
    )

    # Recreate the unique constraint for code+org
    op.create_unique_constraint(
        "uq_document_types_code_org",
        "document_types",
        ["code", "organization_id"],
    )

    # Recreate the partial unique index for global types
    op.create_index(
        "ix_document_types_code_global_active",
        "document_types",
        ["code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND organization_id IS NULL"),
    )
