"""FastAPI application entry point."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.app.dependencies import get_settings
from src.app.exceptions import AppException
from src.app.logging import configure_logging, get_logger
from src.app.middlewares import (
    FirebaseAuthMiddleware,
    LoggingMiddleware,
    OrganizationIdentityMiddleware,
)
from src.app.presentation.api.health import router as health_router
from src.app.presentation.api.v1.router import router as v1_router
from src.shared.infrastructure.cache import RedisCache, set_redis_cache
from src.shared.infrastructure.firebase import FirebaseService, set_firebase_service


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

    # Initialize Redis cache
    redis_cache = RedisCache(settings.REDIS_URL)
    try:
        await redis_cache.connect()
        set_redis_cache(redis_cache)
        logger.info("redis_cache_initialized")
    except Exception as e:
        logger.warning("redis_cache_init_failed", error=str(e))
        # Continue without cache - graceful degradation

    # Initialize Firebase service
    try:
        firebase_service = FirebaseService(settings)
        firebase_service.initialize()
        set_firebase_service(firebase_service)
        logger.info("firebase_service_initialized")
    except Exception as e:
        logger.error("firebase_service_init_failed", error=str(e))
        # Firebase is required - but we log and continue
        # Authentication will fail if Firebase is not configured

    # TODO: Initialize database connection pool
    # TODO: Initialize message broker connection

    yield

    # Shutdown
    logger.info("application_shutting_down", app_name=settings.APP_NAME)

    # Close Redis connection
    try:
        await redis_cache.disconnect()
        logger.info("redis_cache_disconnected")
    except Exception as e:
        logger.warning("redis_cache_disconnect_failed", error=str(e))

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

    # NOTE: Middleware order is REVERSED in Starlette/FastAPI
    # Last added middleware runs FIRST in the request chain
    # So we add them in reverse order of desired execution:
    #   1. OrganizationIdentityMiddleware (added last, runs first in middleware chain
    #      but needs FirebaseAuthMiddleware to have set context)
    #   2. FirebaseAuthMiddleware (runs second, sets user context)
    #   3. LoggingMiddleware (runs third, logs request/response)
    #
    # Actually, since OrganizationIdentityMiddleware depends on FirebaseAuthMiddleware,
    # we need to add OrganizationIdentityMiddleware FIRST so it runs LAST
    # (after FirebaseAuthMiddleware has set the context)

    # Add organization identity middleware FIRST
    # (runs LAST - after FirebaseAuthMiddleware has set user context)
    app.add_middleware(
        OrganizationIdentityMiddleware,
        exclude_prefixes=(
            f"{settings.API_V1_PREFIX}/auth",  # Auth routes don't require org
            f"{settings.API_V1_PREFIX}/users/me",  # User profile doesn't require org
        ),
        require_organization=False,  # Organization header is optional by default
    )

    # Add Firebase authentication middleware SECOND
    # (runs SECOND - after logging, before organization identity)
    app.add_middleware(
        FirebaseAuthMiddleware,
        exclude_prefixes=(
            f"{settings.API_V1_PREFIX}/auth",  # Auth routes don't require auth
        ),
    )

    # Add logging middleware LAST
    # (runs FIRST - logs all requests/responses)
    app.add_middleware(LoggingMiddleware)

    # Register exception handlers
    @app.exception_handler(AppException)
    async def app_exception_handler(
        request: Request, exc: AppException
    ) -> JSONResponse:
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
