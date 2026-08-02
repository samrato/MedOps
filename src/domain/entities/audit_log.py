import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AuditLog:
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    entity_name: str
    entity_id: uuid.UUID | None
    details: str = ""
    ip_address: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
