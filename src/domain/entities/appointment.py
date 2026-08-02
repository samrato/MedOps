import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.exceptions.domain_exceptions import InvalidAppointmentStateException
from src.domain.value_objects.appointment_status import AppointmentStatus
from src.domain.value_objects.time_slot import TimeSlot


@dataclass
class Appointment:
    id: uuid.UUID
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: str = ""
    notes: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    deleted_at: datetime | None = None
    version: int = 1

    @property
    def time_slot(self) -> TimeSlot:
        return TimeSlot(start_time=self.start_time, end_time=self.end_time)

    def cancel(self, reason: str = "") -> None:
        if self.status in (AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED):
            raise InvalidAppointmentStateException(
                f"Cannot cancel appointment with status {self.status.value}"
            )
        self.status = AppointmentStatus.CANCELLED
        self.updated_at = datetime.now(UTC)
        if reason:
            self.notes = f"{self.notes}\nCancellation reason: {reason}".strip()

    def reschedule(self, new_start: datetime, new_end: datetime) -> None:
        if self.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.RESCHEDULED):
            raise InvalidAppointmentStateException(
                f"Cannot reschedule appointment in status {self.status.value}"
            )
        self.start_time = new_start
        self.end_time = new_end
        self.status = AppointmentStatus.RESCHEDULED
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        if self.status not in (AppointmentStatus.SCHEDULED, AppointmentStatus.RESCHEDULED):
            raise InvalidAppointmentStateException(
                f"Cannot complete appointment in status {self.status.value}"
            )
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.now(UTC)
