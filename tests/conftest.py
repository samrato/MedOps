import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import time

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.api.dependencies.database import get_db
from src.domain.entities.doctor import Doctor
from src.domain.entities.patient import Patient
from src.domain.entities.user import User
from src.domain.entities.working_hours import WorkingHours
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.base import Base
from src.infrastructure.repositories.sqlalchemy_doctor_repository import SQLAlchemyDoctorRepository
from src.infrastructure.repositories.sqlalchemy_patient_repository import (
    SQLAlchemyPatientRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher
from src.main import app

# Shared cache mode for SQLite in-memory so concurrent connections share table state
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:memdb_medops?mode=memory&cache=shared&uri=true"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function")
async def test_db_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session


@pytest.fixture
async def async_client(test_session_factory) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_entities(test_db_session: AsyncSession):
    user_repo = SQLAlchemyUserRepository(test_db_session)
    doctor_repo = SQLAlchemyDoctorRepository(test_db_session)
    patient_repo = SQLAlchemyPatientRepository(test_db_session)

    # Doctor User
    doc_user_id = uuid.uuid4()
    doc_user = User(
        id=doc_user_id,
        email="doctor@medops.com",
        password_hash=PasswordHasher.hash_password("DoctorPass123!"),
        full_name="Dr. Gregory House",
        role=UserRole.DOCTOR,
    )
    await user_repo.save(doc_user)

    doc_id = uuid.uuid4()
    doctor = Doctor(
        id=doc_id,
        user_id=doc_user_id,
        specialty="Diagnostics",
        slot_duration_minutes=30,
        working_hours=[
            WorkingHours(
                id=uuid.uuid4(),
                doctor_id=doc_id,
                day_of_week=d,
                start_time=time(9, 0),
                end_time=time(17, 0),
                slot_duration_minutes=30,
            )
            for d in range(7)
        ],
    )
    await doctor_repo.save(doctor)

    # Patient User
    pat_user_id = uuid.uuid4()
    pat_user = User(
        id=pat_user_id,
        email="patient@medops.com",
        password_hash=PasswordHasher.hash_password("PatientPass123!"),
        full_name="John Patient",
        role=UserRole.PATIENT,
    )
    await user_repo.save(pat_user)

    pat_id = uuid.uuid4()
    patient = Patient(
        id=pat_id,
        user_id=pat_user_id,
        phone_number="+19998887777",
    )
    await patient_repo.save(patient)

    await test_db_session.commit()

    doctor_token = JWTHandler.create_access_token(doc_user_id, UserRole.DOCTOR.value)
    patient_token = JWTHandler.create_access_token(pat_user_id, UserRole.PATIENT.value)

    return {
        "doctor_user": doc_user,
        "doctor": doctor,
        "doctor_token": doctor_token,
        "patient_user": pat_user,
        "patient": patient,
        "patient_token": patient_token,
    }
