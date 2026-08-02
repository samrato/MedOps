import json
from typing import Any

import redis.asyncio as redis

from src.infrastructure.config.settings import settings
from src.infrastructure.logging.logger import logger


class RedisCache:
    def __init__(self) -> None:
        self._redis_client: redis.Redis | None = None

    async def connect(self) -> None:
        try:
            self._redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
            await self._redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.warning("Failed to connect to Redis cache. Running with cache bypass.", error=str(e))
            self._redis_client = None

    async def close(self) -> None:
        if self._redis_client:
            await self._redis_client.close()

    async def get_json(self, key: str) -> Any | None:
        if not self._redis_client:
            return None
        try:
            val = await self._redis_client.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logger.warning("Redis get_json error", key=key, error=str(e))
        return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if not self._redis_client:
            return
        try:
            serialized = json.dumps(value, default=str)
            await self._redis_client.set(key, serialized, ex=ttl_seconds)
        except Exception as e:
            logger.warning("Redis set_json error", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        if not self._redis_client:
            return
        try:
            await self._redis_client.delete(key)
        except Exception as e:
            logger.warning("Redis delete error", key=key, error=str(e))

    async def delete_pattern(self, pattern: str) -> None:
        if not self._redis_client:
            return
        try:
            keys = await self._redis_client.keys(pattern)
            if keys:
                await self._redis_client.delete(*keys)
        except Exception as e:
            logger.warning("Redis delete_pattern error", pattern=pattern, error=str(e))


redis_cache = RedisCache()
