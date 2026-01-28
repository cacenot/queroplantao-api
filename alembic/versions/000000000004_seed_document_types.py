"""Seed document_types table.

This migration seeds the document_types table with the default document types
that were previously defined in the DocumentType enum.

Revision ID: 000000000004
Revises: 000000000003
Create Date: 2026-01-27
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "000000000004"
down_revision: Union[str, Sequence[str], None] = "000000000003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed document types."""
    # Note: The actual table creation will be handled by autogenerate migration
    # This migration only seeds the data
    connection = op.get_bind()

    # Seed document types (global - organization_id = NULL)
    connection.execute(
        sa.text("""
        INSERT INTO document_types (
            id, code, name, category, description, help_text, validation_url,
            requires_expiration, default_validity_days, is_active, display_order,
            organization_id, created_at, updated_at
        ) VALUES
            -- Profile documents (PROFILE category)
            (gen_random_uuid(), 'ID_DOCUMENT', 'Documento de Identidade (RG ou CNH)', 'PROFILE',
             'Documento oficial com foto (RG ou CNH)', NULL, NULL,
             false, NULL, true, 10, NULL, now(), now()),
            (gen_random_uuid(), 'PHOTO', 'Foto 3x4', 'PROFILE',
             'Foto do profissional (3x4 ou similar)', NULL, NULL,
             false, NULL, true, 20, NULL, now(), now()),
            (gen_random_uuid(), 'CRIMINAL_RECORD', 'Certidão de Antecedentes Criminais', 'PROFILE',
             'Certidão de antecedentes criminais', NULL, NULL,
             true, 90, true, 30, NULL, now(), now()),
            (gen_random_uuid(), 'ADDRESS_PROOF', 'Comprovante de Endereço', 'PROFILE',
             'Comprovante de endereço atual', NULL, NULL,
             true, 90, true, 40, NULL, now(), now()),
            (gen_random_uuid(), 'CV', 'Currículo', 'PROFILE',
             'Currículo profissional', NULL, NULL,
             false, NULL, true, 50, NULL, now(), now()),
            -- Qualification documents (QUALIFICATION category)
            (gen_random_uuid(), 'DIPLOMA', 'Diploma de Graduação', 'QUALIFICATION',
             'Diploma de Medicina/Enfermagem/etc', NULL, NULL,
             false, NULL, true, 100, NULL, now(), now()),
            (gen_random_uuid(), 'CRM_REGISTRATION_CERTIFICATE', 'Certidão de Regularidade de Inscrição', 'QUALIFICATION',
             'Certidão de regularidade de inscrição no conselho',
             'Acesse o portal do conselho regional do seu estado e solicite a certidão de regularidade.',
             'https://portal.cfm.org.br',
             true, 30, true, 110, NULL, now(), now()),
            (gen_random_uuid(), 'CRM_FINANCIAL_CERTIFICATE', 'Certidão de Regularidade Financeira', 'QUALIFICATION',
             'Certidão de regularidade financeira do conselho', NULL, NULL,
             true, 30, true, 120, NULL, now(), now()),
            (gen_random_uuid(), 'CRM_ETHICS_CERTIFICATE', 'Certidão Ética', 'QUALIFICATION',
             'Certidão ética do conselho', NULL, NULL,
             true, 30, true, 130, NULL, now(), now()),
            -- Specialty documents (SPECIALTY category)
            (gen_random_uuid(), 'RESIDENCY_CERTIFICATE', 'Certificado de Conclusão de Residência', 'SPECIALTY',
             'Certificado de conclusão de residência médica', NULL, NULL,
             false, NULL, true, 200, NULL, now(), now()),
            (gen_random_uuid(), 'SPECIALIST_TITLE', 'Título de Especialista', 'SPECIALTY',
             'Título de especialista emitido pela sociedade', NULL, NULL,
             false, NULL, true, 210, NULL, now(), now()),
            (gen_random_uuid(), 'SBA_DIPLOMA', 'Diploma da SBA (Anestesiologia)', 'SPECIALTY',
             'Diploma da Sociedade Brasileira de Anestesiologia', NULL, NULL,
             false, NULL, true, 220, NULL, now(), now()),
            -- Generic
            (gen_random_uuid(), 'OTHER', 'Outro Documento', 'PROFILE',
             'Outros documentos não categorizados', NULL, NULL,
             false, NULL, true, 999, NULL, now(), now());
    """)
    )


def downgrade() -> None:
    """Remove seeded document types."""
    # Only remove global document types (organization_id IS NULL)
    op.execute(
        """
        DELETE FROM document_types
        WHERE organization_id IS NULL
        AND code IN (
            'ID_DOCUMENT', 'PHOTO', 'CRIMINAL_RECORD', 'ADDRESS_PROOF', 'CV',
            'DIPLOMA', 'CRM_REGISTRATION_CERTIFICATE', 'CRM_FINANCIAL_CERTIFICATE',
            'CRM_ETHICS_CERTIFICATE', 'RESIDENCY_CERTIFICATE', 'SPECIALIST_TITLE',
            'SBA_DIPLOMA', 'OTHER'
        );
        """
    )
