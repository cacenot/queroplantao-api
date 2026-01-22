"""Enum response schemas for frontend consumption."""

from pydantic import BaseModel, ConfigDict


class ProfessionalTypeItem(BaseModel):
    """Response schema for a professional type enum value."""

    model_config = ConfigDict(from_attributes=True)

    value: str
    label: str
    council: str


class DocumentTypeItem(BaseModel):
    """Response schema for a document type enum value."""

    model_config = ConfigDict(from_attributes=True)

    value: str
    label: str
