"""
main.py — Ironclad 2.0 API Server
Forensic-Grade Digital Asset Protection powered by Google AI
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.upload import router as upload_router
from routes.check import router as check_router
from routes.assets import router as assets_router
from services.cache_service import get_cache_stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ── App instance ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="Ironclad — Digital Asset Protection API",
    description=(
        "Forensic-Grade Anti-Piracy System using Google Gemini 2.5 Flash, "
        "Firebase Firestore, and Multi-Hash Digital DNA fingerprinting."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(upload_router, prefix="/upload", tags=["Asset Registration"])
app.include_router(check_router,  prefix="/check",  tags=["Piracy Detection"])
app.include_router(assets_router, prefix="/assets", tags=["Asset Registry"])

# ── System endpoints ──────────────────────────────────────────────────────────

@app.get("/", tags=["System"])
def read_root():
    return {
        "service": "Ironclad Digital Asset Protection",
        "version": "2.0.0",
        "status": "operational",
        "powered_by": ["Gemini 2.5 Flash", "Firebase Firestore", "Google Gen AI SDK"],
        "endpoints": {
            "upload":   "POST /upload/   — Register a protected asset",
            "check":    "POST /check/    — Scan a suspect file for piracy",
            "assets":   "GET  /assets/   — List all protected assets",
            "health":   "GET  /health    — System health check",
            "stats":    "GET  /stats     — System statistics",
            "docs":     "GET  /docs      — Interactive API documentation",
        },
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "api_version": "2.0.0"}


@app.get("/stats", tags=["System"])
def system_stats():
    from services.firebase_store import get_asset_count
    try:
        asset_count = get_asset_count()
    except Exception:
        asset_count = -1

    return {
        "protected_assets": asset_count,
        "cache": get_cache_stats(),
        "capabilities": {
            "file_types": ["image/jpeg", "image/png", "image/webp", "image/gif",
                           "image/bmp", "image/tiff", "application/pdf",
                           "video/mp4", "video/quicktime", "audio/mpeg", "audio/wav"],
            "hashing_algorithms": ["pHash", "dHash", "aHash", "wHash"],
            "ai_model": "Gemini 2.5 Flash",
            "similarity_gates": 2,
        },
    }