"""
Módulos de domínio da aplicação.
Cada módulo é independente e contém sua própria estrutura de camadas.
"""

from src.modules import (
    auth,
    job_postings,
    organizations,
    professionals,
    schedules,
    shifts,
)

__all__ = [
    "auth",
    "job_postings",
    "organizations",
    "professionals",
    "schedules",
    "shifts",
]
