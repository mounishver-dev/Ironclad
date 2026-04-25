"""
firebase_config.py — Firebase Admin SDK Initialization

Supports two modes:
  1. Local dev  → reads firebase_key.json file from disk
  2. Production → reads FIREBASE_KEY_JSON environment variable (Vercel / Cloud Run)
"""

import os
import json
import logging
import firebase_admin
from firebase_admin import credentials, firestore

logger = logging.getLogger(__name__)

def _initialize_firebase():
    """Initialize Firebase Admin SDK — works locally and on Vercel."""
    if firebase_admin._apps:
        # Already initialized (e.g. hot-reload in uvicorn)
        return firestore.client()

    # ── Option 1: Environment variable (Vercel / any cloud) ──────────────
    firebase_key_json = os.getenv("FIREBASE_KEY_JSON")
    if firebase_key_json:
        try:
            key_dict = json.loads(firebase_key_json)
            cred = credentials.Certificate(key_dict)
            logger.info("Firebase initialized from FIREBASE_KEY_JSON env var.")
        except json.JSONDecodeError as e:
            raise ValueError(
                "FIREBASE_KEY_JSON env var is set but not valid JSON. "
                f"Error: {e}"
            )

    # ── Option 2: Local key file (development) ────────────────────────────
    else:
        key_path = os.getenv("FIREBASE_KEY_PATH", "firebase_key.json")
        if not os.path.exists(key_path):
            raise FileNotFoundError(
                f"Firebase key file not found at '{key_path}'. "
                "Set FIREBASE_KEY_JSON env var for production deployments."
            )
        cred = credentials.Certificate(key_path)
        logger.info(f"Firebase initialized from key file: {key_path}")

    firebase_admin.initialize_app(cred)
    return firestore.client()


db_firestore = _initialize_firebase()