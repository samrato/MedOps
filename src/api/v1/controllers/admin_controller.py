import uuid

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import require_roles
from src.api.dependencies.database import get_db
from src.api.schemas.common import APIResponse
from src.api.schemas.doctor import DoctorResponse
from src.domain.entities.doctor import Doctor
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import DomainException
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.models import (
    AppointmentModel,
    AuditLogModel,
    DoctorModel,
    PatientModel,
    UserModel,
)
from src.infrastructure.repositories.sqlalchemy_doctor_repository import SQLAlchemyDoctorRepository
from src.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.security.password_hasher import PasswordHasher

router = APIRouter(prefix="/admin", tags=["Admin"])


class AdminCreateDoctorRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "dr.smith@clinic.com"})
    password: str = Field(..., min_length=8, json_schema_extra={"example": "DocPass123!"})
    full_name: str = Field(..., json_schema_extra={"example": "Dr. Sarah Smith"})
    specialty: str = Field(..., json_schema_extra={"example": "Cardiology"})
    bio: str = Field("", json_schema_extra={"example": "Senior Cardiologist with 15 years experience."})
    slot_duration_minutes: int = Field(30, ge=5, le=120)


@router.post("/doctors", response_model=APIResponse[DoctorResponse], status_code=status.HTTP_201_CREATED)
async def admin_create_doctor(
    req: AdminCreateDoctorRequest,
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Admin endpoint to officially onboard and register a new doctor into the clinic system."""
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
        role=UserRole.DOCTOR,
    )
    await user_repo.save(user)

    doctor_repo = SQLAlchemyDoctorRepository(db)
    doctor = Doctor(
        id=uuid.uuid4(),
        user_id=user_id,
        specialty=req.specialty,
        bio=req.bio,
        slot_duration_minutes=req.slot_duration_minutes,
    )
    saved_doctor = await doctor_repo.save(doctor)

    resp = DoctorResponse(
        id=saved_doctor.id,
        user_id=saved_doctor.user_id,
        specialty=saved_doctor.specialty,
        bio=saved_doctor.bio,
        slot_duration_minutes=saved_doctor.slot_duration_minutes,
    )
    return APIResponse(success=True, data=resp)


@router.get("/dashboard/stats", response_model=APIResponse[dict])
async def get_dashboard_stats(
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    users_count = (await db.execute(select(UserModel))).scalars().all()
    doctors_count = (await db.execute(select(DoctorModel))).scalars().all()
    patients_count = (await db.execute(select(PatientModel))).scalars().all()
    appointments_count = (await db.execute(select(AppointmentModel))).scalars().all()

    stats = {
        "total_users": len(users_count),
        "total_doctors": len(doctors_count),
        "total_patients": len(patients_count),
        "total_appointments": len(appointments_count),
    }
    return APIResponse(success=True, data=stats)


@router.get("/audit-logs", response_model=APIResponse[list[dict]])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(AuditLogModel).order_by(AuditLogModel.timestamp.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()

    data = [
        {
            "id": str(log.id),
            "actor_id": str(log.actor_id) if log.actor_id else None,
            "action": log.action,
            "entity_name": log.entity_name,
            "entity_id": str(log.entity_id) if log.entity_id else None,
            "details": log.details,
            "timestamp": log.timestamp.isoformat(),
        }
        for log in logs
    ]
    return APIResponse(success=True, data=data)
