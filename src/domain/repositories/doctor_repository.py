import uuid
from abc import ABC, abstractmethod

from src.domain.entities.doctor import Doctor


class DoctorRepository(ABC):
    @abstractmethod
    async def get_by_id(self, doctor_id: uuid.UUID) -> Doctor | None:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: uuid.UUID) -> Doctor | None:
        pass

    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 50) -> list[Doctor]:
        pass

    @abstractmethod
    async def save(self, doctor: Doctor) -> Doctor:
        pass
