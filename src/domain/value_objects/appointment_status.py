from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    NO_SHOW = "NO_SHOW"

    def is_active(self) -> bool:
        return self in (AppointmentStatus.SCHEDULED, AppointmentStatus.RESCHEDULED)
