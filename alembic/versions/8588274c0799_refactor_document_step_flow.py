"""Refactor document step flow.

This migration:
1. Renames DOCUMENTS to DOCUMENT_UPLOAD in step_type enum
2. Adds required_document_status enum
3. Adds status column to screening_required_documents
4. Adds review_notes JSONB column to screening_required_documents
5. Removes old notes column (migrating data to review_notes)

Revision ID: 8588274c0799
Revises: 6283b21dcda5
Create Date: 2026-01-27 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "8588274c0799"
down_revision: Union[str, None] = "6283b21dcda5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply document step flow refactoring."""
    # 1. Rename DOCUMENTS to DOCUMENT_UPLOAD in step_type enum
    # PostgreSQL requires renaming enum values with ALTER TYPE
    op.execute("ALTER TYPE step_type RENAME VALUE 'DOCUMENTS' TO 'DOCUMENT_UPLOAD'")

    # 2. Create required_document_status enum
    required_document_status_enum = postgresql.ENUM(
        "PENDING_UPLOAD",
        "UPLOADED",
        "APPROVED",
        "REJECTED",
        "CORRECTION_NEEDED",
        name="required_document_status",
        create_type=True,
    )
    required_document_status_enum.create(op.get_bind(), checkfirst=True)

    # 3. Add status column to screening_required_documents
    op.add_column(
        "screening_required_documents",
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING_UPLOAD",
                "UPLOADED",
                "APPROVED",
                "REJECTED",
                "CORRECTION_NEEDED",
                name="required_document_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING_UPLOAD",
        ),
    )

    # 4. Add review_notes JSONB column
    op.add_column(
        "screening_required_documents",
        sa.Column(
            "review_notes",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
    )

    # 5. Migrate existing notes to review_notes if notes column exists
    # Check if notes column exists and migrate data
    op.execute(
        """
        UPDATE screening_required_documents
        SET review_notes = CASE
            WHEN notes IS NOT NULL AND notes != ''
            THEN jsonb_build_array(jsonb_build_object(
                'text', notes,
                'created_at', created_at::text,
                'action', 'INITIAL_NOTE'
            ))
            ELSE '[]'::jsonb
        END
        """
    )

    # 6. Update status based on is_uploaded flag
    op.execute(
        """
        UPDATE screening_required_documents
        SET status = CASE
            WHEN is_uploaded = true THEN 'UPLOADED'
            ELSE 'PENDING_UPLOAD'
        END::required_document_status
        """
    )

    # 7. Drop old notes column
    op.drop_column("screening_required_documents", "notes")

    # 8. Remove server default from status and review_notes (not needed after migration)
    op.alter_column("screening_required_documents", "status", server_default=None)
    op.alter_column("screening_required_documents", "review_notes", server_default=None)


def downgrade() -> None:
    """Revert document step flow refactoring."""
    # 1. Add back notes column
    op.add_column(
        "screening_required_documents",
        sa.Column("notes", sa.VARCHAR(length=2000), nullable=True),
    )

    # 2. Migrate review_notes back to notes (take first note if exists)
    op.execute(
        """
        UPDATE screening_required_documents
        SET notes = (review_notes->0->>'text')
        WHERE jsonb_array_length(review_notes) > 0
        """
    )

    # 3. Drop review_notes column
    op.drop_column("screening_required_documents", "review_notes")

    # 4. Drop status column
    op.drop_column("screening_required_documents", "status")

    # 5. Drop required_document_status enum
    op.execute("DROP TYPE IF EXISTS required_document_status")

    # 6. Rename DOCUMENT_UPLOAD back to DOCUMENTS
    op.execute("ALTER TYPE step_type RENAME VALUE 'DOCUMENT_UPLOAD' TO 'DOCUMENTS'")
