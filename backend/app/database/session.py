"""
SQLAlchemy engine/session configuration.

Uses SQLite by default for zero-setup local development. Because the
application only relies on standard SQLAlchemy ORM features (no
SQLite-specific SQL), swapping DATABASE_URL to a PostgreSQL DSN
(e.g. postgresql+psycopg2://user:pass@host:5432/dbname) is a drop-in
change — no model or service code needs to change.
"""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.settings import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session per-request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called on application startup."""
    # Import models so they're registered on Base.metadata before create_all.
    from app.models import screening  # noqa: F401

    Base.metadata.create_all(bind=engine)
