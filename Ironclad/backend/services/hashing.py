"""
hashing.py — Triple-Hash DNA Fingerprinting
Generates pHash + dHash + aHash for a composite, attack-resistant fingerprint.
"""

from PIL import Image
import imagehash
import logging

logger = logging.getLogger(__name__)


# ── Single hash generators ────────────────────────────────────────────────────

def generate_phash(image: Image.Image) -> imagehash.ImageHash:
    """
    Perceptual Hash — resistant to resizing and minor colour shifts.
    Best for detecting structurally similar images.
    """
    try:
        return imagehash.phash(image, hash_size=8)  # 64-bit — matches stored legacy records
    except Exception as e:
        raise Exception(f"pHash generation failed: {str(e)}")


def generate_dhash(image: Image.Image) -> imagehash.ImageHash:
    """
    Difference Hash — detects gradient changes, good for detecting crops.
    """
    try:
        return imagehash.dhash(image, hash_size=8)
    except Exception as e:
        raise Exception(f"dHash generation failed: {str(e)}")


def generate_ahash(image: Image.Image) -> imagehash.ImageHash:
    """
    Average Hash — fastest, catches colour-space attacks and filter applications.
    """
    try:
        return imagehash.average_hash(image, hash_size=8)
    except Exception as e:
        raise Exception(f"aHash generation failed: {str(e)}")


def generate_whash(image: Image.Image) -> imagehash.ImageHash:
    """
    Wavelet Hash — catches frequency-domain manipulation (JPEG artefacts, blur).
    """
    try:
        return imagehash.whash(image, hash_size=8)
    except Exception as e:
        raise Exception(f"wHash generation failed: {str(e)}")


# ── Composite DNA ─────────────────────────────────────────────────────────────

def generate_multi_hash(image: Image.Image) -> dict:
    """
    Generate the full Digital DNA fingerprint for an asset.

    Returns a dict with string-serialised hashes:
    {
        "phash": "...",
        "dhash": "...",
        "ahash": "...",
        "whash": "..."
    }
    """
    return {
        "phash": str(generate_phash(image)),
        "dhash": str(generate_dhash(image)),
        "ahash": str(generate_ahash(image)),
        "whash": str(generate_whash(image)),
    }


# ── Similarity scoring ────────────────────────────────────────────────────────

# Weights for each hash type in the composite score
HASH_WEIGHTS = {
    "phash": 0.40,  # Best structural match
    "dhash": 0.30,  # Good for crop detection
    "ahash": 0.15,  # Catches colour attacks
    "whash": 0.15,  # Frequency manipulation
}

MAX_HASH_BITS = 64   # hash_size=8 → 8*8 = 64 bits


def composite_hash_distance(dna1: dict, dna2: dict) -> dict:
    """
    Compute a weighted composite similarity score between two DNA dicts.

    Returns:
    {
        "composite_score": float (0.0 = different, 1.0 = identical),
        "phash_distance": int,
        "dhash_distance": int,
        "ahash_distance": int,
        "whash_distance": int,
        "is_suspect": bool  (True if composite_score >= 0.80)
    }
    """
    scores = {}
    weighted_sum = 0.0

    for key, weight in HASH_WEIGHTS.items():
        h1_str = dna1.get(key)
        h2_str = dna2.get(key)

        if h1_str and h2_str:
            h1 = imagehash.hex_to_hash(h1_str)
            h2 = imagehash.hex_to_hash(h2_str)
            try:
                distance = h1 - h2
                similarity = max(0.0, 1.0 - (distance / MAX_HASH_BITS))
                scores[f"{key}_distance"] = distance
                scores[f"{key}_similarity"] = round(similarity, 4)
                weighted_sum += similarity * weight
            except TypeError:
                # Hash shapes differ (e.g. legacy 8×8 vs new 16×16) — treat as neutral
                import logging
                logging.getLogger(__name__).warning(
                    f"Hash shape mismatch for '{key}': {h1.hash.shape} vs {h2.hash.shape}. "
                    "Using neutral score."
                )
                scores[f"{key}_distance"] = -1
                scores[f"{key}_similarity"] = 0.5
                weighted_sum += 0.5 * weight
        else:
            # Hash string missing — treat as neutral (0.5)
            scores[f"{key}_distance"] = -1
            scores[f"{key}_similarity"] = 0.5
            weighted_sum += 0.5 * weight

    scores["composite_score"] = round(weighted_sum, 4)
    scores["is_suspect"] = weighted_sum >= 0.75  # 75% composite = flagged
    return scores


def hash_dict_from_strings(phash: str, dhash: str = None, ahash: str = None, whash: str = None) -> dict:
    """Helper to reconstruct a DNA dict from individual stored strings."""
    return {
        "phash": phash,
        "dhash": dhash or phash,  # fallback for legacy records
        "ahash": ahash or phash,
        "whash": whash or phash,
    }