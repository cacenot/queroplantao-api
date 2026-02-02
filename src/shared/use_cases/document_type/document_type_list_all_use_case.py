"""Use case for listing all document types (with caching)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.models import DocumentType
from src.shared.infrastructure.cache import get_redis_cache
from src.shared.infrastructure.filters.document_type import (
    DocumentTypeFilter,
    DocumentTypeSorting,
)
from src.shared.infrastructure.repositories.document_type_repository import (
    DocumentTypeRepository,
)
from src.shared.use_cases.document_type.cache import (
    DOCUMENT_TYPES_CACHE_KEY,
    DOCUMENT_TYPES_CACHE_TTL,
)


class ListAllDocumentTypesUseCase:
    """Use case for listing all document types without pagination (cached)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DocumentTypeRepository(session)

    async def execute(
        self,
        organization_id: UUID,
        parent_org_id: UUID,
        family_org_ids: list[UUID] | tuple[UUID, ...],
        *,
        filters: DocumentTypeFilter | None = None,
        sorting: DocumentTypeSorting | None = None,
    ) -> list[DocumentType]:
        """
        List all document types without pagination.

        Results are cached per parent organization with 1 hour TTL.
        Cache is only used when no filters are applied.

        Args:
            organization_id: The current organization UUID.
            parent_org_id: The parent organization ID (for cache key).
            family_org_ids: All organization IDs in the family.
            filters: Optional filters (bypasses cache if set).
            sorting: Optional sorting.

        Returns:
            List of all document types.
        """
        cache = get_redis_cache()
        cache_key = DOCUMENT_TYPES_CACHE_KEY.format(parent_org_id=str(parent_org_id))

        # Only use cache when no filters are applied
        has_filters = filters is not None and any(
            v is not None for v in [filters.search, filters.category, filters.is_active]
        )

        # Try cache first (only if no filters)
        if cache and not has_filters:
            cached = await cache.get(cache_key)
            if cached:
                # Reconstruct DocumentType objects from cached dicts
                return [DocumentType.model_validate(item) for item in cached]

        # Query database
        result = await self.repository.list_all_by_organization(
            organization_id=organization_id,
            family_org_ids=family_org_ids,
            filters=filters,
            sorting=sorting,
        )

        # Cache the result (only if no filters)
        if cache and not has_filters:
            # Serialize to dicts for caching
            cached_data = [item.model_dump(mode="json") for item in result]
            await cache.set(cache_key, cached_data, ttl=DOCUMENT_TYPES_CACHE_TTL)

        return result
