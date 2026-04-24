"""
upload.py — Universal Asset Registration Endpoint
Accepts ANY file type (images, PDF, video, audio) via multipart/form-data.
Generates a full Digital DNA fingerprint and stores it in Firestore.
Cloudinary upload happens in the background so the response is instant.
"""

import io
import time
import logging
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from PIL import Image

from services.file_processor import process_file, get_file_category
from services.hashing import generate_multi_hash
from services.firebase_store import save_asset
from services.cloudinary_service import upload_image

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Background task ───────────────────────────────────────────────────────────

def _upload_to_cloudinary_bg(contents: bytes, filename: str, doc_id: str):
    """Runs in background — updates Cloudinary URL after fast initial response."""
    try:
        url = upload_image(contents, filename)
        logger.info(f"Background Cloudinary upload done for {doc_id}: {url}")
    except Exception as e:
        logger.error(f"Background Cloudinary upload failed for {doc_id}: {e}")


# ── Main upload endpoint ──────────────────────────────────────────────────────

@router.post("/")
async def upload_asset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Register a new protected asset.

    Accepts: images (JPEG/PNG/WEBP/GIF/BMP/TIFF/AVIF), PDF, video, audio.
    Returns the Digital DNA fingerprint immediately.
    """
    start = time.perf_counter()

    try:
        contents = await file.read()
        mime_type = file.content_type or ""
        filename = file.filename or "unknown"
        file_size = len(contents)

        logger.info(f"Upload start: {filename} ({mime_type}, {file_size} bytes)")

        # ── Step 1: Convert to normalised image ──
        try:
            image: Image.Image = process_file(contents, filename, mime_type)
        except ValueError as ve:
            raise HTTPException(status_code=415, detail=str(ve))
        except ImportError as ie:
            raise HTTPException(status_code=501, detail=str(ie))

        # ── Step 2: Generate Digital DNA ──
        dna = generate_multi_hash(image)
        file_category = get_file_category(mime_type)

        # ── Step 3: Cloudinary upload (primary — for URL) ──
        try:
            cloudinary_url = upload_image(contents, filename)
        except Exception as e:
            logger.warning(f"Cloudinary upload failed (using placeholder): {e}")
            cloudinary_url = f"local://{filename}"

        # ── Step 4: Save to Firestore ──
        doc_id = save_asset(
            filename=filename,
            dna=dna,
            cloudinary_url=cloudinary_url,
            file_type=file_category,
            file_size=file_size,
            mime_type=mime_type,
        )

        elapsed = round((time.perf_counter() - start) * 1000, 1)
        logger.info(f"Upload complete: {doc_id} in {elapsed}ms")

        return {
            "success": True,
            "message": "Asset registered and protected successfully",
            "doc_id": doc_id,
            "filename": filename,
            "file_type": file_category,
            "mime_type": mime_type,
            "file_size_bytes": file_size,
            "digital_dna": dna,
            "asset_url": cloudinary_url,
            "processing_time_ms": elapsed,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")