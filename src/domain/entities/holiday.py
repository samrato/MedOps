import uuid
from dataclasses import dataclass
from datetime import date


@dataclass
class Holiday:
    id: uuid.UUID
    doctor_id: uuid.UUID
    date: date
    description: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = uuid.uuid4()
