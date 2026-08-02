import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities.break_time import BreakTime
from src.domain.entities.doctor import Doctor
from src.domain.entities.holiday import Holiday
from src.domain.entities.working_hours import WorkingHours
from src.domain.repositories.doctor_repository import DoctorRepository
from src.infrastructure.database.models import (
    BreakTimeModel,
    DoctorModel,
    HolidayModel,
    WorkingHoursModel,
)


class SQLAlchemyDoctorRepository(DoctorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: DoctorModel) -> Doctor:
        working_hours = [
            WorkingHours(
                id=wh.id,
                doctor_id=wh.doctor_id,
                day_of_week=wh.day_of_week,
                start_time=wh.start_time,
                end_time=wh.end_time,
                slot_duration_minutes=wh.slot_duration_minutes,
                is_active=wh.is_active,
            )
            for wh in (model.working_hours or [])
        ]
        holidays = [
            Holiday(id=h.id, doctor_id=h.doctor_id, date=h.date, description=h.description)
            for h in (model.holidays or [])
        ]
        breaks = [
            BreakTime(
                id=b.id,
                doctor_id=b.doctor_id,
                day_of_week=b.day_of_week,
                start_time=b.start_time,
                end_time=b.end_time,
                description=b.description,
            )
            for b in (model.breaks or [])
        ]
        return Doctor(
            id=model.id,
            user_id=model.user_id,
            specialty=model.specialty,
            bio=model.bio,
            slot_duration_minutes=model.slot_duration_minutes,
            working_hours=working_hours,
            holidays=holidays,
            breaks=breaks,
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )

    async def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        stmt = (
            select(DoctorModel)
            .where(DoctorModel.id == doctor_id)
            .options(
                selectinload(DoctorModel.working_hours),
                selectinload(DoctorModel.holidays),
                selectinload(DoctorModel.breaks),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> Doctor | None:
        stmt = (
            select(DoctorModel)
            .where(DoctorModel.user_id == user_id)
            .options(
                selectinload(DoctorModel.working_hours),
                selectinload(DoctorModel.holidays),
                selectinload(DoctorModel.breaks),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Doctor]:
        stmt = (
            select(DoctorModel)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(DoctorModel.working_hours),
                selectinload(DoctorModel.holidays),
                selectinload(DoctorModel.breaks),
            )
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, doctor: Doctor) -> Doctor:
        stmt = (
            select(DoctorModel)
            .where(DoctorModel.id == doctor.id)
            .options(
                selectinload(DoctorModel.working_hours),
                selectinload(DoctorModel.holidays),
                selectinload(DoctorModel.breaks),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            model = DoctorModel(
                id=doctor.id,
                user_id=doctor.user_id,
                specialty=doctor.specialty,
                bio=doctor.bio,
                slot_duration_minutes=doctor.slot_duration_minutes,
                working_hours=[
                    WorkingHoursModel(
                        id=wh.id,
                        doctor_id=wh.doctor_id,
                        day_of_week=wh.day_of_week,
                        start_time=wh.start_time,
                        end_time=wh.end_time,
                        slot_duration_minutes=wh.slot_duration_minutes,
                        is_active=wh.is_active,
                    )
                    for wh in doctor.working_hours
                ],
                holidays=[
                    HolidayModel(
                        id=h.id,
                        doctor_id=h.doctor_id,
                        date=h.date,
                        description=h.description,
                    )
                    for h in doctor.holidays
                ],
                breaks=[
                    BreakTimeModel(
                        id=b.id,
                        doctor_id=b.doctor_id,
                        day_of_week=b.day_of_week,
                        start_time=b.start_time,
                        end_time=b.end_time,
                        description=b.description,
                    )
                    for b in doctor.breaks
                ],
            )
            self._session.add(model)
        else:
            model.specialty = doctor.specialty
            model.bio = doctor.bio
            model.slot_duration_minutes = doctor.slot_duration_minutes
            model.version += 1

            # Update working hours, holidays, breaks
            model.working_hours = [
                WorkingHoursModel(
                    id=wh.id,
                    doctor_id=wh.doctor_id,
                    day_of_week=wh.day_of_week,
                    start_time=wh.start_time,
                    end_time=wh.end_time,
                    slot_duration_minutes=wh.slot_duration_minutes,
                    is_active=wh.is_active,
                )
                for wh in doctor.working_hours
            ]
            model.holidays = [
                HolidayModel(
                    id=h.id,
                    doctor_id=h.doctor_id,
                    date=h.date,
                    description=h.description,
                )
                for h in doctor.holidays
            ]
            model.breaks = [
                BreakTimeModel(
                    id=b.id,
                    doctor_id=b.doctor_id,
                    day_of_week=b.day_of_week,
                    start_time=b.start_time,
                    end_time=b.end_time,
                    description=b.description,
                )
                for b in doctor.breaks
            ]

        await self._session.flush()
        return self._to_entity(model)
