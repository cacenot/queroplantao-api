"""Schemas for completing screening steps."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.modules.screening.domain.models.enums import (
    ClientValidationOutcome,
    ConversationOutcome,
)


class ConversationStepCompleteRequest(BaseModel):
    """Request schema for completing conversation step."""

    model_config = ConfigDict(from_attributes=True)

    notes: str = Field(
        min_length=10,
        max_length=4000,
        description="Notas da conversa telefônica com o profissional",
    )
    outcome: ConversationOutcome = Field(
        description="Resultado da conversa: PROCEED (prosseguir) ou REJECT (rejeitar)",
    )


class SimpleStepCompleteRequest(BaseModel):
    """Request schema for completing simple steps (no specific data required)."""

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notas opcionais sobre a etapa",
    )


class DocumentUploadStepCompleteRequest(BaseModel):
    """Request schema for completing document upload step.

    This step is completed when all required documents have been uploaded.
    The system validates that all required documents have status = UPLOADED.
    """

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notas opcionais sobre os documentos enviados",
    )


class DocumentReviewStepCompleteRequest(BaseModel):
    """Request schema for completing document review step.

    This step is completed when all documents have been reviewed.
    The system validates that no documents have status = UPLOADED (all must be APPROVED or REJECTED).
    """

    model_config = ConfigDict(from_attributes=True)

    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notas opcionais sobre a revisão",
    )


class ClientValidationStepCompleteRequest(BaseModel):
    """Request schema for completing client validation step."""

    model_config = ConfigDict(from_attributes=True)

    outcome: ClientValidationOutcome = Field(
        description="Decisão do cliente: APPROVED ou REJECTED",
    )
    validated_by_name: str = Field(
        min_length=3,
        max_length=255,
        description="Nome da pessoa no cliente que validou",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Notas do cliente sobre a validação",
    )
