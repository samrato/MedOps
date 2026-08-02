import uuid
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GetPatientAppointmentsQuery:
    patient_id: uuid.UUID
    skip: int = 0
    limit: int = 50


@dataclass(frozen=True)
class GetDoctorAppointmentsQuery:
    doctor_id: uuid.UUID
    target_date: date | None = None
