"""
Módulos de domínio da aplicação.
Cada módulo é independente e contém sua própria estrutura de camadas.
"""

from src.modules import (
    users,
    job_postings,
    organizations,
    professionals,
    schedules,
    shifts,
)

__all__ = [
    "users",
    "job_postings",
    "organizations",
    "professionals",
    "schedules",
    "shifts",
]
