"""add compliance_report_url to screening_processes

Revision ID: 000000000016
Revises: 000000000015
Create Date: 2026-02-03 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "000000000016"
down_revision: str | Sequence[str] | None = "000000000015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "screening_processes",
        sa.Column(
            "compliance_report_url",
            sa.String(length=2048),
            nullable=True,
            comment="URL of the generated compliance report PDF in storage",
        ),
    )


def downgrade() -> None:
    op.drop_column("screening_processes", "compliance_report_url")
