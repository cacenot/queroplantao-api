"""Common schemas for responses."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response."""

    code: str = Field(description="Error code")
    message: str = Field(description="Human-readable error message")
    details: dict | None = Field(default=None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status")
    version: str = Field(description="API version")
    environment: str = Field(description="Current environment")
