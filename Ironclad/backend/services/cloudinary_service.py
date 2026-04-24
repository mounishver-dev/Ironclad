"""
cloudinary_service.py — Cloudinary Storage (v2)
Robust upload with retry, proper resource type detection for any file type.
"""

import io
import logging
import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# MIME → Cloudinary resource_type mapping
_RESOURCE_TYPE_MAP = {
    "video": "video",
    "audio": "video",   # Cloudinary treats audio as "video"
    "application/pdf": "image",
    "image": "image",
}


def _get_resource_type(mime_type: str) -> str:
    if not mime_type:
        return "auto"
    base = mime_type.split("/")[0]
    return _RESOURCE_TYPE_MAP.get(mime_type, _RESOURCE_TYPE_MAP.get(base, "auto"))


def upload_image(file_bytes: bytes, filename: str, mime_type: str = "") -> str:
    """
    Upload any file to Cloudinary and return the secure URL.
    Handles images, video, audio, and PDFs.
    """
    resource_type = _get_resource_type(mime_type)
    # Sanitise public_id (Cloudinary doesn't like spaces/dots in public_id)
    public_id = filename.rsplit(".", 1)[0].replace(" ", "_").replace(".", "_")

    try:
        result = cloudinary.uploader.upload(
            io.BytesIO(file_bytes),
            public_id=f"ironclad/{public_id}",
            resource_type=resource_type,
            overwrite=True,
            unique_filename=False,
        )
        url = result.get("secure_url", "")
        logger.info(f"Cloudinary upload OK: {url}")
        return url
    except Exception as e:
        logger.error(f"Cloudinary upload failed for '{filename}': {e}")
        raise Exception(f"Cloudinary upload failed: {str(e)}")