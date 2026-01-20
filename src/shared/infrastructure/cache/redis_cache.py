"""Redis cache service for application caching."""

import json
import hashlib
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis

from src.app.logging import get_logger


logger = get_logger(__name__)


class RedisCache:
    """
    Async Redis cache service with JSON serialization.

    Provides get/set/delete operations with automatic JSON serialization
    and graceful degradation on connection errors.
    """

    def __init__(self, redis_url: str) -> None:
        """
        Initialize Redis cache.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
        """
        self._redis_url = redis_url
        self._client: Redis | None = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        if self._client is None:
            self._client = redis.from_url(
                self._redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("redis_connected", url=self._redis_url.split("@")[-1])

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._client is not None:
            await self._client.close()
            self._client = None
            logger.info("redis_disconnected")

    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Deserialized value or None if not found or on error.
        """
        if self._client is None:
            return None

        try:
            value = await self._client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning("redis_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key.
            value: Value to cache (must be JSON serializable).
            ttl: Time-to-live in seconds. None for no expiration.

        Returns:
            True if successful, False on error.
        """
        if self._client is None:
            return False

        try:
            serialized = json.dumps(value, default=str)
            if ttl is not None:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)
            return True
        except (redis.RedisError, TypeError, ValueError) as e:
            logger.warning("redis_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key.

        Returns:
            True if key was deleted, False if not found or on error.
        """
        if self._client is None:
            return False

        try:
            result = await self._client.delete(key)
            return result > 0
        except redis.RedisError as e:
            logger.warning("redis_delete_error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key.

        Returns:
            True if key exists, False otherwise.
        """
        if self._client is None:
            return False

        try:
            return await self._client.exists(key) > 0
        except redis.RedisError as e:
            logger.warning("redis_exists_error", key=key, error=str(e))
            return False

    @staticmethod
    def hash_token(token: str) -> str:
        """
        Create a hash of a token for use as cache key.

        Args:
            token: Token to hash.

        Returns:
            SHA256 hash of the token.
        """
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def token_cache_key(token_hash: str) -> str:
        """
        Generate cache key for a Firebase token.

        Args:
            token_hash: Hashed token.

        Returns:
            Cache key string.
        """
        return f"firebase_token:{token_hash}"

    @staticmethod
    def user_cache_key(firebase_uid: str) -> str:
        """
        Generate cache key for a user.

        Args:
            firebase_uid: Firebase user UID.

        Returns:
            Cache key string.
        """
        return f"user:fb:{firebase_uid}"


# Global cache instance (initialized in app lifespan)
_redis_cache: RedisCache | None = None


def get_redis_cache() -> RedisCache | None:
    """Get the global Redis cache instance."""
    return _redis_cache


def set_redis_cache(cache: RedisCache) -> None:
    """Set the global Redis cache instance."""
    global _redis_cache
    _redis_cache = cache
