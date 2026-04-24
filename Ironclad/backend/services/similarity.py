"""
similarity.py — Multi-Gate Similarity Engine
Gate 1: Composite multi-hash (fast, mathematical)
Gate 2: RGB Histogram correlation (structural colour verification)
Both gates must pass before Gemini AI is invoked.
"""

import numpy as np
import cv2
from PIL import Image
from typing import Tuple

from services.hashing import composite_hash_distance


# ── Gate thresholds ───────────────────────────────────────────────────────────

COMPOSITE_THRESHOLD = 0.75      # Gate 1: score ≥ 0.75 to proceed
HISTOGRAM_THRESHOLD = 0.50      # Gate 2: histogram correlation ≥ 0.50

THREAT_HIGH_SCORE    = 0.93     # composite_score ≥ this → HIGH threat
THREAT_MEDIUM_SCORE  = 0.80     # composite_score ≥ this → MEDIUM threat


# ── Gate 1: Multi-hash ────────────────────────────────────────────────────────

def multi_hash_gate(dna1: dict, dna2: dict) -> Tuple[bool, dict]:
    """
    Gate 1: Composite hash distance check.
    Returns (passed, score_details).
    """
    scores = composite_hash_distance(dna1, dna2)
    passed = scores["composite_score"] >= COMPOSITE_THRESHOLD
    return passed, scores


# ── Gate 2: Histogram ─────────────────────────────────────────────────────────

def histogram_similarity(img1: Image.Image, img2: Image.Image) -> float:
    """
    Compare two images using 3D RGB histogram correlation.
    Returns a value between -1 (totally different) and 1 (identical).
    Practically: scores > 0.5 indicate similar colour distribution.
    """
    arr1 = cv2.cvtColor(np.array(img1), cv2.COLOR_RGB2BGR)
    arr2 = cv2.cvtColor(np.array(img2), cv2.COLOR_RGB2BGR)

    # 8-bin per channel → 512 bins total, fast & robust
    hist1 = cv2.calcHist([arr1], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)
    hist2 = cv2.calcHist([arr2], [0, 1, 2], None, [8, 8, 8], [0, 256] * 3)

    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    return float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))


# ── Combined gateway ──────────────────────────────────────────────────────────

def is_similar(
    dna1: dict,
    dna2: dict,
    img1: Image.Image,
    img2: Image.Image,
) -> Tuple[bool, dict]:
    """
    Run the two-gate similarity check.

    Parameters
    ----------
    dna1, dna2 : Digital DNA dicts (phash/dhash/ahash/whash strings)
    img1, img2 : Normalised PIL Images for histogram comparison

    Returns
    -------
    (match: bool, details: dict)
      match=True means the file passed BOTH gates and should go to AI audit.
    """
    # --- Gate 1: Hash similarity ---
    hash_passed, hash_scores = multi_hash_gate(dna1, dna2)

    if not hash_passed:
        return False, {
            "gate_1_passed": False,
            "gate_2_passed": False,
            "reason": "Structurally too different (hash gate failed)",
            **hash_scores,
            "histogram_similarity": None,
        }

    # --- Gate 2: Histogram similarity ---
    hist_score = histogram_similarity(img1, img2)
    hist_passed = hist_score >= HISTOGRAM_THRESHOLD

    details = {
        "gate_1_passed": True,
        "gate_2_passed": hist_passed,
        "composite_score": hash_scores["composite_score"],
        "phash_distance": hash_scores.get("phash_distance"),
        "dhash_distance": hash_scores.get("dhash_distance"),
        "ahash_distance": hash_scores.get("ahash_distance"),
        "whash_distance": hash_scores.get("whash_distance"),
        "histogram_similarity": round(hist_score, 4),
    }

    # Determine preliminary threat level from math alone
    score = hash_scores["composite_score"]
    if score >= THREAT_HIGH_SCORE:
        details["preliminary_threat"] = "High"
    elif score >= THREAT_MEDIUM_SCORE:
        details["preliminary_threat"] = "Medium"
    else:
        details["preliminary_threat"] = "Low"

    if not hist_passed:
        # Hash similar but histogram differs — possible false positive
        details["reason"] = "Hash match but histogram diverges — possible false positive"
        return False, details

    details["reason"] = "Both gates passed — forwarding to AI forensic audit"
    return True, details