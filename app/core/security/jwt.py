from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings

REFRESH_TOKEN_EXPIRE_DAYS = 7


def _base_payload(subject: str, token_type: str, expires_at: datetime) -> dict[str, Any]:
    issued_at = datetime.now(UTC)
    return {
        "sub": subject,
        "type": token_type,
        "iat": issued_at,
        "nbf": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
        "iss": settings.app_name,
        "aud": settings.app_name,
    }


def create_access_token(
    subject: str,
    additional_claims: dict[str, Any] | None = None,
) -> str:
    """Create a short-lived signed JWT access token."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = _base_payload(subject, "access", expires_at)

    if additional_claims:
        protected_claims = {"sub", "type", "iat", "nbf", "exp", "jti", "iss", "aud"}
        payload.update(
            {key: value for key, value in additional_claims.items() if key not in protected_claims}
        )

    return cast(
        str,
        jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm),
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived signed JWT refresh token."""
    expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = _base_payload(subject, "refresh", expires_at)
    return cast(
        str,
        jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm),
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate signature, issuer, audience, and registered claims."""
    try:
        return cast(
            dict[str, Any],
            jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
                issuer=settings.app_name,
                audience=settings.app_name,
                options={"require_sub": True, "require_exp": True, "require_iat": True},
            ),
        )
    except JWTError:
        return None


def verify_token_type(payload: dict[str, Any], expected_type: str) -> bool:
    """Check whether a JWT payload has the expected token type."""
    return payload.get("type") == expected_type
