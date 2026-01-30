"""
Parser for Python enum files.

Extracts enum definitions from Python source files using AST parsing.
Also provides PT-BR labels for enum values.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from queroplantao_mcp.config import ENUM_SOURCES, SHARED_DIR

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class EnumMember:
    """Represents a single enum member."""

    name: str
    value: str
    label_pt: str | None = None
    description: str | None = None


@dataclass
class EnumDefinition:
    """Represents a complete enum definition."""

    name: str
    module: str
    file_path: str
    docstring: str | None = None
    members: list[EnumMember] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "module": self.module,
            "file_path": self.file_path,
            "docstring": self.docstring,
            "members": [
                {
                    "name": m.name,
                    "value": m.value,
                    "label_pt": m.label_pt,
                    "description": m.description,
                }
                for m in self.members
            ],
        }


# =============================================================================
# PT-BR LABELS
# Copied from scripts/generate_ts_enums.py - keep in sync!
# =============================================================================

ENUM_LABELS: dict[str, dict[str, str]] = {
    # Professional types
    "ProfessionalType": {
        "DOCTOR": "Médico",
        "NURSE": "Enfermeiro",
        "NURSING_TECH": "Técnico de Enfermagem",
        "PHARMACIST": "Farmacêutico",
        "DENTIST": "Dentista",
        "PHYSIOTHERAPIST": "Fisioterapeuta",
        "PSYCHOLOGIST": "Psicólogo",
        "NUTRITIONIST": "Nutricionista",
        "BIOMEDIC": "Biomédico",
    },
    # Council types
    "CouncilType": {
        "CRM": "Conselho Regional de Medicina",
        "COREN": "Conselho Regional de Enfermagem",
        "CRF": "Conselho Regional de Farmácia",
        "CRO": "Conselho Regional de Odontologia",
        "CREFITO": "Conselho Regional de Fisioterapia e Terapia Ocupacional",
        "CRP": "Conselho Regional de Psicologia",
        "CRN": "Conselho Regional de Nutricionistas",
        "CRBM": "Conselho Regional de Biomedicina",
    },
    # Gender
    "Gender": {
        "MALE": "Masculino",
        "FEMALE": "Feminino",
    },
    # Marital status
    "MaritalStatus": {
        "SINGLE": "Solteiro(a)",
        "MARRIED": "Casado(a)",
        "DIVORCED": "Divorciado(a)",
        "WIDOWED": "Viúvo(a)",
        "SEPARATED": "Separado(a)",
        "CIVIL_UNION": "União Estável",
    },
    # Education level
    "EducationLevel": {
        "TECHNICAL": "Curso Técnico",
        "UNDERGRADUATE": "Graduação",
        "SPECIALIZATION": "Especialização",
        "MASTERS": "Mestrado",
        "DOCTORATE": "Doutorado",
        "POSTDOC": "Pós-Doutorado",
        "COURSE": "Curso Livre",
        "FELLOWSHIP": "Fellowship",
    },
    # Residency status
    "ResidencyStatus": {
        "R1": "Residente 1º ano",
        "R2": "Residente 2º ano",
        "R3": "Residente 3º ano",
        "R4": "Residente 4º ano",
        "R5": "Residente 5º ano",
        "R6": "Residente 6º ano",
        "COMPLETED": "Concluída",
    },
    # Document source type
    "DocumentSourceType": {
        "DIRECT": "Upload Direto",
        "SCREENING": "Triagem",
    },
    # Screening status
    "ScreeningStatus": {
        "IN_PROGRESS": "Em Andamento",
        "PENDING_SUPERVISOR": "Aguardando Supervisor",
        "APPROVED": "Aprovado",
        "REJECTED": "Rejeitado",
        "EXPIRED": "Expirado",
        "CANCELLED": "Cancelado",
    },
    # Step status
    "StepStatus": {
        "PENDING": "Pendente",
        "IN_PROGRESS": "Em Andamento",
        "COMPLETED": "Concluído",
        "APPROVED": "Aprovado",
        "REJECTED": "Rejeitado",
        "SKIPPED": "Pulado",
        "CANCELLED": "Cancelado",
        "CORRECTION_NEEDED": "Correção Necessária",
    },
    # Step type
    "StepType": {
        "CONVERSATION": "Conversa Inicial",
        "PROFESSIONAL_DATA": "Dados Profissionais",
        "DOCUMENT_UPLOAD": "Upload de Documentos",
        "DOCUMENT_REVIEW": "Revisão de Documentos",
        "PAYMENT_INFO": "Informações de Pagamento",
        "CLIENT_VALIDATION": "Validação do Cliente",
    },
    # Alert category
    "AlertCategory": {
        "DOCUMENT": "Documento",
        "DATA": "Dados",
        "BEHAVIOR": "Comportamento",
        "COMPLIANCE": "Conformidade",
        "QUALIFICATION": "Qualificação",
        "OTHER": "Outros",
    },
    # Source type
    "SourceType": {
        "DIRECT": "Direto",
        "SCREENING": "Triagem",
        "IMPORT": "Importação",
        "API": "API Externa",
    },
    # Change type
    "ChangeType": {
        "ADDED": "Adicionado",
        "MODIFIED": "Modificado",
        "REMOVED": "Removido",
    },
    # Screening document status
    "ScreeningDocumentStatus": {
        "PENDING_UPLOAD": "Aguardando Upload",
        "PENDING_REVIEW": "Aguardando Revisão",
        "APPROVED": "Aprovado",
        "CORRECTION_NEEDED": "Correção Necessária",
        "REUSED": "Reutilizado",
        "SKIPPED": "Pulado",
    },
    # Conversation outcome
    "ConversationOutcome": {
        "PROCEED": "Prosseguir",
        "REJECT": "Rejeitar",
    },
    # Client validation outcome
    "ClientValidationOutcome": {
        "APPROVED": "Aprovado",
        "REJECTED": "Rejeitado",
    },
    # Organization types
    "OrganizationType": {
        "HOSPITAL": "Hospital",
        "CLINIC": "Clínica",
        "LABORATORY": "Laboratório",
        "EMERGENCY_UNIT": "Pronto Socorro",
        "HEALTH_CENTER": "Centro de Saúde",
        "HOME_CARE": "Home Care",
        "OUTSOURCING_COMPANY": "Empresa Terceirizada",
        "OTHER": "Outro",
    },
    # Data scope policy
    "DataScopePolicy": {
        "ORGANIZATION_ONLY": "Somente Organização",
        "FAMILY": "Família",
    },
    # Pix key type
    "PixKeyType": {
        "CPF": "CPF",
        "CNPJ": "CNPJ",
        "EMAIL": "E-mail",
        "PHONE": "Telefone",
        "RANDOM": "Chave Aleatória",
    },
    # Account type
    "AccountType": {
        "CHECKING": "Conta Corrente",
        "SAVINGS": "Conta Poupança",
    },
    # Document category
    "DocumentCategory": {
        "PROFILE": "Perfil",
        "QUALIFICATION": "Qualificação",
        "SPECIALTY": "Especialidade",
    },
    # Document type
    "DocumentType": {
        "RG": "RG",
        "CPF": "CPF",
        "CNH": "CNH",
        "PASSPORT": "Passaporte",
        "DIPLOMA": "Diploma",
        "CERTIFICATE": "Certificado",
        "COUNCIL_CARD": "Carteira do Conselho",
        "COUNCIL_CERTIFICATE": "Certidão do Conselho",
        "SPECIALTY_TITLE": "Título de Especialista",
        "PROOF_OF_RESIDENCE": "Comprovante de Residência",
        "VOTER_REGISTRATION": "Título de Eleitor",
        "MILITARY_CERTIFICATE": "Certificado de Reservista",
        "PROFILE_PHOTO": "Foto de Perfil",
        "VACCINATION_CARD": "Cartão de Vacinação",
        "CRIMINAL_RECORD": "Antecedentes Criminais",
        "BANK_STATEMENT": "Extrato Bancário",
        "OTHER": "Outro",
    },
    # Alert severity
    "AlertSeverity": {
        "LOW": "Baixa",
        "MEDIUM": "Média",
        "HIGH": "Alta",
        "CRITICAL": "Crítica",
    },
    # Alert status
    "AlertStatus": {
        "OPEN": "Aberto",
        "IN_REVIEW": "Em Revisão",
        "RESOLVED": "Resolvido",
        "DISMISSED": "Descartado",
    },
    # User role
    "UserRole": {
        "ADMIN": "Administrador",
        "MANAGER": "Gestor",
        "VIEWER": "Visualizador",
    },
    # Invitation status
    "InvitationStatus": {
        "PENDING": "Pendente",
        "ACCEPTED": "Aceito",
        "EXPIRED": "Expirado",
        "REVOKED": "Revogado",
    },
}


def get_label(enum_name: str, member_name: str) -> str | None:
    """Get PT-BR label for an enum member."""
    if enum_name in ENUM_LABELS:
        return ENUM_LABELS[enum_name].get(member_name)
    return None


def _get_module_from_path(file_path: Path) -> str:
    """Determine the module name from a file path."""
    path_str = str(file_path)

    if str(SHARED_DIR) in path_str:
        return "shared"

    for module_name in ["professionals", "screening", "users", "organizations", "contracts", "units", "shifts"]:
        if f"/modules/{module_name}/" in path_str:
            return module_name

    return "unknown"


def _extract_docstring(node: ast.ClassDef) -> str | None:
    """Extract docstring from a class definition."""
    if (
        node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
        and isinstance(node.body[0].value.value, str)
    ):
        return node.body[0].value.value.strip()
    return None


def _extract_inline_comment(source_lines: list[str], lineno: int) -> str | None:
    """Extract inline comment from a line (after #)."""
    if lineno <= len(source_lines):
        line = source_lines[lineno - 1]
        if "#" in line:
            comment = line.split("#", 1)[1].strip()
            return comment if comment else None
    return None


def _is_str_enum(node: ast.ClassDef) -> bool:
    """Check if a class inherits from str and Enum."""
    base_names = []
    for base in node.bases:
        if isinstance(base, ast.Name):
            base_names.append(base.id)
        elif isinstance(base, ast.Attribute):
            base_names.append(base.attr)

    return "Enum" in base_names


def _parse_enum_file(file_path: Path) -> Iterator[EnumDefinition]:
    """Parse a Python file and yield enum definitions."""
    if not file_path.exists():
        return

    source = file_path.read_text(encoding="utf-8")
    source_lines = source.splitlines()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    module = _get_module_from_path(file_path)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        if not _is_str_enum(node):
            continue

        enum_name = node.name
        docstring = _extract_docstring(node)
        members: list[EnumMember] = []

        for item in node.body:
            # Skip docstring
            if isinstance(item, ast.Expr):
                continue

            # Look for assignments like: MEMBER = "VALUE"
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        member_name = target.id

                        # Extract value
                        member_value = str(item.value.value) if isinstance(item.value, ast.Constant) else member_name

                        # Get PT-BR label
                        label = get_label(enum_name, member_name)

                        # Get inline comment as description
                        description = _extract_inline_comment(source_lines, item.lineno)

                        members.append(
                            EnumMember(
                                name=member_name,
                                value=member_value,
                                label_pt=label,
                                description=description,
                            )
                        )

        if members:
            yield EnumDefinition(
                name=enum_name,
                module=module,
                file_path=str(file_path),
                docstring=docstring,
                members=members,
            )


class EnumParser:
    """Parser for extracting enum definitions from the project."""

    def __init__(self) -> None:
        self._cache: dict[str, EnumDefinition] = {}
        self._loaded = False

    def _load_all(self) -> None:
        """Load all enums from the project."""
        if self._loaded:
            return

        for _module, files in ENUM_SOURCES.items():
            for file_path in files:
                for enum_def in _parse_enum_file(file_path):
                    self._cache[enum_def.name] = enum_def

        self._loaded = True

    def list_enums(self, module: str | None = None) -> list[dict]:
        """
        List all available enums.

        Args:
            module: Optional module to filter by.

        Returns:
            List of enum summaries with name, module, and member count.
        """
        self._load_all()

        result = []
        for enum_def in self._cache.values():
            if module and enum_def.module != module:
                continue

            result.append(
                {
                    "name": enum_def.name,
                    "module": enum_def.module,
                    "member_count": len(enum_def.members),
                    "has_labels": all(m.label_pt is not None for m in enum_def.members),
                }
            )

        return sorted(result, key=lambda x: (x["module"], x["name"]))

    def get_enum(self, enum_name: str) -> dict | None:
        """
        Get detailed information about a specific enum.

        Args:
            enum_name: Name of the enum (e.g., "ScreeningStatus").

        Returns:
            Enum definition with all members and labels.
        """
        self._load_all()

        enum_def = self._cache.get(enum_name)
        if enum_def:
            return enum_def.to_dict()
        return None

    def get_all_enums(self) -> list[dict]:
        """Get all enums with full details."""
        self._load_all()
        return [e.to_dict() for e in self._cache.values()]

    def search_by_value(self, value: str) -> list[dict]:
        """
        Find enums that contain a specific value.

        Args:
            value: Value to search for.

        Returns:
            List of matches with enum name and member.
        """
        self._load_all()

        results = []
        for enum_def in self._cache.values():
            for member in enum_def.members:
                if member.value == value or member.name == value:
                    results.append(
                        {
                            "enum": enum_def.name,
                            "module": enum_def.module,
                            "member": member.name,
                            "value": member.value,
                            "label_pt": member.label_pt,
                        }
                    )

        return results


# Singleton instance
_parser: EnumParser | None = None


def get_enum_parser() -> EnumParser:
    """Get the singleton enum parser instance."""
    global _parser
    if _parser is None:
        _parser = EnumParser()
    return _parser
