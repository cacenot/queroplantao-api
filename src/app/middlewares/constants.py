"""Shared constants for middlewares."""

# Default paths that don't require authentication or organization context
DEFAULT_EXCLUDE_PATHS: set[str] = {
    "/health",
    "/health/",
    "/docs",
    "/docs/",
    "/redoc",
    "/redoc/",
    "/openapi.json",
}

# Header names
ORGANIZATION_ID_HEADER = "X-Organization-Id"
CHILD_ORGANIZATION_ID_HEADER = "X-Child-Organization-Id"
