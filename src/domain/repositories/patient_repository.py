import uuid
from abc import ABC, abstractmethod

from src.domain.entities.patient import Patient


class PatientRepository(ABC):
    @abstractmethod
    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Patient | None:
        pass

    @abstractmethod
    async def save(self, patient: Patient) -> Patient:
        pass
