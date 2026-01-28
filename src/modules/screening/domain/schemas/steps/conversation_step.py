"""Conversation step response schema."""

from typing import Optional

from src.modules.screening.domain.models.enums import ConversationOutcome
from src.modules.screening.domain.schemas.steps.base import StepResponseBase


class ConversationStepResponse(StepResponseBase):
    """
    Response schema for conversation step.

    Includes conversation-specific fields: notes and outcome.
    """

    # Conversation-specific fields
    notes: Optional[str] = None
    outcome: Optional[ConversationOutcome] = None
