"""
VeriShield — FastAPI application.

IMPORTANT: VeriShield is an AI-assisted preliminary document-screening system.
It identifies suspicious indicators and generates a risk assessment for human review.
It does NOT verify documents against official government databases and does NOT
claim 100% fake/genuine verification.
"""
from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.database.session import init_db
from app.api import screening_routes, demo_routes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info(
        "Application started. DEMO_MODE=%s AUTO_DELETE_UPLOADS=%s",
        settings.DEMO_MODE,
        settings.AUTO_DELETE_UPLOADS,
    )
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "VeriShield is an AI-assisted preliminary document-screening system. "
        "It identifies suspicious indicators and generates a risk assessment for human review. "
        "Does not claim 100% fake/genuine verification."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "detail": str(exc)},
    )


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "ok",
        "demo_mode": settings.DEMO_MODE,
        "disclaimer": (
            "This system provides AI-assisted screening and decision support only. "
            "It does not verify documents against official government databases and "
            "does not guarantee document authenticity."
        ),
        "docs": "/docs",
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/system/info")
async def system_info():
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "supported_document_types": [
            "aadhaar",
            "pan",
            "passport",
            "driving_licence",
            "voter_id",
        ],
        "auto_delete_uploads": settings.AUTO_DELETE_UPLOADS,
        "risk_bands": {
            "low_risk_max": settings.RISK_LOW_MAX,
            "medium_risk_max": settings.RISK_MEDIUM_MAX,
        },
        "disclaimer": (
            "Format validation performed by this system is independent of, and not a "
            "substitute for, official government verification."
        ),
    }


app.include_router(screening_routes.router, prefix="/api", tags=["screening"])
app.include_router(demo_routes.router, prefix="/api", tags=["demo"])
