import uuid
from datetime import datetime

from pydantic import BaseModel


class PatientResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    phone_number: str
    date_of_birth: datetime | None
    medical_history_summary: str
