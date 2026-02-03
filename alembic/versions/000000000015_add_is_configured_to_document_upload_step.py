"""add is_configured to document_upload_step

Revision ID: 000000000015
Revises: 000000000014
Create Date: 2026-02-02 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000015"
down_revision: str | Sequence[str] | None = "000000000014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "screening_document_upload_steps",
        sa.Column(
            "is_configured",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("screening_document_upload_steps", "is_configured")
