"""Add document review counts.

Revision ID: 000000000008
Revises: 000000000007
Create Date: 2026-01-28 20:10:00.000000

Adds correction_needed_count and removes legacy rejected/alert counts.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "000000000008"
down_revision: Union[str, Sequence[str], None] = "000000000007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "screening_document_review_steps",
        sa.Column(
            "correction_needed_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="Documents needing correction (re-upload)",
        ),
    )
    op.execute(
        "ALTER TABLE screening_document_review_steps DROP COLUMN IF EXISTS rejected_count;"
    )
    op.execute(
        "ALTER TABLE screening_document_review_steps DROP COLUMN IF EXISTS alert_count;"
    )
    op.alter_column(
        "screening_document_review_steps",
        "correction_needed_count",
        server_default=None,
    )


def downgrade() -> None:
    op.add_column(
        "screening_document_review_steps",
        sa.Column(
            "rejected_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "screening_document_review_steps",
        sa.Column(
            "alert_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.drop_column("screening_document_review_steps", "correction_needed_count")
    op.alter_column(
        "screening_document_review_steps",
        "rejected_count",
        server_default=None,
    )
    op.alter_column(
        "screening_document_review_steps",
        "alert_count",
        server_default=None,
    )
