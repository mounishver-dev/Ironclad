"""
file_processor.py
Universal file ingestion — converts ANY file type into a normalized PIL Image
for fingerprinting. Supports: JPEG, PNG, WEBP, GIF, BMP, TIFF, AVIF,
PDF (first page), Video (first keyframe via OpenCV), Audio (spectrogram).
"""

import io
import mimetypes
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# ── MIME type routing ────────────────────────────────────────────────────────

IMAGE_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "image/bmp", "image/tiff", "image/avif", "image/svg+xml",
    "image/x-icon",
}

VIDEO_TYPES = {
    "video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo",
    "video/x-matroska", "video/webm",
}

AUDIO_TYPES = {
    "audio/mpeg", "audio/wav", "audio/ogg", "audio/flac",
    "audio/aac", "audio/x-m4a",
}

PDF_TYPES = {"application/pdf"}


# ── Public API ───────────────────────────────────────────────────────────────

def process_file(contents: bytes, filename: str, mime_type: str | None = None) -> Image.Image:
    """
    Convert any supported file into a normalized RGB PIL Image.

    Parameters
    ----------
    contents  : raw bytes of the uploaded file
    filename  : original filename (used for MIME detection fallback)
    mime_type : MIME type string; if None, detected from filename extension

    Returns
    -------
    PIL.Image.Image in RGB mode, resized to a standard 512×512 canvas
    """
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(filename)
        mime_type = mime_type or "application/octet-stream"

    mime_type = mime_type.lower().split(";")[0].strip()
    logger.info(f"Processing file '{filename}' as {mime_type}")

    if mime_type in IMAGE_TYPES:
        return _process_image(contents)
    elif mime_type in PDF_TYPES:
        return _process_pdf(contents)
    elif mime_type in VIDEO_TYPES:
        return _process_video(contents, filename)
    elif mime_type in AUDIO_TYPES:
        return _process_audio(contents)
    else:
        # Try as image anyway (handles unknown extensions like .avif on older libs)
        try:
            return _process_image(contents)
        except Exception:
            raise ValueError(f"Unsupported or unrecognised file type: {mime_type}")


def get_file_category(mime_type: str) -> str:
    """Return a human-readable category string for the given MIME type."""
    mime_type = (mime_type or "").lower().split(";")[0].strip()
    if mime_type in IMAGE_TYPES:
        return "image"
    if mime_type in PDF_TYPES:
        return "pdf"
    if mime_type in VIDEO_TYPES:
        return "video"
    if mime_type in AUDIO_TYPES:
        return "audio"
    return "unknown"


# ── Private handlers ─────────────────────────────────────────────────────────

def _normalize(image: Image.Image) -> Image.Image:
    """Strip alpha, convert to RGB, standardise to 512×512."""
    if image.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "P":
            image = image.convert("RGBA")
        background.paste(image, mask=image.split()[-1] if image.mode in ("RGBA", "LA") else None)
        image = background
    elif image.mode != "RGB":
        image = image.convert("RGB")
    return image.resize((512, 512), Image.LANCZOS)


def _process_image(contents: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(contents))
    return _normalize(image)


def _process_pdf(contents: bytes) -> Image.Image:
    """Render the first page of a PDF as an image."""
    try:
        import pypdfium2 as pdfium
        pdf = pdfium.PdfDocument(contents)
        page = pdf[0]
        pil_image = page.render(scale=2).to_pil()
        return _normalize(pil_image)
    except ImportError:
        raise ImportError(
            "pypdfium2 is required for PDF support. "
            "Install it with: pip install pypdfium2"
        )


def _process_video(contents: bytes, filename: str) -> Image.Image:
    """Extract the first keyframe from a video file."""
    try:
        import cv2
        import numpy as np
        import tempfile
        import os

        # Write to a temp file because OpenCV needs a path
        suffix = "." + filename.rsplit(".", 1)[-1] if "." in filename else ".mp4"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        try:
            cap = cv2.VideoCapture(tmp_path)
            ret, frame = cap.read()
            cap.release()
        finally:
            os.unlink(tmp_path)

        if not ret:
            raise ValueError("Could not read any frame from video")

        # Convert BGR → RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        return _normalize(pil_image)

    except ImportError:
        raise ImportError(
            "opencv-python is required for video support. "
            "Install it with: pip install opencv-python"
        )


def _process_audio(contents: bytes) -> Image.Image:
    """Convert audio into a mel-spectrogram image for visual fingerprinting."""
    try:
        import librosa
        import librosa.display
        import numpy as np
        import matplotlib
        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt

        # Load audio from bytes
        audio_buf = io.BytesIO(contents)
        y, sr = librosa.load(audio_buf, sr=22050, mono=True, duration=30.0)

        # Generate mel spectrogram
        S = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
        S_db = librosa.power_to_db(S, ref=np.max)

        fig, ax = plt.subplots(figsize=(5.12, 5.12), dpi=100)
        ax.axis("off")
        librosa.display.specshow(S_db, sr=sr, x_axis=None, y_axis=None, ax=ax)

        buf = io.BytesIO()
        fig.savefig(buf, format="PNG", bbox_inches="tight", pad_inches=0)
        plt.close(fig)
        buf.seek(0)

        return _normalize(Image.open(buf))

    except ImportError:
        raise ImportError(
            "librosa and matplotlib are required for audio support. "
            "Install them with: pip install librosa matplotlib"
        )
