"""
Base models e mixins compartilhados.
"""

from src.shared.domain.models.base import (
    BaseModel,
    NAMING_CONVENTION,
    metadata,
)
from src.shared.domain.models.fields import (
    AwareDatetimeField,
    CNPJField,
    CPFField,
    CPFOrCNPJField,
    PhoneField,
)
from src.shared.domain.models.mixins import (
    MetadataMixin,
    PrimaryKeyMixin,
    SoftDeleteMixin,
    TimestampMixin,
    TrackingMixin,
    VersionMixin,
)

__all__ = [
    # Base models
    "BaseModel",
    "NAMING_CONVENTION",
    "metadata",
    # Fields
    "AwareDatetimeField",
    "CNPJField",
    "CPFField",
    "CPFOrCNPJField",
    "PhoneField",
    # Mixins
    "MetadataMixin",
    "PrimaryKeyMixin",
    "SoftDeleteMixin",
    "TimestampMixin",
    "TrackingMixin",
    "VersionMixin",
]
