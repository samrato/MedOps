import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Patient:
    id: uuid.UUID
    user_id: uuid.UUID
    phone_number: str = ""
    date_of_birth: datetime | None = None
    medical_history_summary: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
