"""
ai_logic.py — Gemini 2.5 Flash Forensic Agent
Performs deep multimodal analysis with structured JSON output.
Uses system instructions to act as a certified Digital Forensic Analyst.
"""

import os
import json
import time
import logging
import requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── Gemini client ─────────────────────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Model preference order — most capable first
MODELS = [
    "gemini-2.5-flash-preview-04-17",  # Primary: Gemini 2.5 Flash
    "gemini-2.0-flash",                 # Fallback 1
    "gemini-1.5-flash",                 # Fallback 2
]

# ── System instruction ────────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """You are a certified Digital Forensic Analyst specialising in 
intellectual property theft detection for sports media broadcasters. 
You have 15 years of experience identifying pirated content.
You analyse pairs of images with FORENSIC PRECISION and respond ONLY with valid JSON.
Your analysis must be objective, factual, and based solely on visual evidence."""

# ── Forensic prompt ───────────────────────────────────────────────────────────
FORENSIC_PROMPT = """FORENSIC ANALYSIS REQUEST — Digital Asset Piracy Detection

You will receive TWO images:
  IMAGE 1: The ORIGINAL protected asset (reference)
  IMAGE 2: The SUSPECT asset under investigation

Perform a comprehensive forensic comparison and respond with ONLY this JSON structure 
(no markdown, no extra text):

{
  "is_stolen": true or false,
  "confidence": 0 to 100,
  "threat_level": "High" or "Medium" or "Low" or "Safe",
  "verdict": "one-sentence verdict",
  "modifications_detected": [
    "list of specific modifications found, e.g. 'Cropped top 20%', 'Gaussian blur applied', 'Watermark removed', 'Aspect ratio changed', 'Color filter applied'"
  ],
  "evidence": [
    "list of specific visual evidence supporting verdict"
  ],
  "piracy_type": "Full Copy" or "Derivative Work" or "Fair Use" or "None",
  "recommended_action": "Immediate Takedown" or "Legal Review" or "Monitor" or "No Action",
  "summary": "2-3 sentence professional summary of findings"
}

Threat Level Guide:
- High: Near-identical copy, minor edits only — clear piracy, immediate action needed
- Medium: Significantly modified but original is clearly the source
- Low: Possible derivative work, substantial transformation present
- Safe: No meaningful similarity, different content"""


# ── Main analysis function ───────────────────────────────────────────────────

def analyze_and_detect_misuse(
    original_url: str,
    suspicious_bytes: bytes,
    suspect_mime: str = "image/jpeg",
) -> dict:
    """
    Perform Gemini forensic analysis comparing an original asset (via URL)
    to a suspect upload (raw bytes).

    Returns a structured dict with all forensic findings.
    Falls back gracefully through model list.
    """
    # Download the original image
    try:
        orig_response = requests.get(original_url, timeout=15)
        orig_response.raise_for_status()
        orig_bytes = orig_response.content
        orig_mime = orig_response.headers.get("content-type", "image/jpeg").split(";")[0]
    except Exception as e:
        logger.error(f"Failed to download original from {original_url}: {e}")
        return _error_result(f"Could not retrieve original asset: {str(e)}")

    # Try each model
    for model_name in MODELS:
        result = _try_model(model_name, orig_bytes, orig_mime, suspicious_bytes, suspect_mime)
        if result is not None:
            return result

    return _error_result("All AI models exhausted. Please retry in 30 seconds.")


def _try_model(
    model_name: str,
    orig_bytes: bytes,
    orig_mime: str,
    suspicious_bytes: bytes,
    suspect_mime: str,
    max_retries: int = 2,
) -> dict | None:
    """
    Attempt forensic analysis with a specific model.
    Returns a result dict on success, None if the model should be skipped.
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(text=FORENSIC_PROMPT),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=orig_mime,
                                    data=orig_bytes,
                                )
                            ),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type=suspect_mime,
                                    data=suspicious_bytes,
                                )
                            ),
                        ],
                    )
                ],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,        # Low temperature = more deterministic forensic output
                    max_output_tokens=1024,
                ),
            )

            raw_text = response.text.strip()
            logger.info(f"[{model_name}] Raw response length: {len(raw_text)}")
            return _parse_response(raw_text, model_name)

        except Exception as e:
            err = str(e).lower()
            if "429" in err or "resource_exhausted" in err or "quota" in err:
                wait = 15 * (attempt + 1)
                logger.warning(f"[{model_name}] Quota hit. Waiting {wait}s...")
                time.sleep(wait)
                continue
            elif "404" in err or "not_found" in err or "invalid" in err:
                logger.warning(f"[{model_name}] Model not available: {e}")
                return None  # Skip to next model
            else:
                logger.error(f"[{model_name}] Unexpected error: {e}")
                return _error_result(f"AI analysis error: {str(e)}")

    return None  # Max retries exhausted for this model


def _parse_response(raw_text: str, model_name: str) -> dict:
    """Parse Gemini's response into a structured dict."""
    # Strip markdown code fences if present
    clean = raw_text
    if "```" in clean:
        lines = clean.split("\n")
        clean = "\n".join(
            line for line in lines
            if not line.strip().startswith("```")
        )

    try:
        data = json.loads(clean)
        data["_model_used"] = model_name
        data["_analysis_status"] = "success"
        return data
    except json.JSONDecodeError:
        # JSON parsing failed — wrap raw text in structured format
        logger.warning(f"[{model_name}] Could not parse JSON, wrapping raw text")
        return {
            "_model_used": model_name,
            "_analysis_status": "partial",
            "is_stolen": None,
            "confidence": None,
            "threat_level": "Unknown",
            "verdict": "AI returned unstructured data",
            "modifications_detected": [],
            "evidence": [],
            "piracy_type": "Unknown",
            "recommended_action": "Manual Review",
            "summary": raw_text[:500],  # Truncate for safety
        }


def _error_result(message: str) -> dict:
    """Return a standardised error result dict."""
    return {
        "_analysis_status": "error",
        "_error": message,
        "is_stolen": None,
        "confidence": None,
        "threat_level": "Unknown",
        "verdict": message,
        "modifications_detected": [],
        "evidence": [],
        "piracy_type": "Unknown",
        "recommended_action": "Manual Review",
        "summary": message,
    }