from dataclasses import dataclass

from src.domain.value_objects.user_role import UserRole


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    full_name: str
    role: UserRole
    specialty: str | None = None  # if doctor
    phone_number: str | None = None  # if patient


@dataclass(frozen=True)
class LoginUserCommand:
    email: str
    password: str
