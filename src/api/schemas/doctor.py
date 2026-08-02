import datetime as dt
import uuid

from pydantic import BaseModel, Field


class WorkingHoursRequest(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, json_schema_extra={"example": 0}, description="0=Monday, 6=Sunday")
    start_time: dt.time = Field(..., json_schema_extra={"example": "09:00:00"})
    end_time: dt.time = Field(..., json_schema_extra={"example": "17:00:00"})
    slot_duration_minutes: int = Field(30, ge=5, le=120, json_schema_extra={"example": 30})


class HolidayRequest(BaseModel):
    date: dt.date = Field(..., json_schema_extra={"example": "2026-12-25"})
    description: str = Field("", json_schema_extra={"example": "Christmas Holiday"})


class BreakTimeRequest(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6, json_schema_extra={"example": 0})
    start_time: dt.time = Field(..., json_schema_extra={"example": "12:00:00"})
    end_time: dt.time = Field(..., json_schema_extra={"example": "13:00:00"})
    description: str = Field("Lunch Break", json_schema_extra={"example": "Lunch Break"})


class DoctorResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    specialty: str
    bio: str
    slot_duration_minutes: int


class SlotResponse(BaseModel):
    start_time: str
    end_time: str
    is_available: bool
    reason_unavailable: str | None = None


class AvailabilityResponse(BaseModel):
    doctor_id: uuid.UUID
    date: str
    slot_duration_minutes: int
    slots: list[SlotResponse]
