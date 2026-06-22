"""
services/cache.py — Redis-backed response caching
Caches full analysis responses keyed by URL (SHA-256).
TTL default: 6 hours.
"""
import json
import hashlib
from loguru import logger

try:
    import redis.asyncio as aioredis
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False

from config import get_settings

settings  = get_settings()
_client   = None
CACHE_TTL = 60 * 60 * 6   # 6 hours


async def _get_client():
    global _client
    if _client is None and _REDIS_AVAILABLE:
        try:
            _client = aioredis.from_url(settings.redis_url, decode_responses=True)
            await _client.ping()
            logger.info("Redis connected")
        except Exception as exc:
            logger.warning(f"Redis unavailable — caching disabled: {exc}")
            _client = None
    return _client


def _cache_key(url: str) -> str:
    return "truthlens:v1:" + hashlib.sha256(url.encode()).hexdigest()


async def get_cached(url: str) -> dict | None:
    client = await _get_client()
    if not client:
        return None
    try:
        raw = await client.get(_cache_key(url))
        if raw:
            logger.info(f"Cache HIT for {url[:60]}")
            return json.loads(raw)
    except Exception as exc:
        logger.warning(f"Cache get error: {exc}")
    return None


async def set_cached(url: str, data: dict, ttl: int = CACHE_TTL) -> None:
    client = await _get_client()
    if not client:
        return
    try:
        await client.setex(_cache_key(url), ttl, json.dumps(data))
        logger.info(f"Cache SET for {url[:60]} (TTL {ttl}s)")
    except Exception as exc:
        logger.warning(f"Cache set error: {exc}")


async def invalidate(url: str) -> None:
    client = await _get_client()
    if not client:
        return
    try:
        await client.delete(_cache_key(url))
    except Exception as exc:
        logger.warning(f"Cache delete error: {exc}")
