import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateAppointmentCommand:
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    reason: str = ""


@dataclass(frozen=True)
class CancelAppointmentCommand:
    appointment_id: uuid.UUID
    actor_id: uuid.UUID
    reason: str = ""


@dataclass(frozen=True)
class RescheduleAppointmentCommand:
    appointment_id: uuid.UUID
    actor_id: uuid.UUID
    new_start_time: datetime
    new_end_time: datetime
