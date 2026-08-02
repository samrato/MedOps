import uuid

from fastapi import APIRouter, Depends, status

from src.api.dependencies.auth import get_current_user
from src.api.dependencies.services import get_appointment_service
from src.api.schemas.appointment import (
    AppointmentResponse,
    CancelAppointmentRequest,
    CreateAppointmentRequest,
    RescheduleAppointmentRequest,
)
from src.api.schemas.common import APIResponse
from src.application.commands.appointment_commands import (
    CancelAppointmentCommand,
    CreateAppointmentCommand,
    RescheduleAppointmentCommand,
)
from src.application.services.appointment_app_service import AppointmentApplicationService
from src.domain.entities.user import User

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=APIResponse[AppointmentResponse], status_code=status.HTTP_201_CREATED)
async def create_appointment(
    req: CreateAppointmentRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentApplicationService = Depends(get_appointment_service),
):
    cmd = CreateAppointmentCommand(
        doctor_id=req.doctor_id,
        patient_id=req.patient_id,
        start_time=req.start_time,
        end_time=req.end_time,
        reason=req.reason,
    )
    appointment_dto = await service.create_appointment(cmd)
    resp = AppointmentResponse(
        id=appointment_dto.id,
        doctor_id=appointment_dto.doctor_id,
        patient_id=appointment_dto.patient_id,
        start_time=appointment_dto.start_time,
        end_time=appointment_dto.end_time,
        status=appointment_dto.status,
        reason=appointment_dto.reason,
        notes=appointment_dto.notes,
        created_at=appointment_dto.created_at,
        updated_at=appointment_dto.updated_at,
    )
    return APIResponse(success=True, data=resp)


@router.patch("/{id}/cancel", response_model=APIResponse[AppointmentResponse])
async def cancel_appointment(
    id: uuid.UUID,
    req: CancelAppointmentRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentApplicationService = Depends(get_appointment_service),
):
    cmd = CancelAppointmentCommand(
        appointment_id=id,
        actor_id=current_user.id,
        reason=req.reason,
    )
    appointment_dto = await service.cancel_appointment(cmd)
    resp = AppointmentResponse(
        id=appointment_dto.id,
        doctor_id=appointment_dto.doctor_id,
        patient_id=appointment_dto.patient_id,
        start_time=appointment_dto.start_time,
        end_time=appointment_dto.end_time,
        status=appointment_dto.status,
        reason=appointment_dto.reason,
        notes=appointment_dto.notes,
        created_at=appointment_dto.created_at,
        updated_at=appointment_dto.updated_at,
    )
    return APIResponse(success=True, data=resp)


@router.patch("/{id}/reschedule", response_model=APIResponse[AppointmentResponse])
async def reschedule_appointment(
    id: uuid.UUID,
    req: RescheduleAppointmentRequest,
    current_user: User = Depends(get_current_user),
    service: AppointmentApplicationService = Depends(get_appointment_service),
):
    cmd = RescheduleAppointmentCommand(
        appointment_id=id,
        actor_id=current_user.id,
        new_start_time=req.new_start_time,
        new_end_time=req.new_end_time,
    )
    appointment_dto = await service.reschedule_appointment(cmd)
    resp = AppointmentResponse(
        id=appointment_dto.id,
        doctor_id=appointment_dto.doctor_id,
        patient_id=appointment_dto.patient_id,
        start_time=appointment_dto.start_time,
        end_time=appointment_dto.end_time,
        status=appointment_dto.status,
        reason=appointment_dto.reason,
        notes=appointment_dto.notes,
        created_at=appointment_dto.created_at,
        updated_at=appointment_dto.updated_at,
    )
    return APIResponse(success=True, data=resp)
