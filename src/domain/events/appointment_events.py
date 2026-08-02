import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AppointmentBookedEvent(DomainEvent):
    appointment_id: uuid.UUID = field(default_factory=uuid.uuid4)
    doctor_id: uuid.UUID = field(default_factory=uuid.uuid4)
    patient_id: uuid.UUID = field(default_factory=uuid.uuid4)
    start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    end_time: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class AppointmentCancelledEvent(DomainEvent):
    appointment_id: uuid.UUID = field(default_factory=uuid.uuid4)
    doctor_id: uuid.UUID = field(default_factory=uuid.uuid4)
    patient_id: uuid.UUID = field(default_factory=uuid.uuid4)
    reason: str = ""


@dataclass
class AppointmentRescheduledEvent(DomainEvent):
    appointment_id: uuid.UUID = field(default_factory=uuid.uuid4)
    doctor_id: uuid.UUID = field(default_factory=uuid.uuid4)
    patient_id: uuid.UUID = field(default_factory=uuid.uuid4)
    new_start_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    new_end_time: datetime = field(default_factory=lambda: datetime.now(UTC))
