from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings

PASSWORD_ITERATIONS = 260_000
PASSWORD_SCHEME = "pbkdf2_sha256"


def utc_now() -> datetime:
    return datetime.now(UTC)


def access_token_expires_delta() -> timedelta:
    return timedelta(minutes=get_settings().access_token_expire_minutes)


def refresh_token_expires_delta() -> timedelta:
    return timedelta(days=get_settings().refresh_token_expire_days)


def access_token_expires_in_seconds() -> int:
    return int(access_token_expires_delta().total_seconds())


def refresh_token_expires_at() -> datetime:
    return utc_now() + refresh_token_expires_delta()


def get_password_hash(password: str) -> str:
    salt = secrets.token_urlsafe(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    )
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"{PASSWORD_SCHEME}${PASSWORD_ITERATIONS}${salt}${encoded}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        scheme, iterations, salt, stored = password_hash.split("$", 3)
    except ValueError:
        return False

    if scheme != PASSWORD_SCHEME:
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    )
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return hmac.compare_digest(encoded, stored)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_access_token(user_id: str, role: str) -> str:
    return _create_token(
        {
            "sub": user_id,
            "role": role,
            "type": "access",
        },
        access_token_expires_delta(),
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        {
            "sub": user_id,
            "type": "refresh",
        },
        refresh_token_expires_delta(),
    )


def decode_access_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    return payload


def decode_token(token: str) -> dict[str, Any]:
    try:
        header_segment, payload_segment, signature_segment = token.split(".")
    except ValueError as exc:
        raise ValueError("Invalid token format") from exc

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    expected_signature = _sign(signing_input)
    actual_signature = _base64url_decode(signature_segment)
    if not hmac.compare_digest(actual_signature, expected_signature):
        raise ValueError("Invalid token signature")

    payload = json.loads(_base64url_decode(payload_segment))
    expires_at = payload.get("exp")
    if not isinstance(expires_at, int) or expires_at < int(utc_now().timestamp()):
        raise ValueError("Token expired")

    return payload


def _create_token(payload: dict[str, Any], expires_delta: timedelta) -> str:
    settings = get_settings()
    if settings.algorithm != "HS256":
        raise ValueError("Only HS256 JWT algorithm is supported")

    expires_at = utc_now() + expires_delta
    token_payload = {
        **payload,
        "exp": int(expires_at.timestamp()),
        "iat": int(utc_now().timestamp()),
    }
    header = {"alg": settings.algorithm, "typ": "JWT"}

    header_segment = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = _base64url_encode(json.dumps(token_payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    signature_segment = _base64url_encode(_sign(signing_input))
    return f"{header_segment}.{payload_segment}.{signature_segment}"


def _sign(signing_input: bytes) -> bytes:
    return hmac.new(
        get_settings().secret_key.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}")
