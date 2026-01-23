"""Firebase authentication middleware."""

from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from src.app.config import Settings
from src.app.context import RequestContext, clear_request_context, set_request_context
from src.app.dependencies import get_settings
from src.app.exceptions import (
    AuthException,
    MissingTokenError,
    UserInactiveError,
    UserNotFoundError,
)
from src.app.i18n import AuthMessages, get_message
from src.app.logging import get_logger
from src.app.middlewares.constants import DEFAULT_EXCLUDE_PATHS
from src.modules.auth.infrastructure.repositories import UserRepository
from src.shared.infrastructure.cache import RedisCache, get_redis_cache
from src.shared.infrastructure.database.connection import async_session_factory
from src.shared.infrastructure.firebase import (
    FirebaseService,
    FirebaseTokenInfo,
    get_firebase_service,
)


logger = get_logger(__name__)


class FirebaseAuthMiddleware(BaseHTTPMiddleware):
    """
    Firebase authentication middleware.

    Validates Firebase ID tokens, looks up users in the database,
    caches results in Redis, and populates RequestContext.

    Flow:
    1. Extract Bearer token from Authorization header
    2. Check token cache (Redis) - if hit, use cached token info
    3. Verify token with Firebase Admin SDK
    4. Cache verified token with TTL = exp - now - 1
    5. Check user cache (Redis) - if hit, use cached user data
    6. Look up user in database by firebase_uid
    7. Cache user data with configured TTL (30 min default)
    8. Set RequestContext with user_id, roles, permissions
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: set[str] | None = None,
        exclude_prefixes: tuple[str, ...] | None = None,
    ) -> None:
        """
        Initialize Firebase auth middleware.

        Args:
            app: ASGI application.
            exclude_paths: Exact paths to exclude from authentication.
            exclude_prefixes: Path prefixes to exclude (e.g., "/api/v1/auth").
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or DEFAULT_EXCLUDE_PATHS
        self.exclude_prefixes = exclude_prefixes or ()

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        """Process request with Firebase authentication."""
        # Skip authentication for excluded paths
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        # Skip OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        try:
            # Extract and validate token
            token = self._extract_token(request)
            if not token:
                raise MissingTokenError()

            # Get services
            settings = get_settings()
            cache = get_redis_cache()
            firebase = get_firebase_service()

            if not firebase:
                logger.error("firebase_service_not_initialized")
                return self._error_response(
                    status_code=500,
                    code="SERVICE_ERROR",
                    message=get_message(AuthMessages.FIREBASE_SERVICE_UNAVAILABLE),
                )

            # Verify token (with cache)
            token_info = await self._verify_token_with_cache(
                token=token,
                firebase=firebase,
                cache=cache,
            )

            # Get user data (with cache)
            user_data = await self._get_user_with_cache(
                firebase_uid=token_info.uid,
                cache=cache,
                settings=settings,
            )

            # Create and set request context
            context = RequestContext(
                user_id=user_data["user_id"],
                firebase_uid=user_data["firebase_uid"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                roles=user_data["roles"],
                permissions=user_data["permissions"],
                phone=user_data.get("phone"),
                cpf=user_data.get("cpf"),
                correlation_id=request.headers.get("X-Correlation-ID"),
            )
            set_request_context(context)

            # Bind user context to logs
            logger.bind(
                user_id=str(user_data["user_id"]),
                firebase_uid=user_data["firebase_uid"],
            )

            # Process request
            response = await call_next(request)
            return response

        except AuthException as e:
            logger.warning(
                "auth_failed",
                error_code=e.code,
                error_message=e.message,
            )
            return self._error_response(
                status_code=e.status_code,
                code=e.code,
                message=e.message,
                details=e.details,
            )
        except Exception as e:
            logger.exception("auth_unexpected_error", error=str(e))
            return self._error_response(
                status_code=500,
                code="INTERNAL_ERROR",
                message=get_message(AuthMessages.FIREBASE_INTERNAL_ERROR),
            )
        finally:
            # Always clear context after request
            clear_request_context()

    def _should_skip_auth(self, path: str) -> bool:
        """Check if path should skip authentication."""
        if path in self.exclude_paths:
            return True

        for prefix in self.exclude_prefixes:
            if path.startswith(prefix):
                return True

        return False

    def _extract_token(self, request: Request) -> str | None:
        """Extract Bearer token from Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    async def _verify_token_with_cache(
        self,
        token: str,
        firebase: FirebaseService,
        cache: RedisCache | None,
    ) -> FirebaseTokenInfo:
        """
        Verify Firebase token with caching.

        Args:
            token: Firebase ID token.
            firebase: Firebase service instance.
            cache: Redis cache instance (optional).

        Returns:
            Verified token information.
        """
        # Try cache first
        if cache:
            token_hash = cache.hash_token(token)
            cache_key = cache.token_cache_key(token_hash)
            cached = await cache.get(cache_key)

            if cached:
                logger.debug("token_cache_hit", token_hash=token_hash[:8])
                return FirebaseTokenInfo(
                    uid=cached["uid"],
                    email=cached.get("email"),
                    email_verified=cached.get("email_verified", False),
                    exp=cached["exp"],
                    iat=cached.get("iat", 0),
                )

        # Verify with Firebase
        token_info = firebase.verify_token(token)

        # Cache the result
        if cache:
            ttl = firebase.calculate_token_ttl(token_info)
            if ttl > 0:
                await cache.set(
                    key=cache.token_cache_key(cache.hash_token(token)),
                    value={
                        "uid": token_info.uid,
                        "email": token_info.email,
                        "email_verified": token_info.email_verified,
                        "exp": token_info.exp,
                        "iat": token_info.iat,
                    },
                    ttl=ttl,
                )
                logger.debug("token_cached", ttl=ttl)

        return token_info

    async def _get_user_with_cache(
        self,
        firebase_uid: str,
        cache: RedisCache | None,
        settings: Settings,
    ) -> dict:
        """
        Get user data with caching.

        Args:
            firebase_uid: Firebase user UID.
            cache: Redis cache instance (optional).
            settings: Application settings.

        Returns:
            Dict with user_id, roles, and permissions.

        Raises:
            UserNotFoundError: If user not found in database.
            UserInactiveError: If user account is inactive.
        """
        # Try cache first
        if cache:
            cache_key = cache.user_cache_key(firebase_uid)
            cached = await cache.get(cache_key)

            if cached:
                logger.debug("user_cache_hit", firebase_uid=firebase_uid)
                return {
                    "user_id": UUID(cached["user_id"]),
                    "firebase_uid": cached["firebase_uid"],
                    "email": cached["email"],
                    "full_name": cached["full_name"],
                    "phone": cached.get("phone"),
                    "cpf": cached.get("cpf"),
                    "roles": cached["roles"],
                    "permissions": cached["permissions"],
                }

        # Query database
        async with async_session_factory() as session:
            repo = UserRepository(session)
            user = await repo.get_by_firebase_uid(firebase_uid)

            if not user:
                raise UserNotFoundError(
                    details={"firebase_uid": firebase_uid},
                )

            if not user.is_active:
                raise UserInactiveError(
                    details={"user_id": str(user.id)},
                )

            # Extract roles and permissions
            roles = UserRepository.extract_role_codes(user)
            permissions = UserRepository.extract_permission_codes(user)

            user_data = {
                "user_id": user.id,
                "firebase_uid": user.firebase_uid,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone,
                "cpf": user.cpf,
                "roles": roles,
                "permissions": permissions,
            }

        # Cache the result
        if cache:
            await cache.set(
                key=cache.user_cache_key(firebase_uid),
                value={
                    "user_id": str(user.id),
                    "firebase_uid": user.firebase_uid,
                    "email": user.email,
                    "full_name": user.full_name,
                    "phone": user.phone,
                    "cpf": user.cpf,
                    "roles": roles,
                    "permissions": permissions,
                },
                ttl=settings.REDIS_USER_CACHE_TTL,
            )
            logger.debug(
                "user_cached",
                firebase_uid=firebase_uid,
                ttl=settings.REDIS_USER_CACHE_TTL,
            )

        return user_data

    def _error_response(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict | None = None,
    ) -> JSONResponse:
        """Create JSON error response."""
        return JSONResponse(
            status_code=status_code,
            content={
                "code": code,
                "message": message,
                "details": details or {},
            },
        )
