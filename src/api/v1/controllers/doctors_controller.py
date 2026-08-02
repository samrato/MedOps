import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import require_roles
from src.api.dependencies.database import get_db
from src.api.dependencies.services import get_availability_engine
from src.api.schemas.common import APIResponse
from src.api.schemas.doctor import (
    AvailabilityResponse,
    BreakTimeRequest,
    DoctorResponse,
    HolidayRequest,
    SlotResponse,
    WorkingHoursRequest,
)
from src.application.services.availability_engine import AvailabilityEngine
from src.domain.entities.break_time import BreakTime
from src.domain.entities.holiday import Holiday
from src.domain.entities.user import User
from src.domain.entities.working_hours import WorkingHours
from src.domain.exceptions.domain_exceptions import DoctorNotFoundException, ForbiddenException
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.repositories.sqlalchemy_doctor_repository import SQLAlchemyDoctorRepository

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/{id}/availability", response_model=APIResponse[AvailabilityResponse])
async def get_doctor_availability(
    id: uuid.UUID,
    date_str: str = Query(..., alias="date", example="2026-08-10"),
    engine: AvailabilityEngine = Depends(get_availability_engine),
):
    target_date = date.fromisoformat(date_str)
    availability = await engine.get_doctor_availability(doctor_id=id, target_date=target_date)

    resp = AvailabilityResponse(
        doctor_id=availability.doctor_id,
        date=availability.date,
        slot_duration_minutes=availability.slot_duration_minutes,
        slots=[
            SlotResponse(
                start_time=s.start_time.isoformat(),
                end_time=s.end_time.isoformat(),
                is_available=s.is_available,
                reason_unavailable=s.reason_unavailable,
            )
            for s in availability.slots
        ],
    )
    return APIResponse(success=True, data=resp)


@router.get("", response_model=APIResponse[list[DoctorResponse]])
async def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    doctor_repo = SQLAlchemyDoctorRepository(db)
    doctors = await doctor_repo.list_all(skip=skip, limit=limit)
    res = [
        DoctorResponse(
            id=d.id,
            user_id=d.user_id,
            specialty=d.specialty,
            bio=d.bio,
            slot_duration_minutes=d.slot_duration_minutes,
        )
        for d in doctors
    ]
    return APIResponse(success=True, data=res)


@router.post("/{id}/working-hours", response_model=APIResponse[str])
async def add_working_hours(
    id: uuid.UUID,
    req: WorkingHoursRequest,
    current_user: User = Depends(require_roles([UserRole.DOCTOR, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    doctor_repo = SQLAlchemyDoctorRepository(db)
    doctor = await doctor_repo.get_by_id(id)
    if not doctor:
        raise DoctorNotFoundException("Doctor not found.")
    if current_user.role == UserRole.DOCTOR and doctor.user_id != current_user.id:
        raise ForbiddenException("You cannot configure another doctor's schedule.")

    wh = WorkingHours(
        id=uuid.uuid4(),
        doctor_id=id,
        day_of_week=req.day_of_week,
        start_time=req.start_time,
        end_time=req.end_time,
        slot_duration_minutes=req.slot_duration_minutes,
    )
    doctor.working_hours.append(wh)
    await doctor_repo.save(doctor)

    return APIResponse(success=True, data="Working hours added successfully.")


@router.post("/{id}/holidays", response_model=APIResponse[str])
async def add_holiday(
    id: uuid.UUID,
    req: HolidayRequest,
    current_user: User = Depends(require_roles([UserRole.DOCTOR, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    doctor_repo = SQLAlchemyDoctorRepository(db)
    doctor = await doctor_repo.get_by_id(id)
    if not doctor:
        raise DoctorNotFoundException("Doctor not found.")
    if current_user.role == UserRole.DOCTOR and doctor.user_id != current_user.id:
        raise ForbiddenException("You cannot add holiday for another doctor.")

    holiday = Holiday(id=uuid.uuid4(), doctor_id=id, date=req.date, description=req.description)
    doctor.holidays.append(holiday)
    await doctor_repo.save(doctor)

    return APIResponse(success=True, data="Holiday added successfully.")


@router.post("/{id}/breaks", response_model=APIResponse[str])
async def add_break(
    id: uuid.UUID,
    req: BreakTimeRequest,
    current_user: User = Depends(require_roles([UserRole.DOCTOR, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    doctor_repo = SQLAlchemyDoctorRepository(db)
    doctor = await doctor_repo.get_by_id(id)
    if not doctor:
        raise DoctorNotFoundException("Doctor not found.")
    if current_user.role == UserRole.DOCTOR and doctor.user_id != current_user.id:
        raise ForbiddenException("You cannot add break for another doctor.")

    break_time = BreakTime(
        id=uuid.uuid4(),
        doctor_id=id,
        day_of_week=req.day_of_week,
        start_time=req.start_time,
        end_time=req.end_time,
        description=req.description,
    )
    doctor.breaks.append(break_time)
    await doctor_repo.save(doctor)

    return APIResponse(success=True, data="Break time added successfully.")
