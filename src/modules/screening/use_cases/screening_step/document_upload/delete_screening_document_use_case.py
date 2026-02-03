"""Use case for deleting a screening document and related uploads."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.config import Settings
from src.app.dependencies.settings import get_settings
from src.app.exceptions import (
    ScreeningDocumentNotFoundError,
    ScreeningProcessInvalidStatusError,
    ScreeningProcessNotFoundError,
    ScreeningStepNotFoundError,
)
from src.app.logging import get_logger
from src.modules.professionals.infrastructure.repositories import (
    ProfessionalDocumentRepository,
)
from src.modules.screening.domain.models.enums import (
    ScreeningDocumentStatus,
    ScreeningStatus,
)
from src.modules.screening.infrastructure.repositories import (
    DocumentUploadStepRepository,
    ScreeningDocumentRepository,
)
from src.shared.infrastructure.firebase import FirebaseStorageService

logger = get_logger(__name__)


class DeleteScreeningDocumentUseCase:
    """
    Delete a screening document and its associated professional document.

    Rules:
    - Allowed only when process status is IN_PROGRESS
    - If ProfessionalDocument is reused by other screenings, only delete ScreeningDocument
    - File deletion is done via background task (up to 3 attempts, log on failure)
    """

    def __init__(
        self,
        session: AsyncSession,
        settings: Settings | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.document_repository = ScreeningDocumentRepository(session)
        self.step_repository = DocumentUploadStepRepository(session)
        self.professional_document_repository = ProfessionalDocumentRepository(session)
        self.storage_service = FirebaseStorageService(self.settings)

    async def execute(
        self,
        screening_document_id: UUID,
        deleted_by: UUID,
        *,
        background_tasks: BackgroundTasks | None = None,
    ) -> None:
        """Delete a screening document by ID."""
        doc = await self.document_repository.get_by_id_with_step_and_process(
            screening_document_id
        )
        if not doc:
            raise ScreeningDocumentNotFoundError(document_id=str(screening_document_id))

        step = doc.upload_step
        if not step:
            raise ScreeningStepNotFoundError(step_id=str(doc.upload_step_id))

        process = step.process
        if not process:
            raise ScreeningProcessNotFoundError(screening_id=str(step.process_id))

        if process.status != ScreeningStatus.IN_PROGRESS:
            raise ScreeningProcessInvalidStatusError(
                current_status=process.status.value,
            )

        professional_doc = None
        if doc.professional_document_id:
            professional_doc = await self.professional_document_repository.get_by_id(
                doc.professional_document_id
            )

        reused = False
        if professional_doc:
            reused_count = (
                await self.document_repository.count_by_professional_document_id(
                    professional_doc.id,
                    exclude_id=doc.id,
                )
            )
            reused = reused_count > 0

        delete_file_path: Optional[str] = None
        if professional_doc and not reused:
            delete_file_path = self._extract_storage_path(professional_doc.file_url)

        await self.document_repository.delete(doc.id)

        if professional_doc and not reused:
            now = datetime.now(timezone.utc)
            professional_doc.deleted_at = now
            professional_doc.deleted_by = deleted_by
            self.session.add(professional_doc)

        await self._refresh_step_counts(step.id, deleted_by)

        if delete_file_path and background_tasks is not None:
            background_tasks.add_task(
                self._delete_file_with_retry,
                delete_file_path,
            )

        await self.session.flush()

    async def _refresh_step_counts(self, step_id: UUID, updated_by: UUID) -> None:
        step = await self.step_repository.get_by_id(step_id)
        if not step:
            return

        step.total_documents = await self.document_repository.count_total_for_step(
            step_id
        )
        step.required_documents = (
            await self.document_repository.count_required_for_step(step_id)
        )
        status_counts = await self.document_repository.count_by_status(step_id)
        pending = status_counts.get(ScreeningDocumentStatus.PENDING_UPLOAD, 0)
        correction = status_counts.get(ScreeningDocumentStatus.CORRECTION_NEEDED, 0)
        total = sum(status_counts.values())
        step.uploaded_documents = total - pending - correction
        step.updated_by = updated_by

    async def _delete_file_with_retry(self, path: str) -> None:
        for attempt in range(1, 4):
            deleted = await self.storage_service.delete_file(path)
            if deleted:
                return
            if attempt < 3:
                await asyncio.sleep(0.5 * attempt)

        logger.error(
            "file_delete_failed_after_retries",
            path=path,
            attempts=3,
        )

    def _extract_storage_path(self, file_url: str) -> Optional[str]:
        if not file_url:
            return None

        parsed = urlparse(file_url)
        if not parsed.path:
            return None

        path = parsed.path.lstrip("/")
        bucket_name = self.settings.FIREBASE_STORAGE_BUCKET
        if bucket_name and path.startswith(f"{bucket_name}/"):
            path = path[len(bucket_name) + 1 :]

        return path or None
