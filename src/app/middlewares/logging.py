"""Request logging middleware for FastAPI."""

import time
import uuid
from collections.abc import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from src.app.middlewares.constants import DEFAULT_EXCLUDE_PATHS


logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for structured request logging.

    Binds request context (request_id, method, path) to all logs within the request.
    Logs request completion with status code and duration.

    Features:
        - Generates or extracts X-Request-ID header
        - Binds context variables for all downstream logs
        - Logs request completion with timing
        - Adds X-Request-ID to response headers
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: set[str] | None = None,
    ) -> None:
        """
        Initialize logging middleware.

        Args:
            app: ASGI application
            exclude_paths: Paths to exclude from logging (e.g., health checks)
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or DEFAULT_EXCLUDE_PATHS

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        """Process request with logging context."""
        # Skip logging for excluded paths
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Clear previous context and bind new values
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # Add query params if present (for debugging)
        if request.query_params:
            structlog.contextvars.bind_contextvars(
                query=str(request.query_params),
            )

        start_time = time.perf_counter()

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Log based on status code
            status_code = response.status_code
            if status_code >= 500:
                logger.error(
                    "request_completed",
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
            elif status_code >= 400:
                logger.warning(
                    "request_completed",
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
            else:
                logger.info(
                    "request_completed",
                    status_code=status_code,
                    duration_ms=duration_ms,
                )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            logger.exception(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
            )
            raise
