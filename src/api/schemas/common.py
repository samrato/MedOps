from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str = Field(..., json_schema_extra={"example": "SLOT_ALREADY_BOOKED"})
    message: str = Field(..., json_schema_extra={"example": "Selected slot has already been booked."})


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    error: ErrorDetail | None = None


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"
