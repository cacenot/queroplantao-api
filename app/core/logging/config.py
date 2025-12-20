"""Logging configuration for development and production environments."""

import logging
import sys
from typing import Literal

import structlog
from structlog.types import Processor


def configure_logging(
    log_level: str = "INFO",
    log_format: Literal["json", "text"] = "json",
    is_development: bool = False,
) -> None:
    """
    Configure structlog for the application.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format - "json" for production, "text" for development
        is_development: Whether running in development mode

    Development mode features:
        - Colored console output
        - Local time timestamps in readable format
        - Pretty exception rendering

    Production mode features:
        - JSON structured output for log aggregation
        - ISO 8601 UTC timestamps
        - Callsite information (file, function, line)
    """
    # Determine if we should use pretty console output
    use_console_renderer = log_format == "text" or is_development

    # Timestamp format based on environment
    if use_console_renderer:
        # Local time, human-readable for development
        timestamper = structlog.processors.TimeStamper(
            fmt="%Y-%m-%d %H:%M:%S", utc=False
        )
    else:
        # ISO 8601 UTC for production
        timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    # Shared processors for both structlog and stdlib
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.ExtraAdder(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]

    # Add callsite info in production for debugging
    if not use_console_renderer:
        shared_processors.append(
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.FILENAME,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                }
            )
        )

    # Configure structlog
    structlog.configure(
        processors=shared_processors
        + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Choose renderer based on environment
    if use_console_renderer:
        renderer: Processor = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )
    else:
        renderer = structlog.processors.JSONRenderer()

    # Create formatter for stdlib handlers
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # Configure root handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Configure library loggers with appropriate levels
    _configure_library_loggers(log_level)


def _configure_library_loggers(app_log_level: str) -> None:
    """
    Configure third-party library loggers.

    Sets appropriate log levels to reduce noise while keeping important messages.

    Args:
        app_log_level: Application log level for reference
    """
    # SQLAlchemy: WARNING to avoid noisy query logs
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)

    # Uvicorn: disable access log (we use middleware), keep error log
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Disable access logs
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    # AsyncPG: WARNING to reduce connection noise
    logging.getLogger("asyncpg").setLevel(logging.WARNING)

    # HTTPX: WARNING to reduce request noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # FastStream/AIO-Pika: INFO for message broker events
    logging.getLogger("faststream").setLevel(logging.INFO)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)

    # Watchfiles (uvicorn reload): WARNING
    logging.getLogger("watchfiles").setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog BoundLogger

    Example:
        ```python
        from app.core.logging import get_logger

        logger = get_logger(__name__)

        async def my_function():
            await logger.ainfo("Processing started", item_id=123)
        ```
    """
    return structlog.get_logger(name)
