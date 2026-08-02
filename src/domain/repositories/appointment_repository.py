import uuid
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.entities.appointment import Appointment


class AppointmentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, appointment_id: uuid.UUID) -> Appointment | None:
        pass

    @abstractmethod
    async def get_overlapping_for_doctor(
        self, doctor_id: uuid.UUID, start_time: datetime, end_time: datetime, exclude_id: uuid.UUID | None = None
    ) -> list[Appointment]:
        """Fetch active appointments for doctor overlapping with [start_time, end_time)."""
        pass

    @abstractmethod
    async def get_overlapping_for_patient(
        self, patient_id: uuid.UUID, start_time: datetime, end_time: datetime, exclude_id: uuid.UUID | None = None
    ) -> list[Appointment]:
        """Fetch active appointments for patient overlapping with [start_time, end_time)."""
        pass

    @abstractmethod
    async def get_by_patient(self, patient_id: uuid.UUID, skip: int = 0, limit: int = 50) -> list[Appointment]:
        pass

    @abstractmethod
    async def get_by_doctor(self, doctor_id: uuid.UUID, start_date: datetime | None = None, end_date: datetime | None = None) -> list[Appointment]:
        pass

    @abstractmethod
    async def save(self, appointment: Appointment) -> Appointment:
        pass
