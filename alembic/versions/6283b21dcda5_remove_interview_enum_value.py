"""remove_interview_enum_value

Revision ID: 6283b21dcda5
Revises: 4ab2c4a709ae
Create Date: 2026-01-26 10:18:27.020326

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6283b21dcda5"
down_revision: Union[str, Sequence[str], None] = "4ab2c4a709ae"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove INTERVIEW steps and enum value."""
    # 1. Delete any existing INTERVIEW steps
    op.execute("DELETE FROM screening_process_steps WHERE step_type = 'INTERVIEW'")

    # 2. Update any screening_processes with current_step_type = INTERVIEW to NULL
    op.execute(
        "UPDATE screening_processes SET current_step_type = NULL WHERE current_step_type = 'INTERVIEW'"
    )

    # 3. Create new enum type without INTERVIEW
    op.execute("""
        CREATE TYPE step_type_new AS ENUM (
            'CONVERSATION',
            'PROFESSIONAL_DATA',
            'QUALIFICATION',
            'SPECIALTY',
            'EDUCATION',
            'DOCUMENTS',
            'COMPANY',
            'BANK_ACCOUNT',
            'DOCUMENT_REVIEW',
            'SUPERVISOR_REVIEW',
            'CLIENT_VALIDATION'
        )
    """)

    # 4. Alter both columns to use new enum type
    op.execute("""
        ALTER TABLE screening_process_steps
        ALTER COLUMN step_type TYPE step_type_new
        USING step_type::text::step_type_new
    """)

    op.execute("""
        ALTER TABLE screening_processes
        ALTER COLUMN current_step_type TYPE step_type_new
        USING current_step_type::text::step_type_new
    """)

    # 5. Drop old enum type and rename new one
    op.execute("DROP TYPE step_type")
    op.execute("ALTER TYPE step_type_new RENAME TO step_type")


def downgrade() -> None:
    """Re-add INTERVIEW enum value."""
    # 1. Create old enum type with INTERVIEW
    op.execute("""
        CREATE TYPE step_type_old AS ENUM (
            'CONVERSATION',
            'PROFESSIONAL_DATA',
            'QUALIFICATION',
            'SPECIALTY',
            'EDUCATION',
            'DOCUMENTS',
            'COMPANY',
            'BANK_ACCOUNT',
            'DOCUMENT_REVIEW',
            'SUPERVISOR_REVIEW',
            'INTERVIEW',
            'CLIENT_VALIDATION'
        )
    """)

    # 2. Alter both columns to use old enum type
    op.execute("""
        ALTER TABLE screening_process_steps
        ALTER COLUMN step_type TYPE step_type_old
        USING step_type::text::step_type_old
    """)

    op.execute("""
        ALTER TABLE screening_processes
        ALTER COLUMN current_step_type TYPE step_type_old
        USING current_step_type::text::step_type_old
    """)

    # 3. Drop new enum type and rename old one
    op.execute("DROP TYPE step_type")
    op.execute("ALTER TYPE step_type_old RENAME TO step_type")
