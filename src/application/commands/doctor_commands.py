import uuid
from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class CreateWorkingHoursCommand:
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int = 30


@dataclass(frozen=True)
class CreateHolidayCommand:
    doctor_id: uuid.UUID
    holiday_date: date
    description: str = ""


@dataclass(frozen=True)
class CreateBreakTimeCommand:
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time
    description: str = "Break"
