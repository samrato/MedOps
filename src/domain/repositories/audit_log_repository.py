from abc import ABC, abstractmethod

from src.domain.entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    @abstractmethod
    async def save(self, audit_log: AuditLog) -> AuditLog:
        pass
