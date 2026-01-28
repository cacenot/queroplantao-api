"""Step-specific response schemas."""

from src.modules.screening.domain.schemas.steps.base import StepResponseBase
from src.modules.screening.domain.schemas.steps.conversation_step import (
    ConversationStepResponse,
)
from src.modules.screening.domain.schemas.steps.professional_data_step import (
    ProfessionalDataStepCompleteRequest,
    ProfessionalDataStepResponse,
)

__all__ = [
    # Base
    "StepResponseBase",
    # Conversation
    "ConversationStepResponse",
    # Professional Data
    "ProfessionalDataStepCompleteRequest",
    "ProfessionalDataStepResponse",
]
