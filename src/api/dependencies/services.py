from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.application.services.appointment_app_service import AppointmentApplicationService
from src.application.services.availability_engine import AvailabilityEngine
from src.application.services.notification_service import NotificationService
from src.infrastructure.repositories.sqlalchemy_appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from src.infrastructure.repositories.sqlalchemy_audit_log_repository import (
    SQLAlchemyAuditLogRepository,
)
from src.infrastructure.repositories.sqlalchemy_doctor_repository import SQLAlchemyDoctorRepository
from src.infrastructure.repositories.sqlalchemy_patient_repository import (
    SQLAlchemyPatientRepository,
)


def get_appointment_service(db: AsyncSession = Depends(get_db)) -> AppointmentApplicationService:
    appointment_repo = SQLAlchemyAppointmentRepository(db)
    doctor_repo = SQLAlchemyDoctorRepository(db)
    patient_repo = SQLAlchemyPatientRepository(db)
    audit_repo = SQLAlchemyAuditLogRepository(db)
    notification_service = NotificationService()
    return AppointmentApplicationService(
        appointment_repo=appointment_repo,
        doctor_repo=doctor_repo,
        patient_repo=patient_repo,
        audit_log_repo=audit_repo,
        notification_service=notification_service,
    )


def get_availability_engine(db: AsyncSession = Depends(get_db)) -> AvailabilityEngine:
    doctor_repo = SQLAlchemyDoctorRepository(db)
    appointment_repo = SQLAlchemyAppointmentRepository(db)
    return AvailabilityEngine(doctor_repo=doctor_repo, appointment_repo=appointment_repo)
