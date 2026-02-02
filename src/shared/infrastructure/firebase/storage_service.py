"""Firebase Storage service for file uploads."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any, BinaryIO
from uuid import UUID

from firebase_admin import storage

if TYPE_CHECKING:
    from google.cloud.storage import Bucket

from src.app.config import Settings
from src.app.exceptions import ValidationError
from src.app.logging import get_logger

logger = get_logger(__name__)


# Allowed MIME types for document uploads
ALLOWED_MIME_TYPES = frozenset(
    {
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/heic",
        "image/heif",
    }
)

# Maximum file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class UploadedFile:
    """Information about an uploaded file."""

    url: str
    path: str
    content_type: str
    size: int


class FirebaseStorageService:
    """
    Firebase Storage service for file uploads.

    Provides methods to upload files to Firebase Storage
    with validation and organized path structure.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize Firebase Storage service.

        Args:
            settings: Application settings with Firebase configuration.
        """
        self._settings = settings
        self._bucket_name = settings.FIREBASE_STORAGE_BUCKET
        self._bucket: Bucket | None = None

    def _get_bucket(self) -> Any:
        """Get or initialize the storage bucket."""
        if self._bucket is None:
            if not self._bucket_name:
                raise ValidationError(
                    message="Firebase Storage bucket not configured",
                    details={
                        "hint": "Set FIREBASE_STORAGE_BUCKET environment variable"
                    },
                )
            self._bucket = storage.bucket(self._bucket_name)
        return self._bucket

    def _validate_file(
        self,
        file_size: int,
        content_type: str | None,
    ) -> str:
        """
        Validate file before upload.

        Args:
            file_size: Size of the file in bytes.
            content_type: MIME type of the file.

        Returns:
            Validated content type.

        Raises:
            ValidationError: If file doesn't meet requirements.
        """
        # Validate size
        if file_size > MAX_FILE_SIZE:
            raise ValidationError(
                message=f"Arquivo muito grande. Tamanho máximo: {MAX_FILE_SIZE // (1024 * 1024)} MB",
                details={
                    "max_size_bytes": MAX_FILE_SIZE,
                    "file_size_bytes": file_size,
                },
            )

        if file_size == 0:
            raise ValidationError(message="Arquivo vazio não é permitido")

        # Validate content type
        if not content_type:
            raise ValidationError(message="Tipo de arquivo não especificado")

        if content_type not in ALLOWED_MIME_TYPES:
            raise ValidationError(
                message=f"Tipo de arquivo não permitido: {content_type}",
                details={
                    "allowed_types": list(ALLOWED_MIME_TYPES),
                    "received_type": content_type,
                },
            )

        return content_type

    def _generate_path(
        self,
        organization_id: UUID,
        professional_id: UUID,
        screening_id: UUID,
        document_type_id: UUID,
        file_name: str,
    ) -> str:
        """
        Generate organized storage path for the file.

        Structure: organizations/{org_id}/professionals/{prof_id}/screenings/{scr_id}/{doc_type_id}/{timestamp}_{filename}

        Args:
            organization_id: Organization UUID.
            professional_id: Professional UUID.
            screening_id: Screening process UUID.
            document_type_id: Document type UUID.
            file_name: Original file name.

        Returns:
            Full path in storage bucket.
        """
        # Sanitize filename
        safe_name = PurePosixPath(file_name).name  # Remove any path components
        safe_name = safe_name.replace(" ", "_")

        # Add timestamp to prevent collisions
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        path = (
            f"organizations/{organization_id}"
            f"/professionals/{professional_id}"
            f"/screenings/{screening_id}"
            f"/{document_type_id}"
            f"/{timestamp}_{safe_name}"
        )

        return path

    async def upload_file(
        self,
        file: BinaryIO,
        file_name: str,
        file_size: int,
        content_type: str | None,
        organization_id: UUID,
        professional_id: UUID,
        screening_id: UUID,
        document_type_id: UUID,
    ) -> UploadedFile:
        """
        Upload a file to Firebase Storage.

        Args:
            file: File-like object with the content.
            file_name: Original file name.
            file_size: Size of the file in bytes.
            content_type: MIME type of the file.
            organization_id: Organization UUID.
            professional_id: Professional UUID.
            screening_id: Screening process UUID.
            document_type_id: Document type UUID.

        Returns:
            UploadedFile with URL and metadata.

        Raises:
            ValidationError: If file doesn't meet requirements.
        """
        # Validate file
        validated_content_type = self._validate_file(file_size, content_type)

        # Generate path
        path = self._generate_path(
            organization_id=organization_id,
            professional_id=professional_id,
            screening_id=screening_id,
            document_type_id=document_type_id,
            file_name=file_name,
        )

        # Upload to Firebase Storage
        bucket = self._get_bucket()
        blob = bucket.blob(path)

        # Read content (sync operation - Firebase SDK is sync)
        content = file.read()

        blob.upload_from_string(
            content,
            content_type=validated_content_type,
        )

        # Make the blob publicly accessible or generate signed URL
        # Using signed URL for security (1 year validity)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(days=365),
            method="GET",
        )

        logger.info(
            "file_uploaded",
            path=path,
            size=file_size,
            content_type=validated_content_type,
        )

        return UploadedFile(
            url=url,
            path=path,
            content_type=validated_content_type,
            size=file_size,
        )

    async def delete_file(self, path: str) -> bool:
        """
        Delete a file from Firebase Storage.

        Args:
            path: Path of the file in the bucket.

        Returns:
            True if deleted, False if not found.
        """
        try:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            blob.delete()
            logger.info("file_deleted", path=path)
            return True
        except Exception as e:
            logger.warning("file_delete_failed", path=path, error=str(e))
            return False


# Global storage service instance
_storage_service: FirebaseStorageService | None = None


def get_storage_service() -> FirebaseStorageService | None:
    """Get the global Firebase Storage service instance."""
    return _storage_service


def set_storage_service(service: FirebaseStorageService) -> None:
    """Set the global Firebase Storage service instance."""
    global _storage_service
    _storage_service = service
