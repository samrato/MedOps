import uuid
from datetime import UTC, datetime, timedelta

import jwt

from src.domain.exceptions.domain_exceptions import UnauthorizedException
from src.infrastructure.config.settings import settings


class JWTHandler:
    @staticmethod
    def create_access_token(user_id: uuid.UUID, role: str, expires_delta: timedelta | None = None) -> str:
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": "access",
        }
        encoded_jwt = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except jwt.PyJWTError as e:
            raise UnauthorizedException(f"Invalid authentication token: {e!s}") from e
