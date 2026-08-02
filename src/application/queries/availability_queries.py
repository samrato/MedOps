import uuid
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GetDoctorAvailabilityQuery:
    doctor_id: uuid.UUID
    target_date: date
