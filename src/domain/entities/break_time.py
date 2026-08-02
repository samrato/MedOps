import uuid
from dataclasses import dataclass
from datetime import time


@dataclass
class BreakTime:
    id: uuid.UUID
    doctor_id: uuid.UUID
    day_of_week: int  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time
    description: str = "Lunch/Rest Break"

    def __post_init__(self) -> None:
        if not (0 <= self.day_of_week <= 6):
            raise ValueError("day_of_week must be between 0 and 6.")
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be strictly before end_time.")
