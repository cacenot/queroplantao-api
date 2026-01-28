"""Add pending document support for screening workflow.

Revision ID: 000000000007
Revises: 000000000006
Create Date: 2026-01-28 14:00:00.000000

Adds fields to professional_documents table to support the screening workflow:
- is_pending: Document awaiting screening approval
- source_type: How document was created (DIRECT or SCREENING)
- screening_id: FK to screening_processes (if from screening)
- promoted_at: When document was promoted from pending
- promoted_by: User who promoted the document
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000007"
down_revision: Union[str, Sequence[str], None] = "000000000006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the DocumentSourceType enum
    documentsourcetype = sa.Enum("DIRECT", "SCREENING", name="documentsourcetype")
    documentsourcetype.create(op.get_bind(), checkfirst=True)

    # Add new columns to professional_documents
    op.add_column(
        "professional_documents",
        sa.Column(
            "is_pending",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("FALSE"),
            comment="True if document is pending screening approval",
        ),
    )
    op.add_column(
        "professional_documents",
        sa.Column(
            "source_type",
            documentsourcetype,
            nullable=False,
            server_default=sa.text("'DIRECT'"),
            comment="How this document was created (DIRECT or SCREENING)",
        ),
    )
    op.add_column(
        "professional_documents",
        sa.Column(
            "screening_id",
            sa.UUID(),
            nullable=True,
            comment="Screening process that created this document",
        ),
    )
    op.add_column(
        "professional_documents",
        sa.Column(
            "promoted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="When document was promoted from pending",
        ),
    )
    op.add_column(
        "professional_documents",
        sa.Column(
            "promoted_by",
            sa.UUID(),
            nullable=True,
            comment="User who promoted the document from pending",
        ),
    )

    # Add FK constraint for screening_id
    op.create_foreign_key(
        "fk_professional_documents_screening_id",
        "professional_documents",
        "screening_processes",
        ["screening_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add index for pending documents lookup
    op.create_index(
        "idx_professional_documents_pending",
        "professional_documents",
        ["screening_id"],
        postgresql_where=sa.text("deleted_at IS NULL AND is_pending = TRUE"),
    )

    # Remove server defaults after populating existing rows
    op.alter_column("professional_documents", "is_pending", server_default=None)
    op.alter_column("professional_documents", "source_type", server_default=None)


def downgrade() -> None:
    # Drop the index
    op.drop_index(
        "idx_professional_documents_pending", table_name="professional_documents"
    )

    # Drop FK constraint
    op.drop_constraint(
        "fk_professional_documents_screening_id",
        "professional_documents",
        type_="foreignkey",
    )

    # Drop columns
    op.drop_column("professional_documents", "promoted_by")
    op.drop_column("professional_documents", "promoted_at")
    op.drop_column("professional_documents", "screening_id")
    op.drop_column("professional_documents", "source_type")
    op.drop_column("professional_documents", "is_pending")

    # Drop the enum
    sa.Enum(name="documentsourcetype").drop(op.get_bind(), checkfirst=True)
