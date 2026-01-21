"""refactor professionals module

Revision ID: a1b2c3d4e5f6
Revises: e1b35e775ed8
Create Date: 2026-01-21 10:00:00.000000

This migration:
1. Refactors the specialties table:
   - Removes: is_active, requires_residency, is_generalist, professional_type
   - Adds: deleted_at for soft delete
   - Changes unique constraint to partial index
   - Increases code/name field lengths
2. Adds deleted_at to all professional-related tables for soft delete
3. Adds organization_id to professional_qualifications for unique constraint
4. Seeds all 54 CFM medical specialties
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e1b35e775ed8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # =========================================================================
    # 1. REFACTOR SPECIALTIES TABLE
    # =========================================================================

    # Drop old unique constraint
    op.drop_constraint("uq_specialties_code", "specialties", type_="unique")

    # Remove unnecessary columns
    op.drop_column("specialties", "is_active")
    op.drop_column("specialties", "requires_residency")
    op.drop_column("specialties", "is_generalist")
    op.drop_column("specialties", "professional_type")

    # Add soft delete column
    op.add_column(
        "specialties",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Alter code and name column lengths
    op.alter_column(
        "specialties",
        "code",
        type_=sa.String(length=50),
        existing_type=sa.String(length=20),
        existing_nullable=False,
    )
    op.alter_column(
        "specialties",
        "name",
        type_=sa.String(length=150),
        existing_type=sa.String(length=100),
        existing_nullable=False,
    )

    # Create new partial unique index
    op.create_index(
        "uq_specialties_code",
        "specialties",
        ["code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # =========================================================================
    # 2. ADD SOFT DELETE TO PROFESSIONAL TABLES
    # =========================================================================

    # Add deleted_at to professional_qualifications
    op.add_column(
        "professional_qualifications",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add deleted_at to professional_specialties
    op.add_column(
        "professional_specialties",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add deleted_at to professional_educations
    op.add_column(
        "professional_educations",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add deleted_at to professional_documents
    op.add_column(
        "professional_documents",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add deleted_at to professional_companies
    op.add_column(
        "professional_companies",
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # =========================================================================
    # 3. ADD ORGANIZATION_ID TO PROFESSIONAL_QUALIFICATIONS
    # =========================================================================

    # Add organization_id column
    op.add_column(
        "professional_qualifications",
        sa.Column("organization_id", sa.Uuid(), nullable=True),
    )

    # Populate organization_id from organization_professionals
    op.execute("""
        UPDATE professional_qualifications pq
        SET organization_id = op.organization_id
        FROM organization_professionals op
        WHERE pq.organization_professional_id = op.id
    """)

    # Make organization_id NOT NULL after population
    op.alter_column(
        "professional_qualifications",
        "organization_id",
        nullable=False,
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_professional_qualifications_organization_id",
        "professional_qualifications",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    # Create unique partial index for council registration per organization
    op.create_index(
        "uq_professional_qualifications_council_org",
        "professional_qualifications",
        ["organization_id", "council_number", "council_state"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # =========================================================================
    # 4. SEED MEDICAL SPECIALTIES (CFM - Conselho Federal de Medicina)
    # =========================================================================

    op.execute("""
        INSERT INTO specialties (id, code, name, description, created_at, updated_at)
        VALUES
            -- Specialties recognized by CFM (Conselho Federal de Medicina)
            (gen_random_uuid(), 'ACUPUNTURA', 'Acupuntura', 'Tratamento através de inserção de agulhas em pontos específicos do corpo', now(), now()),
            (gen_random_uuid(), 'ALERGIA_IMUNOLOGIA', 'Alergia e Imunologia', 'Diagnóstico e tratamento de doenças alérgicas e imunológicas', now(), now()),
            (gen_random_uuid(), 'ANESTESIOLOGIA', 'Anestesiologia', 'Administração de anestesia para procedimentos cirúrgicos e controle da dor', now(), now()),
            (gen_random_uuid(), 'ANGIOLOGIA', 'Angiologia', 'Tratamento clínico de doenças vasculares', now(), now()),
            (gen_random_uuid(), 'CARDIOLOGIA', 'Cardiologia', 'Diagnóstico e tratamento de doenças do coração', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_CARDIOVASCULAR', 'Cirurgia Cardiovascular', 'Cirurgias do coração e grandes vasos', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_MAO', 'Cirurgia da Mão', 'Cirurgias especializadas na mão e punho', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_CABECA_PESCOCO', 'Cirurgia de Cabeça e Pescoço', 'Cirurgias oncológicas da região da cabeça e pescoço', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_APARELHO_DIGESTIVO', 'Cirurgia do Aparelho Digestivo', 'Cirurgias do sistema digestivo', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_GERAL', 'Cirurgia Geral', 'Procedimentos cirúrgicos gerais', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_ONCOLOGICA', 'Cirurgia Oncológica', 'Cirurgias para tratamento de tumores', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_PEDIATRICA', 'Cirurgia Pediátrica', 'Cirurgias em pacientes pediátricos', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_PLASTICA', 'Cirurgia Plástica', 'Cirurgias reconstrutivas e estéticas', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_TORACICA', 'Cirurgia Torácica', 'Cirurgias do tórax, pulmões e mediastino', now(), now()),
            (gen_random_uuid(), 'CIRURGIA_VASCULAR', 'Cirurgia Vascular', 'Cirurgias dos vasos sanguíneos', now(), now()),
            (gen_random_uuid(), 'CLINICA_MEDICA', 'Clínica Médica', 'Medicina Interna - diagnóstico e tratamento clínico de adultos', now(), now()),
            (gen_random_uuid(), 'COLOPROCTOLOGIA', 'Coloproctologia', 'Diagnóstico e tratamento de doenças do intestino grosso, reto e ânus', now(), now()),
            (gen_random_uuid(), 'DERMATOLOGIA', 'Dermatologia', 'Diagnóstico e tratamento de doenças da pele', now(), now()),
            (gen_random_uuid(), 'ENDOCRINOLOGIA_METABOLOGIA', 'Endocrinologia e Metabologia', 'Tratamento de distúrbios hormonais e metabólicos', now(), now()),
            (gen_random_uuid(), 'ENDOSCOPIA', 'Endoscopia', 'Procedimentos diagnósticos e terapêuticos por endoscopia', now(), now()),
            (gen_random_uuid(), 'GASTROENTEROLOGIA', 'Gastroenterologia', 'Diagnóstico e tratamento de doenças do sistema digestivo', now(), now()),
            (gen_random_uuid(), 'GENETICA_MEDICA', 'Genética Médica', 'Diagnóstico e aconselhamento de doenças genéticas', now(), now()),
            (gen_random_uuid(), 'GERIATRIA', 'Geriatria', 'Cuidados médicos para idosos', now(), now()),
            (gen_random_uuid(), 'GINECOLOGIA_OBSTETRICIA', 'Ginecologia e Obstetrícia', 'Saúde da mulher e acompanhamento gestacional', now(), now()),
            (gen_random_uuid(), 'HEMATOLOGIA_HEMOTERAPIA', 'Hematologia e Hemoterapia', 'Tratamento de doenças do sangue e transfusões', now(), now()),
            (gen_random_uuid(), 'HOMEOPATIA', 'Homeopatia', 'Tratamento através de medicamentos homeopáticos', now(), now()),
            (gen_random_uuid(), 'INFECTOLOGIA', 'Infectologia', 'Tratamento de doenças infecciosas', now(), now()),
            (gen_random_uuid(), 'MASTOLOGIA', 'Mastologia', 'Diagnóstico e tratamento de doenças da mama', now(), now()),
            (gen_random_uuid(), 'MEDICINA_EMERGENCIA', 'Medicina de Emergência', 'Atendimento de emergências e urgências médicas', now(), now()),
            (gen_random_uuid(), 'MEDICINA_FAMILIA_COMUNIDADE', 'Medicina de Família e Comunidade', 'Atenção primária à saúde', now(), now()),
            (gen_random_uuid(), 'MEDICINA_ESPORTIVA', 'Medicina Esportiva', 'Cuidados médicos para atletas e praticantes de esportes', now(), now()),
            (gen_random_uuid(), 'MEDICINA_FISICA_REABILITACAO', 'Medicina Física e Reabilitação', 'Reabilitação de pacientes com deficiências', now(), now()),
            (gen_random_uuid(), 'MEDICINA_INTENSIVA', 'Medicina Intensiva', 'Cuidados em unidades de terapia intensiva', now(), now()),
            (gen_random_uuid(), 'MEDICINA_LEGAL_PERICIA', 'Medicina Legal e Perícia Médica', 'Perícias médicas e medicina forense', now(), now()),
            (gen_random_uuid(), 'MEDICINA_NUCLEAR', 'Medicina Nuclear', 'Diagnóstico e tratamento com radiofármacos', now(), now()),
            (gen_random_uuid(), 'MEDICINA_PREVENTIVA_SOCIAL', 'Medicina Preventiva e Social', 'Saúde pública e medicina preventiva', now(), now()),
            (gen_random_uuid(), 'MEDICINA_TRABALHO', 'Medicina do Trabalho', 'Saúde ocupacional', now(), now()),
            (gen_random_uuid(), 'MEDICINA_TRAFEGO', 'Medicina de Tráfego', 'Avaliação médica para habilitação e transporte', now(), now()),
            (gen_random_uuid(), 'NEFROLOGIA', 'Nefrologia', 'Diagnóstico e tratamento de doenças renais', now(), now()),
            (gen_random_uuid(), 'NEUROCIRURGIA', 'Neurocirurgia', 'Cirurgias do sistema nervoso', now(), now()),
            (gen_random_uuid(), 'NEUROLOGIA', 'Neurologia', 'Diagnóstico e tratamento de doenças neurológicas', now(), now()),
            (gen_random_uuid(), 'NUTROLOGIA', 'Nutrologia', 'Tratamento de distúrbios nutricionais', now(), now()),
            (gen_random_uuid(), 'OFTALMOLOGIA', 'Oftalmologia', 'Diagnóstico e tratamento de doenças dos olhos', now(), now()),
            (gen_random_uuid(), 'ORTOPEDIA_TRAUMATOLOGIA', 'Ortopedia e Traumatologia', 'Tratamento de doenças e lesões do sistema musculoesquelético', now(), now()),
            (gen_random_uuid(), 'OTORRINOLARINGOLOGIA', 'Otorrinolaringologia', 'Tratamento de doenças do ouvido, nariz e garganta', now(), now()),
            (gen_random_uuid(), 'PATOLOGIA', 'Patologia', 'Análise laboratorial de tecidos e células', now(), now()),
            (gen_random_uuid(), 'PATOLOGIA_CLINICA', 'Patologia Clínica/Medicina Laboratorial', 'Diagnóstico laboratorial de doenças', now(), now()),
            (gen_random_uuid(), 'PEDIATRIA', 'Pediatria', 'Cuidados médicos para crianças e adolescentes', now(), now()),
            (gen_random_uuid(), 'PNEUMOLOGIA', 'Pneumologia', 'Diagnóstico e tratamento de doenças respiratórias', now(), now()),
            (gen_random_uuid(), 'PSIQUIATRIA', 'Psiquiatria', 'Tratamento de transtornos mentais', now(), now()),
            (gen_random_uuid(), 'RADIOLOGIA_DIAGNOSTICO_IMAGEM', 'Radiologia e Diagnóstico por Imagem', 'Diagnóstico através de exames de imagem', now(), now()),
            (gen_random_uuid(), 'RADIOTERAPIA', 'Radioterapia', 'Tratamento de câncer com radiação', now(), now()),
            (gen_random_uuid(), 'REUMATOLOGIA', 'Reumatologia', 'Tratamento de doenças reumáticas e autoimunes', now(), now()),
            (gen_random_uuid(), 'UROLOGIA', 'Urologia', 'Tratamento de doenças do sistema urinário e reprodutor masculino', now(), now())
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # =========================================================================
    # 1. REMOVE SEEDED SPECIALTIES
    # =========================================================================

    op.execute("""
        DELETE FROM specialties WHERE code IN (
            'ACUPUNTURA', 'ALERGIA_IMUNOLOGIA', 'ANESTESIOLOGIA', 'ANGIOLOGIA',
            'CARDIOLOGIA', 'CIRURGIA_CARDIOVASCULAR', 'CIRURGIA_MAO',
            'CIRURGIA_CABECA_PESCOCO', 'CIRURGIA_APARELHO_DIGESTIVO',
            'CIRURGIA_GERAL', 'CIRURGIA_ONCOLOGICA', 'CIRURGIA_PEDIATRICA',
            'CIRURGIA_PLASTICA', 'CIRURGIA_TORACICA', 'CIRURGIA_VASCULAR',
            'CLINICA_MEDICA', 'COLOPROCTOLOGIA', 'DERMATOLOGIA',
            'ENDOCRINOLOGIA_METABOLOGIA', 'ENDOSCOPIA', 'GASTROENTEROLOGIA',
            'GENETICA_MEDICA', 'GERIATRIA', 'GINECOLOGIA_OBSTETRICIA',
            'HEMATOLOGIA_HEMOTERAPIA', 'HOMEOPATIA', 'INFECTOLOGIA',
            'MASTOLOGIA', 'MEDICINA_EMERGENCIA', 'MEDICINA_FAMILIA_COMUNIDADE',
            'MEDICINA_ESPORTIVA', 'MEDICINA_FISICA_REABILITACAO',
            'MEDICINA_INTENSIVA', 'MEDICINA_LEGAL_PERICIA', 'MEDICINA_NUCLEAR',
            'MEDICINA_PREVENTIVA_SOCIAL', 'MEDICINA_TRABALHO', 'MEDICINA_TRAFEGO',
            'NEFROLOGIA', 'NEUROCIRURGIA', 'NEUROLOGIA', 'NUTROLOGIA',
            'OFTALMOLOGIA', 'ORTOPEDIA_TRAUMATOLOGIA', 'OTORRINOLARINGOLOGIA',
            'PATOLOGIA', 'PATOLOGIA_CLINICA', 'PEDIATRIA', 'PNEUMOLOGIA',
            'PSIQUIATRIA', 'RADIOLOGIA_DIAGNOSTICO_IMAGEM', 'RADIOTERAPIA',
            'REUMATOLOGIA', 'UROLOGIA'
        );
    """)

    # =========================================================================
    # 2. REMOVE ORGANIZATION_ID FROM PROFESSIONAL_QUALIFICATIONS
    # =========================================================================

    op.drop_index(
        "uq_professional_qualifications_council_org",
        table_name="professional_qualifications",
    )
    op.drop_constraint(
        "fk_professional_qualifications_organization_id",
        "professional_qualifications",
        type_="foreignkey",
    )
    op.drop_column("professional_qualifications", "organization_id")

    # =========================================================================
    # 3. REMOVE SOFT DELETE FROM PROFESSIONAL TABLES
    # =========================================================================

    op.drop_column("professional_companies", "deleted_at")
    op.drop_column("professional_documents", "deleted_at")
    op.drop_column("professional_educations", "deleted_at")
    op.drop_column("professional_specialties", "deleted_at")
    op.drop_column("professional_qualifications", "deleted_at")

    # =========================================================================
    # 4. RESTORE SPECIALTIES TABLE STRUCTURE
    # =========================================================================

    # Drop new partial unique index
    op.drop_index("uq_specialties_code", table_name="specialties")

    # Restore column lengths
    op.alter_column(
        "specialties",
        "code",
        type_=sa.String(length=20),
        existing_type=sa.String(length=50),
        existing_nullable=False,
    )
    op.alter_column(
        "specialties",
        "name",
        type_=sa.String(length=100),
        existing_type=sa.String(length=150),
        existing_nullable=False,
    )

    # Remove soft delete column
    op.drop_column("specialties", "deleted_at")

    # Restore original columns
    op.add_column(
        "specialties",
        sa.Column(
            "professional_type",
            sa.Enum(
                "DOCTOR",
                "NURSE",
                "NURSING_TECH",
                "PHARMACIST",
                "DENTIST",
                "PHYSIOTHERAPIST",
                "PSYCHOLOGIST",
                "NUTRITIONIST",
                "BIOMEDIC",
                "OTHER",
                name="professional_type",
                create_constraint=True,
            ),
            nullable=False,
            server_default="DOCTOR",
        ),
    )
    op.add_column(
        "specialties",
        sa.Column(
            "is_generalist", sa.Boolean(), nullable=False, server_default="false"
        ),
    )
    op.add_column(
        "specialties",
        sa.Column(
            "requires_residency", sa.Boolean(), nullable=False, server_default="true"
        ),
    )
    op.add_column(
        "specialties",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    # Restore unique constraint
    op.create_unique_constraint("uq_specialties_code", "specialties", ["code"])
