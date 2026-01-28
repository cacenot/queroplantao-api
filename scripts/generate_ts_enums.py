#!/usr/bin/env python3
"""
Generate TypeScript enum files from Python enums.

This script reads all enums from the backend modules and generates
TypeScript files with enum values and PT-BR labels.

Usage:
    uv run python scripts/generate_ts_enums.py
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "packages" / "api-client" / "src" / "enums"

# Enum source files to process
ENUM_SOURCES: list[tuple[str, Path]] = [
    (
        "professionals",
        PROJECT_ROOT
        / "src"
        / "modules"
        / "professionals"
        / "domain"
        / "models"
        / "enums.py",
    ),
    (
        "screening",
        PROJECT_ROOT
        / "src"
        / "modules"
        / "screening"
        / "domain"
        / "models"
        / "enums.py",
    ),
    (
        "users",
        PROJECT_ROOT / "src" / "modules" / "users" / "domain" / "models" / "enums.py",
    ),
    (
        "organizations",
        PROJECT_ROOT
        / "src"
        / "modules"
        / "organizations"
        / "domain"
        / "models"
        / "enums.py",
    ),
    (
        "shared",
        PROJECT_ROOT / "src" / "shared" / "domain" / "models" / "enums.py",
    ),
    (
        "shared",
        PROJECT_ROOT / "src" / "shared" / "domain" / "models" / "document_type.py",
    ),
]

# Manual PT-BR labels for enums (sync with backend when needed)
# Key: EnumName.MEMBER, Value: PT-BR label
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
        "DRAFT": "Rascunho",
        "IN_PROGRESS": "Em Andamento",
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
        "SUPERVISOR_REVIEW": "Revisão do Supervisor",
        "CLIENT_VALIDATION": "Validação do Cliente",
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
        "RQE_CERTIFICATE": "Certificado RQE",
        "COUNCIL_CARD": "Carteira do Conselho",
        "PROOF_OF_ADDRESS": "Comprovante de Endereço",
        "OTHER": "Outro",
    },
}


@dataclass
class EnumMember:
    """Represents a single enum member."""

    name: str
    value: str


@dataclass
class EnumDefinition:
    """Represents a parsed enum definition."""

    name: str
    members: list[EnumMember]
    docstring: str | None = None


MANUAL_ENUM_DEFINITIONS: dict[str, list[EnumDefinition]] = {
    "shared": [
        EnumDefinition(
            name="DocumentType",
            docstring=(
                "Types of documents that can be uploaded.\n\n"
                "Used to identify specific document types in the screening\n"
                "and professional document management flows."
            ),
            members=[
                EnumMember(name="RG", value="RG"),
                EnumMember(name="CPF", value="CPF"),
                EnumMember(name="CNH", value="CNH"),
                EnumMember(name="PASSPORT", value="PASSPORT"),
                EnumMember(name="DIPLOMA", value="DIPLOMA"),
                EnumMember(name="CERTIFICATE", value="CERTIFICATE"),
                EnumMember(name="RQE_CERTIFICATE", value="RQE_CERTIFICATE"),
                EnumMember(name="COUNCIL_CARD", value="COUNCIL_CARD"),
                EnumMember(name="PROOF_OF_ADDRESS", value="PROOF_OF_ADDRESS"),
                EnumMember(name="OTHER", value="OTHER"),
            ],
        ),
    ]
}


def parse_enums_from_file(file_path: Path) -> Iterator[EnumDefinition]:
    """Parse enum definitions from a Python file using AST."""
    if not file_path.exists():
        return

    source = file_path.read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Check if it's an Enum subclass
        is_enum = any(
            (isinstance(base, ast.Name) and base.id == "Enum")
            or (isinstance(base, ast.Attribute) and base.attr == "Enum")
            or (isinstance(base, ast.Subscript))  # str, Enum pattern
            for base in node.bases
        )

        if not is_enum:
            continue

        members: list[EnumMember] = []
        docstring = ast.get_docstring(node)

        for item in node.body:
            # Skip docstrings, methods, etc
            if not isinstance(item, ast.Assign):
                continue

            for target in item.targets:
                if not isinstance(target, ast.Name):
                    continue

                # Skip private/dunder attributes
                if target.id.startswith("_"):
                    continue

                # Get the value
                if isinstance(item.value, ast.Constant):
                    members.append(
                        EnumMember(name=target.id, value=str(item.value.value))
                    )

        if members:
            yield EnumDefinition(name=node.name, members=members, docstring=docstring)


def to_camel_case(snake_str: str) -> str:
    """Convert SNAKE_CASE to camelCase."""
    components = snake_str.lower().split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def generate_enum_ts(enum_def: EnumDefinition) -> str:
    """Generate TypeScript code for an enum."""
    lines: list[str] = []

    # Add docstring as comment
    if enum_def.docstring:
        lines.append("/**")
        for line in enum_def.docstring.split("\n"):
            lines.append(f" * {line.strip()}")
        lines.append(" */")

    # Enum definition
    lines.append(f"export enum {enum_def.name} {{")
    for member in enum_def.members:
        lines.append(f'  {member.name} = "{member.value}",')
    lines.append("}")
    lines.append("")

    # Labels object
    labels = ENUM_LABELS.get(enum_def.name, {})
    lines.append(
        f"export const {enum_def.name}Labels: Record<{enum_def.name}, string> = {{"
    )
    for member in enum_def.members:
        label = labels.get(member.name, member.name.replace("_", " ").title())
        lines.append(f'  [{enum_def.name}.{member.name}]: "{label}",')
    lines.append("};")
    lines.append("")

    # Helper function to get label
    lines.append(
        f"export function get{enum_def.name}Label(value: {enum_def.name}): string {{"
    )
    lines.append(f"  return {enum_def.name}Labels[value];")
    lines.append("}")

    return "\n".join(lines)


def generate_module_file(module_name: str, enums: list[EnumDefinition]) -> str:
    """Generate a TypeScript file for a module's enums."""
    lines: list[str] = [
        "/**",
        f" * {module_name.title()} module enums.",
        " *",
        " * AUTO-GENERATED by scripts/generate_ts_enums.py",
        " * DO NOT EDIT MANUALLY",
        " */",
        "",
    ]

    for enum_def in enums:
        lines.append(generate_enum_ts(enum_def))
        lines.append("")

    return "\n".join(lines)


def generate_index_file(modules: list[str]) -> str:
    """Generate the main index.ts file that re-exports all enums."""
    lines: list[str] = [
        "/**",
        " * Enums synchronized from the backend.",
        " *",
        " * AUTO-GENERATED by scripts/generate_ts_enums.py",
        " * DO NOT EDIT MANUALLY",
        " */",
        "",
    ]

    for module in modules:
        lines.append(f'export * from "./{module}.js";')

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    print("🔄 Generating TypeScript enums from Python...")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    modules_generated: list[str] = []
    module_enums: dict[str, list[EnumDefinition]] = {}

    for module_name, file_path in ENUM_SOURCES:
        print(f"  📄 Processing {module_name}...")

        enums = list(parse_enums_from_file(file_path))
        if not enums:
            print(f"    ⚠️  No enums found in {file_path}")
            continue

        module_enums.setdefault(module_name, []).extend(enums)
        print(f"    ✅ Collected {len(enums)} enums from {file_path.name}")

    for module_name, enums in MANUAL_ENUM_DEFINITIONS.items():
        module_enums.setdefault(module_name, []).extend(enums)
        print(f"    ✅ Added {len(enums)} manual enums for {module_name}")

    for module_name, enums in module_enums.items():
        content = generate_module_file(module_name, enums)
        output_file = OUTPUT_DIR / f"{module_name}.ts"
        output_file.write_text(content)
        modules_generated.append(module_name)
        print(f"    📦 Generated {len(enums)} enums -> {output_file.name}")

    # Generate index file
    if modules_generated:
        index_content = generate_index_file(modules_generated)
        index_file = OUTPUT_DIR / "index.ts"
        index_file.write_text(index_content)
        print(f"  📦 Generated index.ts with {len(modules_generated)} modules")

    print("✅ Done!")


if __name__ == "__main__":
    main()
