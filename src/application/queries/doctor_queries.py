import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class GetDoctorDetailsQuery:
    doctor_id: uuid.UUID


@dataclass(frozen=True)
class ListDoctorsQuery:
    skip: int = 0
    limit: int = 50
