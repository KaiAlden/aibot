import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from app.config.settings import settings


class AuthError(ValueError):
    pass


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("ascii"), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, expected = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("ascii"),
            int(iterations_text),
        ).hex()
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: str, role: str, tenant_id: int | None) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "role": role,
        "tenant_id": tenant_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = ".".join([_b64_json(header), _b64_json(payload)])
    signature = _sign(signing_input)
    return f"{signing_input}.{signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthError("invalid token")
    signing_input = ".".join(parts[:2])
    if not hmac.compare_digest(_sign(signing_input), parts[2]):
        raise AuthError("invalid token signature")
    payload = _loads_b64_json(parts[1])
    expires_at = int(payload.get("exp", 0))
    if expires_at < int(datetime.now(UTC).timestamp()):
        raise AuthError("token expired")
    return payload


def _sign(value: str) -> str:
    digest = hmac.new(settings.auth_secret_key.encode("utf-8"), value.encode("ascii"), hashlib.sha256).digest()
    return _b64_bytes(digest)


def _b64_json(value: dict[str, Any]) -> str:
    data = json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return _b64_bytes(data)


def _loads_b64_json(value: str) -> dict[str, Any]:
    try:
        raw = base64.urlsafe_b64decode(_pad_b64(value))
        payload = json.loads(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        raise AuthError("invalid token payload") from exc
    if not isinstance(payload, dict):
        raise AuthError("invalid token payload")
    return payload


def _b64_bytes(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _pad_b64(value: str) -> bytes:
    return (value + "=" * (-len(value) % 4)).encode("ascii")
