import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(test_db_session: AsyncSession):
    repo = SQLAlchemyUserRepository(test_db_session)
    user_id = uuid.uuid4()

    user = User(
        id=user_id,
        email="repo_test@medops.com",
        password_hash="hash123",
        full_name="Repo Tester",
        role=UserRole.PATIENT,
    )

    saved_user = await repo.save(user)
    assert saved_user.id == user_id

    fetched = await repo.get_by_email("repo_test@medops.com")
    assert fetched is not None
    assert fetched.full_name == "Repo Tester"
