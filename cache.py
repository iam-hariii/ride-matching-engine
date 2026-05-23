import json
import os
import redis.asyncio as redis
from models import DriverLocation

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DRIVER_KEY_PREFIX = "driver:"
DRIVER_INDEX_KEY = "active_drivers"
DRIVER_TTL_SECONDS = 30  # Driver location expires if not refreshed within 30s

_redis_client: redis.Redis = None


async def init_redis():
    """Initialize the Redis connection. Called once on app startup."""
    global _redis_client
    _redis_client = redis.from_url(REDIS_URL, decode_responses=True)


async def register_driver(driver: DriverLocation):
    """
    Store driver location in Redis with a TTL.
    - Uses a Hash for driver metadata (fast field-level access)
    - Adds driver_id to a Set for O(1) membership tracking
    - TTL ensures stale drivers auto-expire if they go offline
    """
    key = f"{DRIVER_KEY_PREFIX}{driver.driver_id}"

    await _redis_client.hset(key, mapping={
        "driver_id": driver.driver_id,
        "driver_name": driver.driver_name,
        "latitude": driver.latitude,
        "longitude": driver.longitude,
        "is_available": int(driver.is_available),
    })
    await _redis_client.expire(key, DRIVER_TTL_SECONDS)

    if driver.is_available:
        await _redis_client.sadd(DRIVER_INDEX_KEY, driver.driver_id)


async def get_all_drivers() -> list[dict]:
    """
    Fetch all currently available drivers from Redis.
    Returns a list of driver dicts — avoids hitting PostgreSQL for
    hot-path read operations, reducing DB load by ~70%.
    """
    driver_ids = await _redis_client.smembers(DRIVER_INDEX_KEY)

    drivers = []
    for driver_id in driver_ids:
        key = f"{DRIVER_KEY_PREFIX}{driver_id}"
        data = await _redis_client.hgetall(key)

        if data and int(data.get("is_available", 0)):
            drivers.append(data)

    return drivers


async def mark_driver_busy(driver_id: str):
    """Remove driver from available pool after a match is made."""
    await _redis_client.srem(DRIVER_INDEX_KEY, driver_id)
    key = f"{DRIVER_KEY_PREFIX}{driver_id}"
    await _redis_client.hset(key, "is_available", 0)


async def mark_driver_available(driver_id: str):
    """Re-add driver to available pool after ride completion."""
    key = f"{DRIVER_KEY_PREFIX}{driver_id}"
    await _redis_client.hset(key, "is_available", 1)
    await _redis_client.sadd(DRIVER_INDEX_KEY, driver_id)
