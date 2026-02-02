"""Document type cache utilities."""

from uuid import UUID

from src.shared.infrastructure.cache import get_redis_cache


# Cache key pattern for document types
DOCUMENT_TYPES_CACHE_KEY = "doc_types:{parent_org_id}"
DOCUMENT_TYPES_CACHE_TTL = 3600  # 1 hour


async def invalidate_document_types_cache(parent_org_id: UUID) -> None:
    """
    Invalidate document types cache for the organization.

    Args:
        parent_org_id: The parent organization ID (cache key identifier).
    """
    cache = get_redis_cache()
    if cache:
        cache_key = DOCUMENT_TYPES_CACHE_KEY.format(parent_org_id=str(parent_org_id))
        await cache.delete(cache_key)
