"""Professional module enums for PostgreSQL."""

from enum import Enum


class CouncilType(str, Enum):
    """
    Types of professional councils in Brazil.

    Each healthcare profession has its own regulatory council
    responsible for registration and oversight.
    """

    CRM = "CRM"  # Conselho Regional de Medicina
    COREN = "COREN"  # Conselho Regional de Enfermagem
    CRF = "CRF"  # Conselho Regional de Farmácia
    CRO = "CRO"  # Conselho Regional de Odontologia
    CREFITO = "CREFITO"  # Conselho Regional de Fisioterapia e Terapia Ocupacional
    CRP = "CRP"  # Conselho Regional de Psicologia
    CRN = "CRN"  # Conselho Regional de Nutricionistas
    CRBM = "CRBM"  # Conselho Regional de Biomedicina


class ProfessionalType(str, Enum):
    """
    Types of healthcare professionals.

    Defines the main category of healthcare worker.
    """

    DOCTOR = "DOCTOR"  # Médico
    NURSE = "NURSE"  # Enfermeiro
    NURSING_TECH = "NURSING_TECH"  # Técnico de Enfermagem
    PHARMACIST = "PHARMACIST"  # Farmacêutico
    DENTIST = "DENTIST"  # Dentista
    PHYSIOTHERAPIST = "PHYSIOTHERAPIST"  # Fisioterapeuta
    PSYCHOLOGIST = "PSYCHOLOGIST"  # Psicólogo
    NUTRITIONIST = "NUTRITIONIST"  # Nutricionista
    BIOMEDIC = "BIOMEDIC"  # Biomédico


class ResidencyStatus(str, Enum):
    """
    Medical residency status.

    Tracks the progress of a professional through their
    residency/specialization program.
    """

    R1 = "R1"  # Primeiro ano
    R2 = "R2"  # Segundo ano
    R3 = "R3"  # Terceiro ano
    R4 = "R4"  # Quarto ano
    R5 = "R5"  # Quinto ano
    R6 = "R6"  # Sexto ano (algumas especialidades)
    COMPLETED = "COMPLETED"  # Concluída


class Gender(str, Enum):
    """Gender options for professionals."""

    MALE = "MALE"
    FEMALE = "FEMALE"


class MaritalStatus(str, Enum):
    """Marital status options."""

    SINGLE = "SINGLE"  # Solteiro(a)
    MARRIED = "MARRIED"  # Casado(a)
    DIVORCED = "DIVORCED"  # Divorciado(a)
    WIDOWED = "WIDOWED"  # Viúvo(a)
    SEPARATED = "SEPARATED"  # Separado(a)
    CIVIL_UNION = "CIVIL_UNION"  # União estável


class EducationLevel(str, Enum):
    """
    Education level types.

    Covers technical courses through doctoral degrees.
    """

    TECHNICAL = "TECHNICAL"  # Curso técnico
    UNDERGRADUATE = "UNDERGRADUATE"  # Graduação
    SPECIALIZATION = "SPECIALIZATION"  # Especialização / Pós-graduação lato sensu
    MASTERS = "MASTERS"  # Mestrado
    DOCTORATE = "DOCTORATE"  # Doutorado
    POSTDOC = "POSTDOC"  # Pós-doutorado
    COURSE = "COURSE"  # Curso livre / Capacitação
    FELLOWSHIP = "FELLOWSHIP"  # Fellowship


class DocumentCategory(str, Enum):
    """
    Document category based on which entity it relates to.

    Used to group documents by their relation to professional data.
    """

    PROFILE = "PROFILE"  # Documentos pessoais do profissional
    QUALIFICATION = "QUALIFICATION"  # Documentos da qualificação/conselho
    SPECIALTY = "SPECIALTY"  # Documentos da especialidade


class DocumentType(str, Enum):
    """
    Types of documents that can be uploaded by professionals.

    Each document type has a specific purpose and may or may not
    require an expiration date.
    """

    # Profile documents (PROFILE category)
    ID_DOCUMENT = "ID_DOCUMENT"  # Documento oficial com foto (RG ou CNH)
    PHOTO = "PHOTO"  # Foto do profissional (3x4 ou similar)
    CRIMINAL_RECORD = "CRIMINAL_RECORD"  # Antecedentes criminais
    ADDRESS_PROOF = "ADDRESS_PROOF"  # Comprovante de endereço
    CV = "CV"  # Currículo

    # Qualification documents (QUALIFICATION category)
    DIPLOMA = "DIPLOMA"  # Diploma de Medicina/Enfermagem/etc
    CRM_REGISTRATION_CERTIFICATE = (
        "CRM_REGISTRATION_CERTIFICATE"  # Certidão de Regularidade de Inscrição
    )
    CRM_FINANCIAL_CERTIFICATE = (
        "CRM_FINANCIAL_CERTIFICATE"  # Certidão de Regularidade Financeira
    )
    CRM_ETHICS_CERTIFICATE = "CRM_ETHICS_CERTIFICATE"  # Certidão Ética

    # Specialty documents (SPECIALTY category)
    RESIDENCY_CERTIFICATE = (
        "RESIDENCY_CERTIFICATE"  # Certificado de Conclusão de Residência
    )
    SPECIALIST_TITLE = "SPECIALIST_TITLE"  # Título de Especialista da Sociedade
    SBA_DIPLOMA = "SBA_DIPLOMA"  # Diploma da SBA (anestesiologia)

    # Generic
    OTHER = "OTHER"  # Outros documentos


# ============================================================================
# COUNCIL ↔ PROFESSIONAL TYPE VALIDATION
# ============================================================================

# Mapping of which professional types are valid for each council
COUNCIL_TO_PROFESSIONAL_TYPES: dict[CouncilType, frozenset[ProfessionalType]] = {
    CouncilType.CRM: frozenset({ProfessionalType.DOCTOR}),
    CouncilType.COREN: frozenset(
        {ProfessionalType.NURSE, ProfessionalType.NURSING_TECH}
    ),
    CouncilType.CRF: frozenset({ProfessionalType.PHARMACIST}),
    CouncilType.CRO: frozenset({ProfessionalType.DENTIST}),
    CouncilType.CREFITO: frozenset({ProfessionalType.PHYSIOTHERAPIST}),
    CouncilType.CRP: frozenset({ProfessionalType.PSYCHOLOGIST}),
    CouncilType.CRN: frozenset({ProfessionalType.NUTRITIONIST}),
    CouncilType.CRBM: frozenset({ProfessionalType.BIOMEDIC}),
}

# Reverse mapping: which council corresponds to each professional type
PROFESSIONAL_TYPE_TO_COUNCIL: dict[ProfessionalType, CouncilType] = {
    ProfessionalType.DOCTOR: CouncilType.CRM,
    ProfessionalType.NURSE: CouncilType.COREN,
    ProfessionalType.NURSING_TECH: CouncilType.COREN,
    ProfessionalType.PHARMACIST: CouncilType.CRF,
    ProfessionalType.DENTIST: CouncilType.CRO,
    ProfessionalType.PHYSIOTHERAPIST: CouncilType.CREFITO,
    ProfessionalType.PSYCHOLOGIST: CouncilType.CRP,
    ProfessionalType.NUTRITIONIST: CouncilType.CRN,
    ProfessionalType.BIOMEDIC: CouncilType.CRBM,
}


def validate_council_for_professional_type(
    council_type: CouncilType,
    professional_type: ProfessionalType,
) -> bool:
    """
    Validate that a council type is valid for a professional type.

    For example, a DOCTOR must have CRM council, not COREN.

    Args:
        council_type: The council registration type (CRM, COREN, etc.)
        professional_type: The declared professional type (DOCTOR, NURSE, etc.)

    Returns:
        True if the council is valid for the professional type, False otherwise.
    """
    valid_types = COUNCIL_TO_PROFESSIONAL_TYPES.get(council_type, frozenset())
    return professional_type in valid_types


def get_expected_council_for_professional_type(
    professional_type: ProfessionalType,
) -> CouncilType:
    """
    Get the expected council type for a professional type.

    Args:
        professional_type: The professional type (DOCTOR, NURSE, etc.)

    Returns:
        The expected council type for this professional.

    Raises:
        KeyError: If no council mapping exists for the professional type.
    """
    return PROFESSIONAL_TYPE_TO_COUNCIL[professional_type]


# ============================================================================
# PT-BR LABELS FOR FRONTEND
# ============================================================================

# Human-readable PT-BR labels for ProfessionalType
PROFESSIONAL_TYPE_LABELS: dict[ProfessionalType, str] = {
    ProfessionalType.DOCTOR: "Médico",
    ProfessionalType.NURSE: "Enfermeiro(a)",
    ProfessionalType.NURSING_TECH: "Técnico(a) de Enfermagem",
    ProfessionalType.PHARMACIST: "Farmacêutico(a)",
    ProfessionalType.DENTIST: "Dentista",
    ProfessionalType.PHYSIOTHERAPIST: "Fisioterapeuta",
    ProfessionalType.PSYCHOLOGIST: "Psicólogo(a)",
    ProfessionalType.NUTRITIONIST: "Nutricionista",
    ProfessionalType.BIOMEDIC: "Biomédico(a)",
}

# Human-readable PT-BR labels for DocumentType
DOCUMENT_TYPE_LABELS: dict[DocumentType, str] = {
    # Profile documents
    DocumentType.ID_DOCUMENT: "Documento de Identidade (RG ou CNH)",
    DocumentType.PHOTO: "Foto 3x4",
    DocumentType.CRIMINAL_RECORD: "Certidão de Antecedentes Criminais",
    DocumentType.ADDRESS_PROOF: "Comprovante de Endereço",
    DocumentType.CV: "Currículo",
    # Qualification documents
    DocumentType.DIPLOMA: "Diploma de Graduação",
    DocumentType.CRM_REGISTRATION_CERTIFICATE: "Certidão de Regularidade de Inscrição",
    DocumentType.CRM_FINANCIAL_CERTIFICATE: "Certidão de Regularidade Financeira",
    DocumentType.CRM_ETHICS_CERTIFICATE: "Certidão Ética",
    # Specialty documents
    DocumentType.RESIDENCY_CERTIFICATE: "Certificado de Conclusão de Residência",
    DocumentType.SPECIALIST_TITLE: "Título de Especialista",
    DocumentType.SBA_DIPLOMA: "Diploma da SBA (Anestesiologia)",
    # Generic
    DocumentType.OTHER: "Outro Documento",
}
