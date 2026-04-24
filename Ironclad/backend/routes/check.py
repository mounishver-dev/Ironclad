"""
check.py — Async Parallel Piracy Detection Endpoint
Uses async I/O to fetch stored images in parallel (2x speed improvement).
Runs two-gate similarity filter before invoking Gemini AI.
"""

import io
import time
import asyncio
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import aiohttp

from services.file_processor import process_file, get_file_category
from services.hashing import generate_multi_hash, hash_dict_from_strings
from services.similarity import is_similar
from services.ai_logic import analyze_and_detect_misuse
from services.firebase_store import get_all_assets
from services.cache_service import get_cached_assets, set_cached_assets

logger = logging.getLogger(__name__)
router = APIRouter()

# Max concurrent HTTP fetches for stored images
MAX_CONCURRENT_FETCHES = 20
FETCH_TIMEOUT_SECONDS = 10


# ── Async image fetcher ───────────────────────────────────────────────────────

async def _fetch_image_async(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
) -> bytes | None:
    """Fetch a single image URL asynchronously, respecting concurrency limit."""
    if not url or url.startswith("local://"):
        return None
    async with semaphore:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=FETCH_TIMEOUT_SECONDS)) as resp:
                if resp.status == 200:
                    return await resp.read()
                logger.warning(f"Non-200 status {resp.status} for {url}")
                return None
        except Exception as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None


async def _fetch_all_images_parallel(assets: list) -> list:
    """
    Fetch all stored asset images in parallel.
    Returns list of (asset_dict, image_bytes | None) tuples.
    """
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)
    connector = aiohttp.TCPConnector(limit=MAX_CONCURRENT_FETCHES, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            _fetch_image_async(session, asset.get("path", ""), semaphore)
            for asset in assets
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    pairs = []
    for asset, result in zip(assets, results):
        img_bytes = result if isinstance(result, bytes) else None
        pairs.append((asset, img_bytes))

    return pairs


# ── Single check endpoint ─────────────────────────────────────────────────────

@router.post("/")
async def check_asset(file: UploadFile = File(...)):
    """
    Scan a suspect file against the entire protected asset database.
    Uses async parallel fetching + two-gate filter + Gemini AI forensics.
    """
    start = time.perf_counter()

    try:
        contents = await file.read()
        mime_type = file.content_type or ""
        filename = file.filename or "unknown"

        logger.info(f"Check start: {filename} ({mime_type}, {len(contents)} bytes)")

        # ── Step 1: Process suspect file ──
        try:
            suspect_image: Image.Image = process_file(contents, filename, mime_type)
        except (ValueError, ImportError) as e:
            raise HTTPException(status_code=415, detail=str(e))

        suspect_dna = generate_multi_hash(suspect_image)

        # ── Step 2: Load asset database (with cache) ──
        assets = get_cached_assets()
        if assets is None:
            assets = get_all_assets()
            set_cached_assets(assets)

        if not assets:
            return {
                "status": "No Data",
                "message": "No protected assets registered yet. Upload originals first.",
                "processing_time_ms": _elapsed(start),
            }

        # ── Step 3: Parallel fetch all stored images ──
        fetch_start = time.perf_counter()
        asset_image_pairs = await _fetch_all_images_parallel(assets)
        fetch_elapsed = round((time.perf_counter() - fetch_start) * 1000, 1)
        logger.info(f"Parallel fetch of {len(assets)} assets took {fetch_elapsed}ms")

        # ── Step 4: Two-gate similarity scan ──
        for asset, img_bytes in asset_image_pairs:
            stored_dna = {
                "phash": asset.get("phash", asset.get("hash", "")),
                "dhash": asset.get("dhash", asset.get("hash", "")),
                "ahash": asset.get("ahash", asset.get("hash", "")),
                "whash": asset.get("whash", asset.get("hash", "")),
            }

            # Open stored image for histogram comparison
            if img_bytes:
                try:
                    stored_image = Image.open(io.BytesIO(img_bytes)).convert("RGB").resize((512, 512))
                except Exception:
                    stored_image = suspect_image  # Fallback
            else:
                stored_image = suspect_image  # Can't do histogram without image

            match, details = is_similar(suspect_dna, stored_dna, suspect_image, stored_image)

            if match:
                # ── Step 5: Gemini AI Forensic Audit ──
                ai_report = analyze_and_detect_misuse(
                    original_url=asset.get("path", ""),
                    suspicious_bytes=contents,
                    suspect_mime=mime_type or "image/jpeg",
                )

                # Determine final threat level (AI overrides if available)
                final_threat = ai_report.get("threat_level", details.get("preliminary_threat", "Medium"))
                is_stolen = ai_report.get("is_stolen", True)

                total_elapsed = _elapsed(start)
                logger.info(f"MATCH FOUND: {asset.get('filename')} | Threat: {final_threat} | {total_elapsed}ms")

                return {
                    "status": "Unauthorized" if is_stolen else "Review Required",
                    "matched_asset": {
                        "filename": asset.get("filename"),
                        "file_type": asset.get("file_type", "image"),
                        "asset_url": asset.get("path", ""),
                    },
                    "similarity": {
                        "composite_score": details.get("composite_score"),
                        "phash_distance": details.get("phash_distance"),
                        "dhash_distance": details.get("dhash_distance"),
                        "ahash_distance": details.get("ahash_distance"),
                        "whash_distance": details.get("whash_distance"),
                        "histogram_similarity": details.get("histogram_similarity"),
                        "gate_1_passed": details.get("gate_1_passed"),
                        "gate_2_passed": details.get("gate_2_passed"),
                    },
                    "threat_level": final_threat,
                    "ai_forensics": ai_report,
                    "suspect": {
                        "filename": filename,
                        "file_type": get_file_category(mime_type),
                        "digital_dna": suspect_dna,
                    },
                    "performance": {
                        "total_time_ms": total_elapsed,
                        "fetch_time_ms": fetch_elapsed,
                        "assets_scanned": len(assets),
                    },
                }

        # ── No match found ──
        return {
            "status": "Safe",
            "message": "No matching protected asset found in the database.",
            "suspect": {
                "filename": filename,
                "file_type": get_file_category(mime_type),
                "digital_dna": suspect_dna,
            },
            "performance": {
                "total_time_ms": _elapsed(start),
                "fetch_time_ms": fetch_elapsed if 'fetch_elapsed' in dir() else 0,
                "assets_scanned": len(assets),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _elapsed(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 1)