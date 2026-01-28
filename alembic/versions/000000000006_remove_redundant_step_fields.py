"""remove_redundant_step_fields

Revision ID: 000000000006
Revises: 000000000005
Create Date: 2026-01-28 14:00:00.000000

This migration removes redundant array fields from screening_professional_data_steps:
- qualification_ids: redundant, can be queried via professional_id relationship
- specialty_ids: redundant, can be queried via qualification.specialties
- education_ids: redundant, can be queried via qualification.educations

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "000000000006"
down_revision: Union[str, Sequence[str], None] = "000000000005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove redundant array columns from screening_professional_data_steps."""
    op.drop_column("screening_professional_data_steps", "qualification_ids")
    op.drop_column("screening_professional_data_steps", "specialty_ids")
    op.drop_column("screening_professional_data_steps", "education_ids")


def downgrade() -> None:
    """Re-add the array columns (data will be lost)."""
    op.add_column(
        "screening_professional_data_steps",
        sa.Column(
            "education_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=True,
            server_default="{}",
        ),
    )
    op.add_column(
        "screening_professional_data_steps",
        sa.Column(
            "specialty_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=True,
            server_default="{}",
        ),
    )
    op.add_column(
        "screening_professional_data_steps",
        sa.Column(
            "qualification_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=True,
            server_default="{}",
        ),
    )
