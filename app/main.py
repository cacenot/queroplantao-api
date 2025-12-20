"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.dependencies import get_settings
from app.core.exceptions import AppException
from app.presentation.api.health import router as health_router
from app.presentation.api.v1.router import router as v1_router


@asynccontextmanager
async def lifespan():
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")

    # TODO: Initialize database connection pool
    # TODO: Initialize message broker connection

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}...")

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
    )


if __name__ == "__main__":
    run()
