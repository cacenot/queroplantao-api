"""
Base models e mixins compartilhados.
"""

from src.shared.domain.models.base import (
    BaseModel,
    GlobalBaseModel,
    NAMING_CONVENTION,
    metadata,
    TenantBaseModel,
    TenantTrackableModel,
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
    TenantMixin,
    TimestampMixin,
    TrackingMixin,
    VersionMixin,
)

__all__ = [
    # Base models
    "BaseModel",
    "GlobalBaseModel",
    "NAMING_CONVENTION",
    "metadata",
    "TenantBaseModel",
    "TenantTrackableModel",
    # Fields
    "AwareDatetimeField",
    "CNPJField",
    "CPFField",
    "CPFOrCNPJField",
    "PhoneField",
    # Mixins
    "MetadataMixin",
    "PrimaryKeyMixin",
    "TenantMixin",
    "TimestampMixin",
    "TrackingMixin",
    "VersionMixin",
]
