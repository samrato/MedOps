import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.entities.break_time import BreakTime
from src.domain.entities.holiday import Holiday
from src.domain.entities.working_hours import WorkingHours


@dataclass
class Doctor:
    id: uuid.UUID
    user_id: uuid.UUID
    specialty: str
    bio: str = ""
    slot_duration_minutes: int = 30
    working_hours: list[WorkingHours] = field(default_factory=list)
    holidays: list[Holiday] = field(default_factory=list)
    breaks: list[BreakTime] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    version: int = 1
