"""Screening routes."""

from src.modules.screening.presentation.routes.screening_document_routes import (
    router as document_router,
)
from src.modules.screening.presentation.routes.screening_process_routes import (
    router as process_router,
)
from src.modules.screening.presentation.routes.screening_public_routes import (
    router as public_router,
)
from src.modules.screening.presentation.routes.screening_step_routes import (
    router as step_router,
)

__all__ = [
    "document_router",
    "process_router",
    "public_router",
    "step_router",
]
