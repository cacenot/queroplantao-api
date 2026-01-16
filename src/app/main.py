"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.app.dependencies import get_settings
from src.app.exceptions import AppException
from src.app.logging import LoggingMiddleware, configure_logging, get_logger
from src.app.presentation.api.health import router as health_router
from src.app.presentation.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Get settings and configure logging first
    settings = get_settings()
    configure_logging(
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        is_development=settings.is_development,
    )

    logger = get_logger(__name__)

    # Startup
    logger.info(
        "application_starting",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        log_level=settings.LOG_LEVEL,
    )

    # TODO: Initialize database connection pool
    # TODO: Initialize message broker connection

    yield

    # Shutdown
    logger.info("application_shutting_down", app_name=settings.APP_NAME)

    # TODO: Close database connections
    # TODO: Close message broker connections


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        description="REST API para gestão de plantões médicos",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Add logging middleware (after CORS, before routes)
    app.add_middleware(LoggingMiddleware)

    # Register exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Include routers
    app.include_router(health_router)
    app.include_router(v1_router)

    return app


# Create application instance
app = create_app()


def run() -> None:
    """Run the application with uvicorn."""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if not settings.RELOAD else 1,
        access_log=False,  # Disable uvicorn access log, we use LoggingMiddleware
    )


if __name__ == "__main__":
    run()
