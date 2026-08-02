import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.schemas.auth import LoginRequest, RegisterUserRequest, TokenResponse
from src.api.schemas.common import APIResponse
from src.domain.entities.doctor import Doctor
from src.domain.entities.patient import Patient
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import DomainException, UnauthorizedException
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.repositories.sqlalchemy_doctor_repository import SQLAlchemyDoctorRepository
from src.infrastructure.repositories.sqlalchemy_patient_repository import (
    SQLAlchemyPatientRepository,
)
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.jwt_handler import JWTHandler
from src.infrastructure.security.password_hasher import PasswordHasher

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register(req: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    user_repo = SQLAlchemyUserRepository(db)
    existing = await user_repo.get_by_email(req.email)
    if existing:
        raise DomainException("User with this email already exists.")

    hashed_pw = PasswordHasher.hash_password(req.password)
    user_id = uuid.uuid4()
    user = User(
        id=user_id,
        email=req.email,
        password_hash=hashed_pw,
        full_name=req.full_name,
        role=req.role,
    )
    await user_repo.save(user)

    if req.role == UserRole.DOCTOR:
        doctor_repo = SQLAlchemyDoctorRepository(db)
        doctor = Doctor(
            id=uuid.uuid4(),
            user_id=user_id,
            specialty=req.specialty or "General Practice",
        )
        await doctor_repo.save(doctor)
    elif req.role == UserRole.PATIENT:
        patient_repo = SQLAlchemyPatientRepository(db)
        patient = Patient(
            id=uuid.uuid4(),
            user_id=user_id,
            phone_number=req.phone_number or "",
        )
        await patient_repo.save(patient)

    access_token = JWTHandler.create_access_token(user_id=user_id, role=user.role.value)
    token_resp = TokenResponse(access_token=access_token, role=user.role.value, user_id=str(user_id))
    return APIResponse(success=True, data=token_resp)


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_email(req.email)
    if not user or not PasswordHasher.verify_password(req.password, user.password_hash):
        raise UnauthorizedException("Invalid email or password.")

    access_token = JWTHandler.create_access_token(user_id=user.id, role=user.role.value)
    token_resp = TokenResponse(access_token=access_token, role=user.role.value, user_id=str(user.id))
    return APIResponse(success=True, data=token_resp)
