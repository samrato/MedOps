from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class TimeSlot:
    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be strictly before end time.")

    def overlaps(self, other: "TimeSlot") -> bool:
        """
        Check if this time slot overlaps with another.
        Overlaps if start_time < other.end_time AND end_time > other.start_time.
        """
        return self.start_time < other.end_time and self.end_time > other.start_time

    def is_in_past(self, reference_time: datetime | None = None) -> bool:
        now = reference_time or datetime.now(UTC)
        start = self.start_time if self.start_time.tzinfo else self.start_time.replace(tzinfo=UTC)
        return start < now

    def contains(self, dt: datetime) -> bool:
        return self.start_time <= dt < self.end_time

    def duration_minutes(self) -> int:
        return int((self.end_time - self.start_time).total_seconds() // 60)
