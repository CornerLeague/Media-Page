"""Redis service for caching and job queues."""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List, Union
import redis.asyncio as redis
from redis.asyncio import Redis
import logging

from ..core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RedisService:
    """Redis service for caching and job management."""

    def __init__(self):
        self.redis: Optional[Redis] = None
        self.connection_pool = None

    async def connect(self):
        """Connect to Redis."""
        try:
            # Build connection kwargs, excluding ssl if False to avoid compatibility issues
            connection_kwargs = {
                'decode_responses': True,
                'encoding': 'utf-8',
                'db': settings.REDIS_DB,
                'retry_on_timeout': True,
                'health_check_interval': 30
            }

            if settings.REDIS_PASSWORD:
                connection_kwargs['password'] = settings.REDIS_PASSWORD

            if settings.REDIS_SSL:
                connection_kwargs['ssl'] = settings.REDIS_SSL

            self.connection_pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                **connection_kwargs
            )

            self.redis = Redis(connection_pool=self.connection_pool)

            # Test connection
            await self.redis.ping()
            logger.info("Successfully connected to Redis")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def health_check(self) -> bool:
        """Check Redis health."""
        try:
            if not self.redis:
                return False
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            return False

    # Cache methods
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        try:
            if not self.redis:
                return None
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional expiration."""
        try:
            if not self.redis:
                return False
            await self.redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if not self.redis:
                return False
            result = await self.redis.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            if not self.redis:
                return False
            result = await self.redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {str(e)}")
            return False

    # JSON cache methods
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from cache."""
        try:
            value = await self.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Redis GET_JSON error for key {key}: {str(e)}")
            return None

    async def set_json(
        self,
        key: str,
        value: Dict[str, Any],
        expire: Optional[int] = None
    ) -> bool:
        """Set JSON value in cache."""
        try:
            json_str = json.dumps(value, default=str)
            return await self.set(key, json_str, expire)
        except Exception as e:
            logger.error(f"Redis SET_JSON error for key {key}: {str(e)}")
            return False

    # List operations
    async def lpush(self, key: str, *values: str) -> int:
        """Push values to the left of a list."""
        try:
            if not self.redis:
                return 0
            return await self.redis.lpush(key, *values)
        except Exception as e:
            logger.error(f"Redis LPUSH error for key {key}: {str(e)}")
            return 0

    async def rpop(self, key: str) -> Optional[str]:
        """Pop value from the right of a list."""
        try:
            if not self.redis:
                return None
            return await self.redis.rpop(key)
        except Exception as e:
            logger.error(f"Redis RPOP error for key {key}: {str(e)}")
            return None

    async def llen(self, key: str) -> int:
        """Get length of a list."""
        try:
            if not self.redis:
                return 0
            return await self.redis.llen(key)
        except Exception as e:
            logger.error(f"Redis LLEN error for key {key}: {str(e)}")
            return 0

    # Set operations
    async def sadd(self, key: str, *values: str) -> int:
        """Add values to a set."""
        try:
            if not self.redis:
                return 0
            return await self.redis.sadd(key, *values)
        except Exception as e:
            logger.error(f"Redis SADD error for key {key}: {str(e)}")
            return 0

    async def srem(self, key: str, *values: str) -> int:
        """Remove values from a set."""
        try:
            if not self.redis:
                return 0
            return await self.redis.srem(key, *values)
        except Exception as e:
            logger.error(f"Redis SREM error for key {key}: {str(e)}")
            return 0

    async def smembers(self, key: str) -> set:
        """Get all members of a set."""
        try:
            if not self.redis:
                return set()
            return await self.redis.smembers(key)
        except Exception as e:
            logger.error(f"Redis SMEMBERS error for key {key}: {str(e)}")
            return set()

    # Hash operations
    async def hset(self, key: str, field: str, value: str) -> int:
        """Set field in hash."""
        try:
            if not self.redis:
                return 0
            return await self.redis.hset(key, field, value)
        except Exception as e:
            logger.error(f"Redis HSET error for key {key}: {str(e)}")
            return 0

    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get field from hash."""
        try:
            if not self.redis:
                return None
            return await self.redis.hget(key, field)
        except Exception as e:
            logger.error(f"Redis HGET error for key {key}: {str(e)}")
            return None

    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all fields from hash."""
        try:
            if not self.redis:
                return {}
            return await self.redis.hgetall(key)
        except Exception as e:
            logger.error(f"Redis HGETALL error for key {key}: {str(e)}")
            return {}

    # User-specific cache methods
    async def cache_user_data(
        self,
        user_id: str,
        data: Dict[str, Any],
        expire: int = 3600
    ) -> bool:
        """Cache user data."""
        key = f"user:{user_id}"
        return await self.set_json(key, data, expire)

    async def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user data."""
        key = f"user:{user_id}"
        return await self.get_json(key)

    async def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate user cache."""
        key = f"user:{user_id}"
        return await self.delete(key)

    # Team-specific cache methods
    async def cache_team_data(
        self,
        team_id: str,
        data: Dict[str, Any],
        expire: int = 7200
    ) -> bool:
        """Cache team data."""
        key = f"team:{team_id}"
        return await self.set_json(key, data, expire)

    async def get_team_data(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get cached team data."""
        key = f"team:{team_id}"
        return await self.get_json(key)

    # Job queue methods (simple implementation)
    async def enqueue_job(
        self,
        queue_name: str,
        job_data: Dict[str, Any]
    ) -> bool:
        """Enqueue a job."""
        job_json = json.dumps(job_data, default=str)
        queue_key = f"queue:{queue_name}"
        return await self.lpush(queue_key, job_json) > 0

    async def dequeue_job(self, queue_name: str) -> Optional[Dict[str, Any]]:
        """Dequeue a job."""
        queue_key = f"queue:{queue_name}"
        job_json = await self.rpop(queue_key)
        if job_json:
            try:
                return json.loads(job_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in queue {queue_name}: {job_json}")
        return None

    async def get_queue_size(self, queue_name: str) -> int:
        """Get queue size."""
        queue_key = f"queue:{queue_name}"
        return await self.llen(queue_key)


# Global Redis service instance
_redis_service: Optional[RedisService] = None


async def get_redis_service() -> RedisService:
    """Get Redis service instance."""
    global _redis_service

    if _redis_service is None:
        _redis_service = RedisService()
        await _redis_service.connect()

    return _redis_service


async def close_redis_service():
    """Close Redis service."""
    global _redis_service

    if _redis_service:
        await _redis_service.disconnect()
        _redis_service = None