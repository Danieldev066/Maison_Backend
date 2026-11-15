import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

_ITERATIONS = 600_000
_ALGORITHM = "pbkdf2_sha256"


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${_encode(salt)}${_encode(hashed)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iteration_text, salt_encoded, expected_encoded = stored.split("$")
        iterations = int(iteration_text)
        if algorithm != _ALGORITHM or not 100_000 <= iterations <= 2_000_000:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _decode(salt_encoded), iterations)
        return hmac.compare_digest(actual, _decode(expected_encoded))
    except (ValueError, TypeError, base64.binascii.Error):
        return False


def issue_access_token(user_id: int) -> tuple[str, int]:
    settings = get_settings()
    lifetime = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": str(user_id), "type": "access", "iat": now, "exp": now + timedelta(seconds=lifetime)},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return token, lifetime


def parse_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, get_settings().SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        sub = payload.get("sub")
        if not isinstance(sub, str) or not sub.isdigit():
            return None
        return int(sub)
    except jwt.InvalidTokenError:
        return None
