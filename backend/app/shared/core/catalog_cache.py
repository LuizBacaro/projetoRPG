"""Simple in-memory cache for read-heavy catalog endpoints."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Any, Callable


class CatalogCache:
    """Thread-safe TTL cache with namespace invalidation support."""

    def __init__(self, max_entries: int = 512) -> None:
        self._max_entries = max_entries
        self._values: "OrderedDict[str, tuple[float, Any]]" = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: str) -> Any:
        now = time.time()
        with self._lock:
            item = self._values.get(key)
            if not item:
                return None

            expires_at, value = item
            if expires_at <= now:
                self._values.pop(key, None)
                return None

            self._values.move_to_end(key)
            return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        expires_at = time.time() + ttl_seconds
        with self._lock:
            self._values[key] = (expires_at, value)
            self._values.move_to_end(key)
            self._evict_if_needed_locked()

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl_seconds: int) -> Any:
        cached = self.get(key)
        if cached is not None:
            return cached

        value = factory()
        self.set(key, value, ttl_seconds)
        return value

    def invalidate_prefix(self, prefix: str) -> int:
        removed = 0
        with self._lock:
            keys = [key for key in self._values.keys() if key.startswith(prefix)]
            for key in keys:
                self._values.pop(key, None)
                removed += 1
        return removed

    def clear(self) -> None:
        with self._lock:
            self._values.clear()

    def _evict_if_needed_locked(self) -> None:
        now = time.time()
        expired_keys = [
            key for key, (expires_at, _) in self._values.items() if expires_at <= now
        ]
        for key in expired_keys:
            self._values.pop(key, None)

        while len(self._values) > self._max_entries:
            self._values.popitem(last=False)


def make_cache_key(namespace: str, **parts: Any) -> str:
    ordered = sorted(parts.items(), key=lambda item: item[0])
    params = "|".join(f"{key}={value}" for key, value in ordered)
    return f"{namespace}:{params}"


catalog_cache = CatalogCache()
