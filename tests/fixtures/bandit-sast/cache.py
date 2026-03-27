"""
Caching layer for the inventory service.

Wraps Redis with automatic serialisation so callers can
store arbitrary Python objects without worrying about encoding.
"""

import logging
import pickle
import time
from typing import Any

import redis

from config import get_config

logger = logging.getLogger(__name__)


class CacheBackend:
    """Thin wrapper around Redis that handles object serialisation."""

    def __init__(self):
        cfg = get_config()
        self._client = redis.from_url(cfg.REDIS_URL)
        self._default_ttl = cfg.CACHE_TTL
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """
        Retrieve a cached object by key.

        Returns None on cache miss. Automatically deserialises
        the stored bytes back into the original Python object.
        """
        raw = self._client.get(key)
        if raw is None:
            self._misses += 1
            return None
        self._hits += 1
        return pickle.loads(raw)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Store an object in the cache with an optional TTL override."""
        ttl = ttl or self._default_ttl
        data = pickle.dumps(value)
        self._client.setex(key, ttl, data)

    def delete(self, key: str) -> None:
        """Remove a single key from the cache."""
        self._client.delete(key)

    def flush_all(self) -> None:
        """Clear the entire cache. Use with caution."""
        self._client.flushdb()
        logger.info("Cache flushed")

    def stats(self) -> dict:
        """Return hit/miss counters for monitoring."""
        total = self._hits + self._misses
        ratio = self._hits / total if total else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": round(ratio, 3),
            "timestamp": int(time.time()),
        }


# Module-level singleton so Flask routes can import directly.
cache = CacheBackend()
