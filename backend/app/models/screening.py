"""
ORM models.

Only minimal metadata is persisted by default. Raw uploaded document
images are NOT stored in the database; they live briefly on disk in
UPLOAD_DIR and are deleted after processing when AUTO_DELETE_UPLOADS
is enabled (see config/settings.py and services/storage_service.py).
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    ForeignKey,
    JSON,
    Boolean,
)
from sqlalchemy.orm import relationship

from app.database.session import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Screening(Base):
    """Top-level record for a single screening request (one or more documents)."""

    __tablename__ = "screenings"

    id = Column(String, primary_key=True, default=gen_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending | processing | completed | failed
    demo_mode = Column(Boolean, default=True)
    demo_scenario = Column(String, nullable=True)  # e.g. "genuine", "tampered", ...

    final_risk_score = Column(Float, nullable=True)
    final_risk_level = Column(String, nullable=True)  # LOW | MEDIUM | HIGH
    risk_explanations = Column(JSON, nullable=True)  # list[str]

    face_similarity = Column(Float, nullable=True)
    face_match_status = Column(String, nullable=True)

    cross_document_consistency = Column(String, nullable=True)  # HIGH | MEDIUM | LOW | N/A
    cross_document_findings = Column(JSON, nullable=True)

    documents = relationship(
        "Document", back_populates="screening", cascade="all, delete-orphan"
    )
    risk_assessment = relationship(
        "RiskAssessment",
        back_populates="screening",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Document(Base):
    """A single uploaded document within a screening."""

    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_uuid)
    screening_id = Column(String, ForeignKey("screenings.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    original_filename = Column(String, nullable=True)
    document_type = Column(String, nullable=True)  # aadhaar | pan | passport | dl | voter_id
    classification_confidence = Column(Float, nullable=True)
    manually_selected_type = Column(Boolean, default=False)

    ocr_confidence = Column(Float, nullable=True)
    extracted_fields = Column(JSON, nullable=True)  # structured field dict

    validation_status = Column(String, nullable=True)  # PASS | WARN | FAIL
    validation_issues = Column(JSON, nullable=True)  # list[str]
    expiry_status = Column(String, nullable=True)  # VALID | EXPIRED | N/A | UNKNOWN

    tampering_score = Column(Float, nullable=True)
    tampering_level = Column(String, nullable=True)  # LOW | MEDIUM | HIGH
    tampering_indicators = Column(JSON, nullable=True)  # list[str]
    suspicious_regions = Column(JSON, nullable=True)  # list[dict: x,y,w,h,reason]

    file_deleted = Column(Boolean, default=False)

    screening = relationship("Screening", back_populates="documents")
    analysis_result = relationship(
        "AnalysisResult",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AnalysisResult(Base):
    """Consolidated per-document analysis snapshot (denormalized for fast reads)."""

    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    summary = Column(JSON, nullable=True)

    document = relationship("Document", back_populates="analysis_result")


class RiskAssessment(Base):
    """Final explainable risk breakdown for a screening."""

    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True, default=gen_uuid)
    screening_id = Column(String, ForeignKey("screenings.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    ocr_points = Column(Float, nullable=True)
    validation_points = Column(Float, nullable=True)
    expiry_points = Column(Float, nullable=True)
    tampering_points = Column(Float, nullable=True)
    face_points = Column(Float, nullable=True)
    cross_doc_points = Column(Float, nullable=True)

    total_score = Column(Float, nullable=True)
    risk_level = Column(String, nullable=True)
    explanations = Column(JSON, nullable=True)
    weights_used = Column(JSON, nullable=True)

    screening = relationship("Screening", back_populates="risk_assessment")
