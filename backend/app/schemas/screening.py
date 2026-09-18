"""Pydantic schemas used across the API layer."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, ConfigDict


class DocumentType(str, Enum):
    aadhaar = "aadhaar"
    pan = "pan"
    passport = "passport"
    driving_licence = "driving_licence"
    voter_id = "voter_id"
    unknown = "unknown"


class RiskLevel(str, Enum):
    low = "LOW RISK"
    medium = "MEDIUM RISK"
    high = "HIGH RISK"


# ---------- Module 2: Document type detection ----------


class DocumentDetectionResponse(BaseModel):
    document_type: DocumentType
    confidence: float
    processing_status: str
    requires_manual_selection: bool = False


# ---------- Module 3: OCR / field extraction ----------


class ExtractedFields(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    document_number: Optional[str] = None
    parent_name: Optional[str] = None
    nationality: Optional[str] = None
    expiry_date: Optional[str] = None
    issue_date: Optional[str] = None
    mrz_raw: Optional[str] = None
    photograph_region_detected: bool = False


class OCRExtractionResponse(BaseModel):
    document_type: DocumentType
    ocr_confidence: float
    extracted_fields: ExtractedFields
    raw_text_lines: List[str] = Field(default_factory=list)


# ---------- Module 4: Validation ----------


class ValidationStatus(str, Enum):
    pass_ = "PASS"
    warn = "WARN"
    fail = "FAIL"


class ValidationResponse(BaseModel):
    document_type: DocumentType
    validation_status: ValidationStatus
    issues: List[str] = Field(default_factory=list)
    expiry_status: str = "N/A"
    mrz_match: Optional[bool] = None
    notes: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "This validation checks document format and internal logical consistency only. "
        "It does NOT verify records against any government database."
    )


# ---------- Module 5: Tampering detection ----------


class SuspiciousRegion(BaseModel):
    x: int
    y: int
    width: int
    height: int
    reason: str
    severity: str  # LOW | MEDIUM | HIGH


class TamperingResponse(BaseModel):
    tampering_score: float
    tampering_level: str  # LOW | MEDIUM | HIGH
    suspicious_regions: List[SuspiciousRegion] = Field(default_factory=list)
    detected_indicators: List[str] = Field(default_factory=list)
    explanation: str
    disclaimer: str = "Potential tampering indicators detected by heuristic analysis. This is not a guaranteed forgery determination."


# ---------- Module 6: Face verification ----------


class FaceVerificationResponse(BaseModel):
    face_similarity: float  # 0-100
    match_status: str  # LIKELY MATCH | MANUAL REVIEW REQUIRED | LIKELY MISMATCH | NO FACE DETECTED
    confidence: float
    notes: List[str] = Field(default_factory=list)


# ---------- Module 7: Cross-document consistency ----------


class FieldComparison(BaseModel):
    field_name: str
    values: Dict[str, Optional[str]]  # document_id/type -> value
    consistent: bool
    note: Optional[str] = None


class CrossDocumentResponse(BaseModel):
    consistency_level: str  # HIGH | MEDIUM | LOW | N/A
    comparisons: List[FieldComparison] = Field(default_factory=list)
    findings: List[str] = Field(default_factory=list)


# ---------- Module 8: Risk engine ----------


class RiskBreakdownItem(BaseModel):
    category: str
    points_awarded: float
    max_points: float
    reason: str


class RiskAssessmentResponse(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    breakdown: List[RiskBreakdownItem]
    explanations: List[str]
    weights_used: Dict[str, float]


# ---------- Top-level screening ----------


class ScreeningDocumentResult(BaseModel):
    document_id: str
    original_filename: Optional[str]
    document_type: DocumentType
    classification_confidence: float
    ocr_confidence: float
    extracted_fields: ExtractedFields
    validation: ValidationResponse
    tampering: TamperingResponse


class ScreeningResultResponse(BaseModel):
    screening_id: str
    created_at: datetime
    status: str
    demo_mode: bool
    demo_scenario: Optional[str] = None
    documents: List[ScreeningDocumentResult]
    face_verification: Optional[FaceVerificationResponse] = None
    cross_document: Optional[CrossDocumentResponse] = None
    risk_assessment: RiskAssessmentResponse


class ScreeningListItem(BaseModel):
    screening_id: str
    created_at: datetime
    status: str
    document_types: List[str]
    risk_level: Optional[str]
    risk_score: Optional[float]


class ScreeningListResponse(BaseModel):
    total: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    items: List[ScreeningListItem]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class ValidationRequest(BaseModel):
    document_type: DocumentType
    fields: Dict[str, Any] = Field(default_factory=dict)


class CompareDocumentsItem(BaseModel):
    document_id: str
    document_type: str
    fields: Dict[str, Any] = Field(default_factory=dict)


class CompareDocumentsRequest(BaseModel):
    documents: List[CompareDocumentsItem]

