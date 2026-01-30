"""Configuration for the MCP server."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

# =============================================================================
# PATH CONFIGURATION
# =============================================================================

# MCP server root
MCP_ROOT: Final[Path] = Path(__file__).parent.parent.parent

# API project root (queroplantao-api)
PROJECT_ROOT: Final[Path] = MCP_ROOT.parent.parent

# Source directories
SRC_DIR: Final[Path] = PROJECT_ROOT / "src"
MODULES_DIR: Final[Path] = SRC_DIR / "modules"
SHARED_DIR: Final[Path] = SRC_DIR / "shared"

# Documentation directories
DOCS_DIR: Final[Path] = PROJECT_ROOT / "docs"
MODULES_DOCS_DIR: Final[Path] = DOCS_DIR / "modules"
BRUNO_DIR: Final[Path] = DOCS_DIR / "bruno"

# API Client
API_CLIENT_DIR: Final[Path] = PROJECT_ROOT / "packages" / "api-client"
OPENAPI_SPEC_PATH: Final[Path] = API_CLIENT_DIR / "openapi.json"

# Scripts
SCRIPTS_DIR: Final[Path] = PROJECT_ROOT / "scripts"
TS_ENUMS_SCRIPT: Final[Path] = SCRIPTS_DIR / "generate_ts_enums.py"

# =============================================================================
# MODULE CONFIGURATION
# =============================================================================

# All available modules in the API
AVAILABLE_MODULES: Final[list[str]] = [
    "contracts",
    "job_postings",
    "organizations",
    "professionals",
    "schedules",
    "screening",
    "shifts",
    "units",
    "users",
]

# Module descriptions (in Portuguese)
MODULE_DESCRIPTIONS: Final[dict[str, str]] = {
    "contracts": "Gestão de contratos com clientes e profissionais",
    "job_postings": "Publicação e gestão de vagas de plantão",
    "organizations": "Gestão de organizações e membros",
    "professionals": "Cadastro e gestão de profissionais de saúde",
    "schedules": "Escalas e agendamentos de plantões",
    "screening": "Processo de triagem de profissionais",
    "shifts": "Gestão de plantões e turnos",
    "units": "Unidades de saúde e locais de trabalho",
    "users": "Usuários e autenticação",
}

# Enum source files per module
ENUM_SOURCES: Final[dict[str, list[Path]]] = {
    "professionals": [MODULES_DIR / "professionals" / "domain" / "models" / "enums.py"],
    "screening": [MODULES_DIR / "screening" / "domain" / "models" / "enums.py"],
    "users": [MODULES_DIR / "users" / "domain" / "models" / "enums.py"],
    "organizations": [MODULES_DIR / "organizations" / "domain" / "models" / "enums.py"],
    "contracts": [MODULES_DIR / "contracts" / "domain" / "models" / "enums.py"],
    "shared": [
        SHARED_DIR / "domain" / "models" / "enums.py",
        SHARED_DIR / "domain" / "models" / "document_type.py",
    ],
}

# =============================================================================
# LLM CONFIGURATION
# =============================================================================

# OpenAI API Key (from environment)
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")

# Model to use for analysis tools
LLM_MODEL: Final[str] = os.getenv("MCP_LLM_MODEL", "gpt-4o-mini")

# Temperature for LLM responses (lower = more deterministic)
LLM_TEMPERATURE: Final[float] = float(os.getenv("MCP_LLM_TEMPERATURE", "0.1"))

# Max tokens for LLM responses
LLM_MAX_TOKENS: Final[int] = int(os.getenv("MCP_LLM_MAX_TOKENS", "4096"))

# =============================================================================
# SERVER CONFIGURATION
# =============================================================================

# Server name for MCP protocol
SERVER_NAME: Final[str] = "queroplantao-mcp"

# Server description
SERVER_DESCRIPTION: Final[str] = (
    "MCP Server for Quero Plantão API providing technical documentation, "
    "schema information, business rules, and code analysis tools."
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_module_path(module: str) -> Path:
    """Get the path to a module's directory."""
    if module not in AVAILABLE_MODULES:
        raise ValueError(f"Unknown module: {module}. Available: {AVAILABLE_MODULES}")
    return MODULES_DIR / module


def get_module_docs_path(module: str) -> Path | None:
    """Get the path to a module's documentation file, if it exists."""
    doc_path = MODULES_DOCS_DIR / f"{module.upper()}_MODULE.md"
    return doc_path if doc_path.exists() else None


def get_enum_files(module: str | None = None) -> list[Path]:
    """Get all enum files, optionally filtered by module."""
    if module:
        return ENUM_SOURCES.get(module, [])

    all_files: list[Path] = []
    for files in ENUM_SOURCES.values():
        all_files.extend(files)
    return all_files


def validate_project_structure() -> dict[str, bool]:
    """Validate that the project structure is accessible."""
    return {
        "project_root": PROJECT_ROOT.exists(),
        "src_dir": SRC_DIR.exists(),
        "modules_dir": MODULES_DIR.exists(),
        "docs_dir": DOCS_DIR.exists(),
        "openapi_spec": OPENAPI_SPEC_PATH.exists(),
        "api_client": API_CLIENT_DIR.exists(),
    }
