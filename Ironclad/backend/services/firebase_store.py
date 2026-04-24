"""
firebase_store.py — Firestore Asset Store (v2)
Upgraded schema stores multi-hash DNA, file metadata, and timestamps.
Backwards compatible with legacy single-hash records.
"""

import time
import logging
from services.firebase_config import db_firestore
from services.cache_service import invalidate_cache

logger = logging.getLogger(__name__)

COLLECTION = "assets_v2"
LEGACY_COLLECTION = "images"   # Keep reading from old collection for BC


# ── Write ─────────────────────────────────────────────────────────────────────

def save_asset(
    filename: str,
    dna: dict,          # {"phash": "...", "dhash": "...", "ahash": "...", "whash": "..."}
    cloudinary_url: str,
    file_type: str = "image",
    file_size: int = 0,
    mime_type: str = "image/jpeg",
) -> str:
    """
    Save a new protected asset to Firestore with full DNA metadata.
    Returns the document ID.
    """
    # Use a clean document ID (no special chars)
    doc_id = _sanitise_doc_id(filename)
    doc_ref = db_firestore.collection(COLLECTION).document(doc_id)

    doc_ref.set({
        "filename": filename,
        "doc_id": doc_id,
        "phash": dna.get("phash", ""),
        "dhash": dna.get("dhash", ""),
        "ahash": dna.get("ahash", ""),
        "whash": dna.get("whash", ""),
        "path": cloudinary_url,
        "file_type": file_type,
        "file_size": file_size,
        "mime_type": mime_type,
        "upload_timestamp": time.time(),
        "upload_date": _timestamp_to_iso(),
        "schema_version": 2,
    })

    invalidate_cache()
    logger.info(f"Asset saved: {doc_id}")
    return doc_id


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_assets() -> list:
    """
    Retrieve all assets from Firestore (v2 + legacy).
    Returns a list of dicts, each with DNA fields.
    """
    assets = []

    # Read v2 assets
    for doc in db_firestore.collection(COLLECTION).stream():
        d = doc.to_dict()
        # Normalise to ensure DNA dict exists
        d.setdefault("dhash", d.get("phash", ""))
        d.setdefault("ahash", d.get("phash", ""))
        d.setdefault("whash", d.get("phash", ""))
        d.setdefault("file_type", "image")
        d.setdefault("schema_version", 2)
        assets.append(d)

    # Read legacy assets and backfill missing fields
    for doc in db_firestore.collection(LEGACY_COLLECTION).stream():
        d = doc.to_dict()
        legacy = {
            "filename": d.get("filename", "unknown"),
            "phash": d.get("hash", ""),
            "dhash": d.get("hash", ""),
            "ahash": d.get("hash", ""),
            "whash": d.get("hash", ""),
            "path": d.get("path", ""),
            "file_type": "image",
            "schema_version": 1,
        }
        assets.append(legacy)

    logger.info(f"Fetched {len(assets)} total assets from Firestore")
    return assets


def get_asset_count() -> int:
    """Fast count of protected assets."""
    v2 = len(list(db_firestore.collection(COLLECTION).stream()))
    legacy = len(list(db_firestore.collection(LEGACY_COLLECTION).stream()))
    return v2 + legacy


# ── Legacy compatibility ───────────────────────────────────────────────────────

def save_image_data(filename: str, hash_value: str, path: str) -> None:
    """Legacy function — kept for backwards compatibility."""
    save_asset(
        filename=filename,
        dna={"phash": hash_value, "dhash": hash_value, "ahash": hash_value, "whash": hash_value},
        cloudinary_url=path,
    )


def get_all_images() -> list:
    """Legacy function — returns all assets in old format."""
    assets = get_all_assets()
    return [
        {"filename": a.get("filename"), "hash": a.get("phash"), "path": a.get("path")}
        for a in assets
    ]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sanitise_doc_id(filename: str) -> str:
    """Convert filename to a safe Firestore document ID."""
    import re
    base = filename.rsplit(".", 1)[0] if "." in filename else filename
    return re.sub(r"[^\w\-]", "_", base)[:100]


def _timestamp_to_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()