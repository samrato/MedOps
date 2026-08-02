import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.patient import Patient
from src.domain.repositories.patient_repository import PatientRepository
from src.infrastructure.database.models import PatientModel


class SQLAlchemyPatientRepository(PatientRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_entity(self, model: PatientModel) -> Patient:
        return Patient(
            id=model.id,
            user_id=model.user_id,
            phone_number=model.phone_number,
            date_of_birth=model.date_of_birth,
            medical_history_summary=model.medical_history_summary,
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )

    async def get_by_id(self, patient_id: uuid.UUID) -> Patient | None:
        model = await self._session.get(PatientModel, patient_id)
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: uuid.UUID) -> Patient | None:
        stmt = select(PatientModel).where(PatientModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, patient: Patient) -> Patient:
        model = await self._session.get(PatientModel, patient.id)
        if not model:
            model = PatientModel(
                id=patient.id,
                user_id=patient.user_id,
                phone_number=patient.phone_number,
                date_of_birth=patient.date_of_birth,
                medical_history_summary=patient.medical_history_summary,
            )
            self._session.add(model)
        else:
            model.phone_number = patient.phone_number
            model.date_of_birth = patient.date_of_birth
            model.medical_history_summary = patient.medical_history_summary
            model.version += 1

        await self._session.flush()
        return self._to_entity(model)
