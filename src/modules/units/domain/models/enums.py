"""Units module enums for PostgreSQL."""

from enum import Enum


class UnitType(str, Enum):
    """
    Types of healthcare units/facilities.

    Defines the main category of the work location.
    """

    HOSPITAL = "HOSPITAL"  # Hospital
    CLINIC = "CLINIC"  # Clínica
    UPA = "UPA"  # Unidade de Pronto Atendimento
    UBS = "UBS"  # Unidade Básica de Saúde
    EMERGENCY_ROOM = "EMERGENCY_ROOM"  # Pronto Socorro
    LABORATORY = "LABORATORY"  # Laboratório
    HOME_CARE = "HOME_CARE"  # Home Care / Atendimento Domiciliar
    SURGERY_CENTER = "SURGERY_CENTER"  # Centro Cirúrgico
    DIALYSIS_CENTER = "DIALYSIS_CENTER"  # Centro de Diálise
    IMAGING_CENTER = "IMAGING_CENTER"  # Centro de Imagem
    MATERNITY = "MATERNITY"  # Maternidade
    REHABILITATION = "REHABILITATION"  # Centro de Reabilitação
    OTHER = "OTHER"  # Outros
