import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.value_objects.user_role import UserRole


@dataclass
class User:
    id: uuid.UUID
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
