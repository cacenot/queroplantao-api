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


class DataScopePolicy(str, Enum):
    """
    Policy for data scope in queries.

    Controls whether queries should return data only from the current
    organization or from the entire family (parent + children/siblings).

    Used at runtime to determine query scope for shared resources.
    """

    # Only the current organization
    ORGANIZATION_ONLY = "ORGANIZATION_ONLY"

    # Entire family: parent + all children (if parent) or parent + siblings (if child)
    FAMILY = "FAMILY"
