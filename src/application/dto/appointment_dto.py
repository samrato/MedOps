import uuid
from dataclasses import dataclass
from datetime import datetime

from src.domain.value_objects.appointment_status import AppointmentStatus


@dataclass
class TimeSlotDTO:
    start_time: datetime
    end_time: datetime
    is_available: bool = True
    reason_unavailable: str | None = None


@dataclass
class DoctorAvailabilityDTO:
    doctor_id: uuid.UUID
    date: str
    slot_duration_minutes: int
    slots: list[TimeSlotDTO]


@dataclass
class AppointmentDTO:
    id: uuid.UUID
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    reason: str
    notes: str
    created_at: datetime
    updated_at: datetime
