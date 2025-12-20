"""Security utilities - JWT validation and authentication."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import Depends, Header
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.context import RequestContext, set_request_context
from app.core.dependencies import get_settings
from app.core.exceptions import AuthenticationError


class JWTPayload(BaseModel):
    """JWT payload schema from BFF."""

    sub: UUID = Field(description="User ID")
    tenant_id: UUID = Field(description="Tenant ID")
    roles: list[str] = Field(default_factory=list, description="User roles")
    exp: int = Field(description="Expiration timestamp")
    iat: int | None = Field(default=None, description="Issued at timestamp")
    iss: str | None = Field(default=None, description="Issuer")


def decode_jwt_token(token: str, settings: Settings) -> JWTPayload:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string
        settings: Application settings

    Returns:
        Decoded JWT payload

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True},
        )
        return JWTPayload(**payload)
    except JWTError as e:
        raise AuthenticationError(
            message="Invalid or expired token",
            details={"error": str(e)},
        ) from e


def extract_token_from_header(authorization: str | None) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        JWT token string

    Raises:
        AuthenticationError: If header is missing or malformed
    """
    if not authorization:
        raise AuthenticationError(message="Missing Authorization header")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError(
            message="Invalid Authorization header format. Expected: Bearer <token>"
        )

    return parts[1]


async def get_current_context(
    authorization: Annotated[str | None, Header()] = None,
    x_correlation_id: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> RequestContext:
    """
    FastAPI dependency to get current request context from JWT.

    This dependency:
    1. Extracts JWT from Authorization header
    2. Validates and decodes the token
    3. Creates and sets RequestContext in context var
    4. Returns the context for use in endpoints

    Args:
        authorization: Authorization header with Bearer token
        x_correlation_id: Optional correlation ID for request tracing
        settings: Application settings

    Returns:
        RequestContext with user and tenant information

    Raises:
        AuthenticationError: If authentication fails
    """
    token = extract_token_from_header(authorization)
    payload = decode_jwt_token(token, settings)

    context = RequestContext(
        user_id=payload.sub,
        tenant_id=payload.tenant_id,
        roles=payload.roles,
        correlation_id=x_correlation_id,
    )

    # Bind user context to structlog for all subsequent logs
    structlog.contextvars.bind_contextvars(
        user_id=str(context.user_id),
        tenant_id=str(context.tenant_id),
        roles=context.roles,
    )
    if x_correlation_id:
        structlog.contextvars.bind_contextvars(correlation_id=x_correlation_id)

    # Set in context var for access in deeper layers
    set_request_context(context)

    return context


# Type alias for dependency injection
CurrentContext = Annotated[RequestContext, Depends(get_current_context)]
