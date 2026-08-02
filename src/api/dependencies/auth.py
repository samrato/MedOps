import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import ForbiddenException, UnauthorizedException
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.jwt_handler import JWTHandler

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = JWTHandler.decode_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException("Invalid token payload.")

    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(uuid.UUID(user_id_str))
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")

    return user


def require_roles(allowed_roles: list[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise ForbiddenException(f"User role {current_user.role.value} is not authorized for this operation.")
        return current_user

    return role_checker
