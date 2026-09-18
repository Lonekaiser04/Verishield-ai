"""
Central application configuration.

All values can be overridden via environment variables (see .env.example).
Risk engine weights live here so they can be tuned without touching
business logic in services/risk_service.py.
"""
from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


def _bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class Settings:
    # --- General ---
    APP_NAME: str = "VeriShield"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = _bool("DEBUG", "true")

    # --- Demo mode ---
    # When true, the system uses bundled synthetic scenarios and lightweight
    # heuristic fallbacks instead of requiring heavyweight ML model downloads.
    DEMO_MODE: bool = _bool("DEMO_MODE", "true")

    # --- Storage ---
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'app' / 'database' / 'screening.db'}"
    )
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "app" / "uploads_tmp")))
    # If true, uploaded document images are deleted from disk immediately
    # after processing completes. Only derived metadata/results are kept.
    AUTO_DELETE_UPLOADS: bool = _bool("AUTO_DELETE_UPLOADS", "true")
    MAX_UPLOAD_MB: int = int(os.getenv("MAX_UPLOAD_MB", "15"))

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    # --- OCR / CV ---
    OCR_LANG: str = os.getenv("OCR_LANG", "en")
    USE_GPU: bool = _bool("USE_GPU", "false")

    # --- Face verification ---
    FACE_MATCH_THRESHOLD: float = float(os.getenv("FACE_MATCH_THRESHOLD", "70"))  # percent
    FACE_REVIEW_THRESHOLD: float = float(os.getenv("FACE_REVIEW_THRESHOLD", "50"))  # percent

    # --- Risk engine weights (must sum to 100 across categories) ---
    # Each weight represents the maximum number of risk points that
    # category can contribute to the final 0-100 risk score.
    RISK_WEIGHT_OCR_CONFIDENCE: float = float(os.getenv("RISK_WEIGHT_OCR_CONFIDENCE", "10"))
    RISK_WEIGHT_VALIDATION: float = float(os.getenv("RISK_WEIGHT_VALIDATION", "20"))
    RISK_WEIGHT_EXPIRY: float = float(os.getenv("RISK_WEIGHT_EXPIRY", "10"))
    RISK_WEIGHT_TAMPERING: float = float(os.getenv("RISK_WEIGHT_TAMPERING", "30"))
    RISK_WEIGHT_FACE: float = float(os.getenv("RISK_WEIGHT_FACE", "15"))
    RISK_WEIGHT_CROSS_DOC: float = float(os.getenv("RISK_WEIGHT_CROSS_DOC", "15"))

    RISK_LOW_MAX: int = int(os.getenv("RISK_LOW_MAX", "30"))
    RISK_MEDIUM_MAX: int = int(os.getenv("RISK_MEDIUM_MAX", "60"))
    # anything above RISK_MEDIUM_MAX is HIGH RISK

    # --- Document classifier confidence threshold ---
    CLASSIFIER_CONFIDENCE_THRESHOLD: float = float(
        os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD", "0.55")
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
