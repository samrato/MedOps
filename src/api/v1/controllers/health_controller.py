from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_db
from src.api.schemas.common import APIResponse, HealthResponse
from src.infrastructure.cache.redis_client import redis_cache

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=APIResponse[HealthResponse])
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    redis_status = "healthy"
    try:
        if redis_cache._redis_client:
            await redis_cache._redis_client.ping()
        else:
            redis_status = "disabled"
    except Exception:
        redis_status = "unhealthy"

    status_str = "healthy" if db_status == "healthy" and redis_status in ("healthy", "disabled") else "degraded"

    health = HealthResponse(
        status=status_str,
        version="1.0.0",
        database=db_status,
        redis=redis_status,
    )
    return APIResponse(success=True, data=health)
