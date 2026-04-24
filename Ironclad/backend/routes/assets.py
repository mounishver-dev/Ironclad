"""
assets.py — Asset Registry Endpoints
List, count, and inspect all registered protected assets.
"""

import logging
from fastapi import APIRouter, HTTPException

from services.firebase_store import get_all_assets, get_asset_count
from services.cache_service import get_cached_assets, set_cached_assets, get_cache_stats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_assets():
    """Return all registered protected assets with their metadata."""
    try:
        assets = get_cached_assets()
        if assets is None:
            assets = get_all_assets()
            set_cached_assets(assets)

        # Return a clean, UI-friendly list (omit raw hash strings for brevity)
        summary = []
        for a in assets:
            summary.append({
                "filename": a.get("filename"),
                "file_type": a.get("file_type", "image"),
                "mime_type": a.get("mime_type", "image/jpeg"),
                "asset_url": a.get("path", ""),
                "upload_date": a.get("upload_date", ""),
                "file_size_bytes": a.get("file_size", 0),
                "schema_version": a.get("schema_version", 1),
                "has_multi_hash": bool(a.get("dhash")),
            })

        return {
            "total": len(summary),
            "assets": summary,
            "cache": get_cache_stats(),
        }

    except Exception as e:
        logger.error(f"List assets error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count")
async def asset_count():
    """Fast endpoint to return just the number of protected assets."""
    try:
        count = get_asset_count()
        return {"total_protected_assets": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
