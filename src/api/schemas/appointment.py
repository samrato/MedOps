import datetime as dt
import uuid

from pydantic import BaseModel, Field

from src.domain.value_objects.appointment_status import AppointmentStatus


class CreateAppointmentRequest(BaseModel):
    doctor_id: uuid.UUID = Field(..., json_schema_extra={"example": "a0000000-0000-0000-0000-000000000001"})
    patient_id: uuid.UUID = Field(..., json_schema_extra={"example": "b0000000-0000-0000-0000-000000000001"})
    start_time: dt.datetime = Field(..., json_schema_extra={"example": "2026-08-10T09:00:00Z"})
    end_time: dt.datetime = Field(..., json_schema_extra={"example": "2026-08-10T09:30:00Z"})
    reason: str = Field("", json_schema_extra={"example": "Annual General Checkup"})


class CancelAppointmentRequest(BaseModel):
    reason: str = Field("", json_schema_extra={"example": "Schedule conflict"})


class RescheduleAppointmentRequest(BaseModel):
    new_start_time: dt.datetime = Field(..., json_schema_extra={"example": "2026-08-10T10:00:00Z"})
    new_end_time: dt.datetime = Field(..., json_schema_extra={"example": "2026-08-10T10:30:00Z"})


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    patient_id: uuid.UUID
    start_time: dt.datetime
    end_time: dt.datetime
    status: AppointmentStatus
    reason: str
    notes: str
    created_at: dt.datetime
    updated_at: dt.datetime
