import asyncio
import uuid
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError

from src.application.commands.appointment_commands import (
    CancelAppointmentCommand,
    CreateAppointmentCommand,
    RescheduleAppointmentCommand,
)
from src.application.dto.appointment_dto import AppointmentDTO
from src.application.services.notification_service import NotificationService
from src.domain.entities.appointment import Appointment
from src.domain.entities.audit_log import AuditLog
from src.domain.events.appointment_events import (
    AppointmentBookedEvent,
    AppointmentCancelledEvent,
    AppointmentRescheduledEvent,
)
from src.domain.exceptions.domain_exceptions import (
    AppointmentNotFoundException,
    DoctorNotFoundException,
    DoctorOnBreakException,
    DoctorOnHolidayException,
    DoubleBookingException,
    OutsideWorkingHoursException,
    PastAppointmentException,
    PatientNotFoundException,
    SlotAlreadyBookedException,
)
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.audit_log_repository import AuditLogRepository
from src.domain.repositories.doctor_repository import DoctorRepository
from src.domain.repositories.patient_repository import PatientRepository
from src.domain.value_objects.time_slot import TimeSlot
from src.infrastructure.cache.redis_client import RedisCache, redis_cache

_global_booking_lock = asyncio.Lock()


class AppointmentApplicationService:
    def __init__(
        self,
        appointment_repo: AppointmentRepository,
        doctor_repo: DoctorRepository,
        patient_repo: PatientRepository,
        audit_log_repo: AuditLogRepository,
        notification_service: NotificationService,
        cache: RedisCache = redis_cache,
    ) -> None:
        self._appointment_repo = appointment_repo
        self._doctor_repo = doctor_repo
        self._patient_repo = patient_repo
        self._audit_log_repo = audit_log_repo
        self._notification_service = notification_service
        self._cache = cache

    def _to_dto(self, appointment: Appointment) -> AppointmentDTO:
        return AppointmentDTO(
            id=appointment.id,
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            start_time=appointment.start_time,
            end_time=appointment.end_time,
            status=appointment.status,
            reason=appointment.reason,
            notes=appointment.notes,
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
        )

    async def _validate_booking_rules(
        self,
        doctor_id: uuid.UUID,
        patient_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_appointment_id: uuid.UUID | None = None,
    ) -> None:
        now = datetime.now(UTC)
        slot = TimeSlot(start_time=start_time, end_time=end_time)

        if slot.is_in_past(now):
            raise PastAppointmentException("Appointments cannot be booked in the past.")

        doctor = await self._doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise DoctorNotFoundException(f"Doctor with ID {doctor_id} not found.")

        patient = await self._patient_repo.get_by_id(patient_id)
        if not patient:
            raise PatientNotFoundException(f"Patient with ID {patient_id} not found.")

        target_date = start_time.date()
        day_of_week = target_date.weekday()

        if any(h.date == target_date for h in doctor.holidays):
            raise DoctorOnHolidayException(f"Doctor is on holiday on {target_date.isoformat()}.")

        wh_today = [wh for wh in doctor.working_hours if wh.day_of_week == day_of_week and wh.is_active]
        if not wh_today:
            raise OutsideWorkingHoursException("Doctor has no working hours scheduled on this day of week.")

        start_time_only = start_time.time()
        end_time_only = end_time.time()

        is_within_working_hours = any(
            wh.start_time <= start_time_only and end_time_only <= wh.end_time for wh in wh_today
        )
        if not is_within_working_hours:
            raise OutsideWorkingHoursException("Requested time range falls outside doctor's working hours.")

        breaks_today = [b for b in doctor.breaks if b.day_of_week == day_of_week]
        for b in breaks_today:
            break_start_dt = datetime.combine(target_date, b.start_time, tzinfo=UTC)
            break_end_dt = datetime.combine(target_date, b.end_time, tzinfo=UTC)
            break_slot = TimeSlot(start_time=break_start_dt, end_time=break_end_dt)
            if slot.overlaps(break_slot):
                raise DoctorOnBreakException("Requested appointment overlaps with doctor's break time.")

        doctor_overlaps = await self._appointment_repo.get_overlapping_for_doctor(
            doctor_id, start_time, end_time, exclude_id=exclude_appointment_id
        )
        if doctor_overlaps:
            raise SlotAlreadyBookedException("Selected slot has already been booked.")

        patient_overlaps = await self._appointment_repo.get_overlapping_for_patient(
            patient_id, start_time, end_time, exclude_id=exclude_appointment_id
        )
        if patient_overlaps:
            raise DoubleBookingException("Patient already has an overlapping appointment during this time.")

    async def create_appointment(self, cmd: CreateAppointmentCommand) -> AppointmentDTO:
        start_time = cmd.start_time if cmd.start_time.tzinfo else cmd.start_time.replace(tzinfo=UTC)
        end_time = cmd.end_time if cmd.end_time.tzinfo else cmd.end_time.replace(tzinfo=UTC)

        async with _global_booking_lock:
            await self._validate_booking_rules(cmd.doctor_id, cmd.patient_id, start_time, end_time)

            appointment = Appointment(
                id=uuid.uuid4(),
                doctor_id=cmd.doctor_id,
                patient_id=cmd.patient_id,
                start_time=start_time,
                end_time=end_time,
                reason=cmd.reason,
            )

            try:
                saved_app = await self._appointment_repo.save(appointment)
            except IntegrityError as err:
                raise SlotAlreadyBookedException("Selected slot has already been booked.") from err

        await self._audit_log_repo.save(
            AuditLog(
                id=uuid.uuid4(),
                actor_id=cmd.patient_id,
                action="CREATE_APPOINTMENT",
                entity_name="Appointment",
                entity_id=saved_app.id,
                details=f"Booked slot {start_time.isoformat()} to {end_time.isoformat()}",
            )
        )

        cache_key = f"availability:{cmd.doctor_id}:{start_time.date().isoformat()}"
        await self._cache.delete(cache_key)

        event = AppointmentBookedEvent(
            appointment_id=saved_app.id,
            doctor_id=saved_app.doctor_id,
            patient_id=saved_app.patient_id,
            start_time=saved_app.start_time,
            end_time=saved_app.end_time,
        )
        await self._notification_service.send_booking_confirmation(event)

        return self._to_dto(saved_app)

    async def cancel_appointment(self, cmd: CancelAppointmentCommand) -> AppointmentDTO:
        appointment = await self._appointment_repo.get_by_id(cmd.appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(f"Appointment with ID {cmd.appointment_id} not found.")

        appointment.cancel(reason=cmd.reason)
        saved_app = await self._appointment_repo.save(appointment)

        await self._audit_log_repo.save(
            AuditLog(
                id=uuid.uuid4(),
                actor_id=cmd.actor_id,
                action="CANCEL_APPOINTMENT",
                entity_name="Appointment",
                entity_id=saved_app.id,
                details=f"Cancelled appointment. Reason: {cmd.reason}",
            )
        )

        cache_key = f"availability:{saved_app.doctor_id}:{saved_app.start_time.date().isoformat()}"
        await self._cache.delete(cache_key)

        event = AppointmentCancelledEvent(
            appointment_id=saved_app.id,
            doctor_id=saved_app.doctor_id,
            patient_id=saved_app.patient_id,
            reason=cmd.reason,
        )
        await self._notification_service.send_cancellation_notice(event)

        return self._to_dto(saved_app)

    async def reschedule_appointment(self, cmd: RescheduleAppointmentCommand) -> AppointmentDTO:
        appointment = await self._appointment_repo.get_by_id(cmd.appointment_id)
        if not appointment:
            raise AppointmentNotFoundException(f"Appointment with ID {cmd.appointment_id} not found.")

        new_start = cmd.new_start_time if cmd.new_start_time.tzinfo else cmd.new_start_time.replace(tzinfo=UTC)
        new_end = cmd.new_end_time if cmd.new_end_time.tzinfo else cmd.new_end_time.replace(tzinfo=UTC)

        async with _global_booking_lock:
            await self._validate_booking_rules(
                doctor_id=appointment.doctor_id,
                patient_id=appointment.patient_id,
                start_time=new_start,
                end_time=new_end,
                exclude_appointment_id=appointment.id,
            )

            old_start_date = appointment.start_time.date()

            appointment.reschedule(new_start, new_end)
            try:
                saved_app = await self._appointment_repo.save(appointment)
            except IntegrityError as err:
                raise SlotAlreadyBookedException("Selected slot has already been booked.") from err

        await self._audit_log_repo.save(
            AuditLog(
                id=uuid.uuid4(),
                actor_id=cmd.actor_id,
                action="RESCHEDULE_APPOINTMENT",
                entity_name="Appointment",
                entity_id=saved_app.id,
                details=f"Rescheduled to {new_start.isoformat()}",
            )
        )

        await self._cache.delete(f"availability:{saved_app.doctor_id}:{old_start_date.isoformat()}")
        await self._cache.delete(f"availability:{saved_app.doctor_id}:{new_start.date().isoformat()}")

        event = AppointmentRescheduledEvent(
            appointment_id=saved_app.id,
            doctor_id=saved_app.doctor_id,
            patient_id=saved_app.patient_id,
            new_start_time=new_start,
            new_end_time=new_end,
        )
        await self._notification_service.send_reschedule_notice(event)

        return self._to_dto(saved_app)
