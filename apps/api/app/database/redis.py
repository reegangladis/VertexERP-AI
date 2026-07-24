import logging

import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure the Redis client
redis_client = redis.from_url(
    settings.redis_url, encoding="utf-8", decode_responses=True
)


async def check_redis_health() -> bool:
    """Verifies connection to the Redis server by issuing a PING command."""
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis healthcheck failed: {e}")
        return False
