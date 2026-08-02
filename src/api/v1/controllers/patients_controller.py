import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.database import get_db
from src.api.schemas.appointment import AppointmentResponse
from src.api.schemas.common import APIResponse
from src.domain.entities.user import User
from src.domain.exceptions.domain_exceptions import ForbiddenException
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.repositories.sqlalchemy_appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from src.infrastructure.repositories.sqlalchemy_patient_repository import (
    SQLAlchemyPatientRepository,
)

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/{id}/appointments", response_model=APIResponse[list[AppointmentResponse]])
async def get_patient_appointments(
    id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    patient_repo = SQLAlchemyPatientRepository(db)
    patient = await patient_repo.get_by_id(id)
    if not patient:
        patient_by_user = await patient_repo.get_by_user_id(id)
        if patient_by_user:
            patient = patient_by_user
        else:
            return APIResponse(success=True, data=[])

    # Check permission (Patient can only view own appointments unless Admin or Doctor)
    if current_user.role == UserRole.PATIENT and patient.user_id != current_user.id:
        raise ForbiddenException("You cannot view appointments for another patient.")

    app_repo = SQLAlchemyAppointmentRepository(db)
    appointments = await app_repo.get_by_patient(patient.id, skip=skip, limit=limit)

    res = [
        AppointmentResponse(
            id=a.id,
            doctor_id=a.doctor_id,
            patient_id=a.patient_id,
            start_time=a.start_time,
            end_time=a.end_time,
            status=a.status,
            reason=a.reason,
            notes=a.notes,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in appointments
    ]
    return APIResponse(success=True, data=res)
