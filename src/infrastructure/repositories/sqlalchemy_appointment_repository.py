import uuid
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.appointment import Appointment
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.value_objects.appointment_status import AppointmentStatus
from src.infrastructure.database.models import AppointmentModel


class SQLAlchemyAppointmentRepository(AppointmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: AppointmentModel) -> Appointment:
        return Appointment(
            id=model.id,
            doctor_id=model.doctor_id,
            patient_id=model.patient_id,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            reason=model.reason,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            version=model.version,
        )

    async def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        model = await self._session.get(AppointmentModel, appointment_id)
        return self._to_entity(model) if model else None

    async def get_overlapping_for_doctor(
        self,
        doctor_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: uuid.UUID | None = None,
        lock_for_update: bool = True,
    ) -> list[Appointment]:
        """
        Fetch active appointments for doctor that overlap with [start_time, end_time).
        Overlap condition: existing.start < requested.end AND existing.end > requested.start.
        """
        active_statuses = [AppointmentStatus.SCHEDULED, AppointmentStatus.RESCHEDULED]
        conditions = [
            AppointmentModel.doctor_id == doctor_id,
            AppointmentModel.status.in_(active_statuses),
            AppointmentModel.start_time < end_time,
            AppointmentModel.end_time > start_time,
            AppointmentModel.deleted_at.is_(None),
        ]
        if exclude_id:
            conditions.append(AppointmentModel.id != exclude_id)

        stmt = select(AppointmentModel).where(and_(*conditions))
        
        # Apply pessimistic locking in PostgreSQL to prevent race conditions
        if lock_for_update and self._session.bind and self._session.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update()

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_overlapping_for_patient(
        self,
        patient_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_id: uuid.UUID | None = None,
        lock_for_update: bool = True,
    ) -> list[Appointment]:
        """
        Fetch active appointments for patient that overlap with [start_time, end_time).
        """
        active_statuses = [AppointmentStatus.SCHEDULED, AppointmentStatus.RESCHEDULED]
        conditions = [
            AppointmentModel.patient_id == patient_id,
            AppointmentModel.status.in_(active_statuses),
            AppointmentModel.start_time < end_time,
            AppointmentModel.end_time > start_time,
            AppointmentModel.deleted_at.is_(None),
        ]
        if exclude_id:
            conditions.append(AppointmentModel.id != exclude_id)

        stmt = select(AppointmentModel).where(and_(*conditions))
        
        if lock_for_update and self._session.bind and self._session.bind.dialect.name != "sqlite":
            stmt = stmt.with_for_update()

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_patient(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Appointment]:
        stmt = (
            select(AppointmentModel)
            .where(
                and_(
                    AppointmentModel.patient_id == patient_id,
                    AppointmentModel.deleted_at.is_(None),
                )
            )
            .order_by(AppointmentModel.start_time.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def get_by_doctor(
        self, doctor_id: uuid.UUID, start_date: datetime | None = None, end_date: datetime | None = None
    ) -> list[Appointment]:
        conditions = [
            AppointmentModel.doctor_id == doctor_id,
            AppointmentModel.deleted_at.is_(None),
        ]
        if start_date:
            conditions.append(AppointmentModel.start_time >= start_date)
        if end_date:
            conditions.append(AppointmentModel.end_time <= end_date)

        stmt = select(AppointmentModel).where(and_(*conditions)).order_by(AppointmentModel.start_time.asc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    async def save(self, appointment: Appointment) -> Appointment:
        model = await self._session.get(AppointmentModel, appointment.id)
        if not model:
            model = AppointmentModel(
                id=appointment.id,
                doctor_id=appointment.doctor_id,
                patient_id=appointment.patient_id,
                start_time=appointment.start_time,
                end_time=appointment.end_time,
                status=appointment.status,
                reason=appointment.reason,
                notes=appointment.notes,
            )
            self._session.add(model)
        else:
            model.start_time = appointment.start_time
            model.end_time = appointment.end_time
            model.status = appointment.status
            model.reason = appointment.reason
            model.notes = appointment.notes
            model.deleted_at = appointment.deleted_at
            model.version += 1

        await self._session.flush()
        return self._to_entity(model)
