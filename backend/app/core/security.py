"""JWT token creation/verification and password hashing utilities."""

from __future__ import annotations


from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
import bcrypt

from app.core.config import settings

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    except ValueError:
        return False


def create_access_token(user_id: UUID, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str, token_type: str = "access") -> str | None:
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get("type") != token_type:
        return None
    return payload.get("sub")
