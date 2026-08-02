from pydantic import BaseModel, EmailStr, Field

from src.domain.value_objects.user_role import UserRole


class RegisterUserRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "patient@example.com"})
    password: str = Field(..., min_length=8, json_schema_extra={"example": "SecureP@ssw0rd123!"})
    full_name: str = Field(..., json_schema_extra={"example": "John Doe"})
    role: UserRole = Field(..., json_schema_extra={"example": UserRole.PATIENT})
    specialty: str | None = Field(None, json_schema_extra={"example": "Cardiology"})
    phone_number: str | None = Field(None, json_schema_extra={"example": "+1234567890"})


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., json_schema_extra={"example": "patient@example.com"})
    password: str = Field(..., json_schema_extra={"example": "SecureP@ssw0rd123!"})


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str
