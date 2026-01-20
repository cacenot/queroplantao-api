"""Organization module enums for PostgreSQL."""

from enum import Enum


class OrganizationType(str, Enum):
    """
    Types of healthcare organizations.

    Defines the main category of the organization.
    """

    HOSPITAL = "HOSPITAL"  # Hospital
    CLINIC = "CLINIC"  # Clínica
    LABORATORY = "LABORATORY"  # Laboratório
    EMERGENCY_UNIT = "EMERGENCY_UNIT"  # UPA / Pronto Socorro
    HEALTH_CENTER = "HEALTH_CENTER"  # Posto de Saúde / UBS
    HOME_CARE = "HOME_CARE"  # Home Care
    OUTSOURCING_COMPANY = "OUTSOURCING_COMPANY"  # Empresa Terceirizadora / Licitadora
    OTHER = "OTHER"  # Outros


class SharingScope(str, Enum):
    """
    Defines what data a parent organization shares with child organizations.

    Used to control visibility between organizations in a hierarchy.
    """

    NONE = "NONE"  # Nenhum compartilhamento
    PROFESSIONALS = "PROFESSIONALS"  # Compartilha apenas profissionais
    SCHEDULES = "SCHEDULES"  # Compartilha profissionais + escalas
    FULL = "FULL"  # Compartilhamento total
