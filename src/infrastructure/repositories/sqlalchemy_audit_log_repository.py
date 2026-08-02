from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.audit_log import AuditLog
from src.domain.repositories.audit_log_repository import AuditLogRepository
from src.infrastructure.database.models import AuditLogModel


class SQLAlchemyAuditLogRepository(AuditLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, audit_log: AuditLog) -> AuditLog:
        model = AuditLogModel(
            id=audit_log.id,
            actor_id=audit_log.actor_id,
            action=audit_log.action,
            entity_name=audit_log.entity_name,
            entity_id=audit_log.entity_id,
            details=audit_log.details,
            ip_address=audit_log.ip_address,
            timestamp=audit_log.timestamp,
        )
        self._session.add(model)
        await self._session.flush()
        return audit_log
