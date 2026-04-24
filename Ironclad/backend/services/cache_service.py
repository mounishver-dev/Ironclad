"""
cache_service.py — In-Memory Asset Cache
Reduces Firestore reads on every /check call by caching the asset list.
Cache is invalidated whenever a new asset is uploaded.
Uses a simple time-based TTL (5 minutes default).
"""

import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ── Cache state ───────────────────────────────────────────────────────────────

_cache: dict = {
    "assets": None,       # List[dict] or None
    "timestamp": 0.0,     # Unix timestamp of last cache fill
    "hit_count": 0,       # Diagnostic counter
    "miss_count": 0,
}

CACHE_TTL_SECONDS = 300   # 5 minutes


# ── Public API ────────────────────────────────────────────────────────────────

def get_cached_assets() -> Optional[list]:
    """
    Return cached asset list if fresh, else None (caller should re-query Firestore).
    """
    if _cache["assets"] is None:
        _cache["miss_count"] += 1
        return None

    age = time.time() - _cache["timestamp"]
    if age > CACHE_TTL_SECONDS:
        logger.info(f"Cache expired (age={age:.0f}s). Forcing refresh.")
        _cache["assets"] = None
        _cache["miss_count"] += 1
        return None

    _cache["hit_count"] += 1
    logger.debug(f"Cache hit (age={age:.0f}s, {len(_cache['assets'])} assets)")
    return _cache["assets"]


def set_cached_assets(assets: list) -> None:
    """Store a fresh asset list in the cache."""
    _cache["assets"] = assets
    _cache["timestamp"] = time.time()
    logger.info(f"Cache updated with {len(assets)} assets.")


def invalidate_cache() -> None:
    """Force cache invalidation — call this after every upload."""
    _cache["assets"] = None
    _cache["timestamp"] = 0.0
    logger.info("Asset cache invalidated.")


def get_cache_stats() -> dict:
    """Return diagnostic info about cache performance."""
    total = _cache["hit_count"] + _cache["miss_count"]
    hit_rate = (_cache["hit_count"] / total * 100) if total > 0 else 0
    return {
        "hit_count": _cache["hit_count"],
        "miss_count": _cache["miss_count"],
        "hit_rate_pct": round(hit_rate, 1),
        "cached_assets": len(_cache["assets"]) if _cache["assets"] else 0,
        "cache_age_seconds": round(time.time() - _cache["timestamp"], 1) if _cache["timestamp"] else None,
        "ttl_seconds": CACHE_TTL_SECONDS,
    }
