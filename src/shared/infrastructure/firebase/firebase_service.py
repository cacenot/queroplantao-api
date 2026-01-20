"""Firebase Admin SDK service for token verification."""

import base64
import json
import time
from dataclasses import dataclass

import firebase_admin
from firebase_admin import auth, credentials

from src.app.config import Settings
from src.app.exceptions import (
    ExpiredTokenError,
    FirebaseAuthError,
    FirebaseInitError,
    InvalidTokenError,
    RevokedTokenError,
)
from src.app.logging import get_logger


logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class FirebaseTokenInfo:
    """Verified Firebase token information."""

    uid: str
    email: str | None
    email_verified: bool
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp


class FirebaseService:
    """
    Firebase Admin SDK service for token verification.

    Initializes Firebase Admin SDK and provides token verification
    with detailed error handling.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize Firebase service.

        Args:
            settings: Application settings with Firebase configuration.
        """
        self._settings = settings
        self._initialized = False

    def initialize(self) -> None:
        """
        Initialize Firebase Admin SDK.

        Decodes base64 credentials and initializes the SDK.
        Only initializes once; subsequent calls are no-ops.

        Raises:
            FirebaseInitError: If initialization fails.
        """
        if self._initialized:
            return

        if firebase_admin._apps:
            # Already initialized (e.g., in another instance)
            self._initialized = True
            return

        try:
            if not self._settings.FIREBASE_CREDENTIALS_BASE64:
                raise FirebaseInitError(
                    message="Firebase credentials not configured",
                    details={
                        "hint": "Set FIREBASE_CREDENTIALS_BASE64 environment variable"
                    },
                )

            # Decode base64 credentials
            creds_json = base64.b64decode(
                self._settings.FIREBASE_CREDENTIALS_BASE64
            ).decode("utf-8")
            creds_dict = json.loads(creds_json)

            # Initialize Firebase Admin SDK
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(
                cred,
                {
                    "projectId": self._settings.FIREBASE_PROJECT_ID
                    or creds_dict.get("project_id"),
                },
            )

            self._initialized = True
            logger.info(
                "firebase_initialized",
                project_id=self._settings.FIREBASE_PROJECT_ID,
            )

        except json.JSONDecodeError as e:
            raise FirebaseInitError(
                message="Invalid Firebase credentials JSON",
                details={"error": str(e)},
            ) from e
        except ValueError as e:
            raise FirebaseInitError(
                message="Invalid Firebase credentials",
                details={"error": str(e)},
            ) from e
        except Exception as e:
            raise FirebaseInitError(
                message="Failed to initialize Firebase",
                details={"error": str(e)},
            ) from e

    def verify_token(self, token: str, check_revoked: bool = True) -> FirebaseTokenInfo:
        """
        Verify a Firebase ID token.

        Args:
            token: Firebase ID token to verify.
            check_revoked: Whether to check if the token has been revoked.

        Returns:
            FirebaseTokenInfo with verified token claims.

        Raises:
            InvalidTokenError: If token is invalid or malformed.
            ExpiredTokenError: If token has expired.
            RevokedTokenError: If token has been revoked.
            FirebaseAuthError: For other Firebase authentication errors.
        """
        if not self._initialized:
            self.initialize()

        try:
            decoded_token = auth.verify_id_token(
                token,
                check_revoked=check_revoked,
            )

            return FirebaseTokenInfo(
                uid=decoded_token["uid"],
                email=decoded_token.get("email"),
                email_verified=decoded_token.get("email_verified", False),
                exp=decoded_token["exp"],
                iat=decoded_token.get("iat", 0),
            )

        except auth.ExpiredIdTokenError as e:
            raise ExpiredTokenError(
                message="Firebase token has expired",
                details={"error": str(e)},
            ) from e
        except auth.RevokedIdTokenError as e:
            raise RevokedTokenError(
                message="Firebase token has been revoked",
                details={"error": str(e)},
            ) from e
        except auth.InvalidIdTokenError as e:
            raise InvalidTokenError(
                message="Invalid Firebase token",
                details={"error": str(e)},
            ) from e
        except auth.CertificateFetchError as e:
            raise FirebaseAuthError(
                message="Failed to fetch Firebase certificates",
                details={"error": str(e)},
            ) from e
        except Exception as e:
            raise FirebaseAuthError(
                message="Firebase authentication failed",
                details={"error": str(e)},
            ) from e

    def calculate_token_ttl(self, token_info: FirebaseTokenInfo) -> int:
        """
        Calculate TTL for caching a token based on expiration.

        Returns expiration time minus current time minus 1 second
        as a safety margin.

        Args:
            token_info: Verified token information.

        Returns:
            TTL in seconds (minimum 0).
        """
        ttl = token_info.exp - int(time.time()) - 1
        return max(0, ttl)


# Global Firebase service instance
_firebase_service: FirebaseService | None = None


def get_firebase_service() -> FirebaseService | None:
    """Get the global Firebase service instance."""
    return _firebase_service


def set_firebase_service(service: FirebaseService) -> None:
    """Set the global Firebase service instance."""
    global _firebase_service
    _firebase_service = service
