"""
Primary screening API routes.

Implements:
  POST /api/screen                 - full end-to-end screening
  POST /api/documents/detect       - document type detection only
  POST /api/documents/extract      - OCR + field extraction only
  POST /api/documents/validate     - validation only (given extracted fields)
  POST /api/tampering/analyze      - tampering analysis only
  POST /api/face/verify            - face verification only
  POST /api/identity/compare       - cross-document comparison only
  GET  /api/screenings             - list past screenings
  GET  /api/screenings/{id}        - full detail for one screening
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import screening as models
from app.schemas import screening as schemas
from app.services import (
    storage_service,
    pipeline_service,
    document_classifier,
    ocr_service,
    validation_service,
    tampering_service,
    face_service,
    cross_document_service,
)
from app.utils.image_utils import load_image_any, preprocess_pipeline
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.post("/screen", response_model=schemas.ScreeningResultResponse)
async def screen_documents(
    documents: List[UploadFile] = File(..., description="One or more identity document images/PDFs"),
    document_types: Optional[str] = Form(
        None, description="Comma-separated manual document types, aligned by index (optional)"
    ),
    person_photo: Optional[UploadFile] = File(None, description="Optional person photo for face verification"),
    db: Session = Depends(get_db),
):
    """End-to-end screening: Modules 2 through 8 in one call."""
    if not documents:
        raise HTTPException(status_code=400, detail="At least one document must be uploaded.")

    manual_types = document_types.split(",") if document_types else []

    screening = models.Screening(status="processing", demo_mode=settings.DEMO_MODE)
    db.add(screening)
    db.commit()
    db.refresh(screening)

    saved_paths: list[Path] = []
    document_results: list[dict] = []
    document_records: list[models.Document] = []

    try:
        for idx, upload in enumerate(documents):
            try:
                saved_path = storage_service.save_upload(upload)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            saved_paths.append(saved_path)

            manual_type = manual_types[idx].strip() if idx < len(manual_types) and manual_types[idx].strip() else None
            result = pipeline_service.process_single_document(saved_path, manual_document_type=manual_type)
            result["_file_path"] = saved_path
            result["_original_filename"] = upload.filename
            document_results.append(result)

        person_photo_path: Optional[Path] = None
        if person_photo is not None:
            try:
                person_photo_path = storage_service.save_upload(person_photo)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc
            saved_paths.append(person_photo_path)

        face_result = pipeline_service.run_face_verification(document_results, person_photo_path)

        # Persist Document rows first so we have IDs for cross-doc comparison output
        for result in document_results:
            doc_record = models.Document(
                screening_id=screening.id,
                original_filename=result["_original_filename"],
                document_type=result["document_type"],
                classification_confidence=result["classification_confidence"],
                manually_selected_type=result["classification_confidence"] == 1.0,
                ocr_confidence=result["ocr_confidence"],
                extracted_fields=result["extracted_fields"],
                validation_status=result["validation"]["status"],
                validation_issues=result["validation"]["issues"],
                expiry_status=result["validation"].get("expiry_status", "N/A"),
                tampering_score=result["tampering"]["tampering_score"],
                tampering_level=result["tampering"]["tampering_level"],
                tampering_indicators=result["tampering"]["detected_indicators"],
                suspicious_regions=result["tampering"]["suspicious_regions"],
            )
            db.add(doc_record)
            document_records.append(doc_record)
        db.commit()
        for rec in document_records:
            db.refresh(rec)

        document_ids = [rec.id for rec in document_records]
        cross_doc_result = pipeline_service.run_cross_document_check(document_results, document_ids)
        risk_result = pipeline_service.run_risk_engine(document_results, face_result, cross_doc_result)

        # Persist screening-level results
        screening.status = "completed"
        screening.final_risk_score = risk_result["risk_score"]
        screening.final_risk_level = risk_result["risk_level"]
        screening.risk_explanations = risk_result["explanations"]
        if face_result:
            screening.face_similarity = face_result["face_similarity"]
            screening.face_match_status = face_result["match_status"]
        if cross_doc_result:
            screening.cross_document_consistency = cross_doc_result["consistency_level"]
            screening.cross_document_findings = cross_doc_result["findings"]

        risk_record = models.RiskAssessment(
            screening_id=screening.id,
            ocr_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "OCR Confidence"),
            validation_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "Document Validation"),
            expiry_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "Expiry Check"),
            tampering_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "Tampering Analysis"),
            face_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "Face Verification"),
            cross_doc_points=next(b["points_awarded"] for b in risk_result["breakdown"] if b["category"] == "Cross-Document Consistency"),
            total_score=risk_result["risk_score"],
            risk_level=risk_result["risk_level"],
            explanations=risk_result["explanations"],
            weights_used=risk_result["weights_used"],
        )
        db.add(risk_record)
        db.commit()

        # Build response
        doc_response_items = []
        for rec, result in zip(document_records, document_results):
            doc_response_items.append(
                schemas.ScreeningDocumentResult(
                    document_id=rec.id,
                    original_filename=rec.original_filename,
                    document_type=result["document_type"],
                    classification_confidence=result["classification_confidence"],
                    ocr_confidence=result["ocr_confidence"],
                    extracted_fields=schemas.ExtractedFields(**result["extracted_fields"]),
                    validation=schemas.ValidationResponse(
                        document_type=result["document_type"],
                        validation_status=result["validation"]["status"],
                        issues=result["validation"]["issues"],
                        expiry_status=result["validation"].get("expiry_status", "N/A"),
                        mrz_match=result["validation"].get("mrz_match"),
                        notes=result["validation"].get("notes", []),
                    ),
                    tampering=schemas.TamperingResponse(
                        tampering_score=result["tampering"]["tampering_score"],
                        tampering_level=result["tampering"]["tampering_level"],
                        suspicious_regions=result["tampering"]["suspicious_regions"],
                        detected_indicators=result["tampering"]["detected_indicators"],
                        explanation=result["tampering"]["explanation"],
                    ),
                )
            )

        response = schemas.ScreeningResultResponse(
            screening_id=screening.id,
            created_at=screening.created_at,
            status=screening.status,
            demo_mode=screening.demo_mode,
            demo_scenario=screening.demo_scenario,
            documents=doc_response_items,
            face_verification=schemas.FaceVerificationResponse(**face_result) if face_result else None,
            cross_document=schemas.CrossDocumentResponse(**cross_doc_result) if cross_doc_result else None,
            risk_assessment=schemas.RiskAssessmentResponse(
                risk_score=risk_result["risk_score"],
                risk_level=risk_result["risk_level"],
                breakdown=risk_result["breakdown"],
                explanations=risk_result["explanations"],
                weights_used=risk_result["weights_used"],
            ),
        )
        return response

    except HTTPException:
        screening.status = "failed"
        db.commit()
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Screening pipeline failed for screening_id=%s", screening.id)
        screening.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Screening failed: {exc}") from exc
    finally:
        for path in saved_paths:
            storage_service.delete_file(path)
        if saved_paths:
            for rec in document_records:
                rec.file_deleted = settings.AUTO_DELETE_UPLOADS
            db.commit()


# ---------------------------------------------------------------------------
# Individual module endpoints (useful for debugging / partial integrations)
# ---------------------------------------------------------------------------


@router.post("/documents/detect", response_model=schemas.DocumentDetectionResponse)
async def detect_document_type(document: UploadFile = File(...)):
    saved_path = storage_service.save_upload(document)
    try:
        raw_img = load_image_any(saved_path)
        ocr_result = ocr_service.run_ocr(saved_path)
        classification = document_classifier.classify_document(ocr_result.lines)
        requires_manual = document_classifier.needs_manual_selection(classification)
        return schemas.DocumentDetectionResponse(
            document_type=classification.document_type,
            confidence=classification.confidence,
            processing_status="completed",
            requires_manual_selection=requires_manual,
        )
    finally:
        storage_service.delete_file(saved_path)


@router.post("/documents/extract", response_model=schemas.OCRExtractionResponse)
async def extract_document_fields(
    document: UploadFile = File(...), document_type: Optional[str] = Form(None)
):
    saved_path = storage_service.save_upload(document)
    try:
        result = pipeline_service.process_single_document(saved_path, manual_document_type=document_type)
        return schemas.OCRExtractionResponse(
            document_type=result["document_type"],
            ocr_confidence=result["ocr_confidence"],
            extracted_fields=schemas.ExtractedFields(**result["extracted_fields"]),
            raw_text_lines=result["raw_text_lines"],
        )
    finally:
        storage_service.delete_file(saved_path)


@router.post("/documents/validate", response_model=schemas.ValidationResponse)
async def validate_document_fields(payload: schemas.ValidationRequest):
    result = validation_service.validate_document(payload.document_type.value, payload.fields)
    return schemas.ValidationResponse(
        document_type=payload.document_type,
        validation_status=result["status"],
        issues=result["issues"],
        expiry_status=result.get("expiry_status", "N/A"),
        mrz_match=result.get("mrz_match"),
        notes=result.get("notes", []),
    )


@router.post("/tampering/analyze", response_model=schemas.TamperingResponse)
async def analyze_document_tampering(document: UploadFile = File(...)):
    saved_path = storage_service.save_upload(document)
    try:
        raw_img = load_image_any(saved_path)
        preprocessed_img, _ = preprocess_pipeline(raw_img)
        demo_override = tampering_service.analyze_tampering_demo_override(Path(saved_path).name)
        result = demo_override if demo_override else tampering_service.analyze_tampering(saved_path, preprocessed_img)
        return schemas.TamperingResponse(
            tampering_score=result["tampering_score"],
            tampering_level=result["tampering_level"],
            suspicious_regions=result["suspicious_regions"],
            detected_indicators=result["detected_indicators"],
            explanation=result["explanation"],
        )
    finally:
        storage_service.delete_file(saved_path)


@router.post("/face/verify", response_model=schemas.FaceVerificationResponse)
async def verify_document_face(
    document: UploadFile = File(...),
    person_photo: UploadFile = File(...),
):
    doc_path = storage_service.save_upload(document)
    person_path = storage_service.save_upload(person_photo)
    try:
        doc_img = load_image_any(doc_path)
        person_img = load_image_any(person_path)
        result = face_service.verify_faces(
            document_image_path=doc_path,
            person_image_path=person_path,
            document_img_bgr=doc_img,
            person_img_bgr=person_img,
        )
        return schemas.FaceVerificationResponse(**result)
    finally:
        storage_service.delete_file(doc_path)
        storage_service.delete_file(person_path)


@router.post("/identity/compare", response_model=schemas.CrossDocumentResponse)
async def compare_identities(payload: schemas.CompareDocumentsRequest):
    doc_list = [
        {
            "document_id": d.document_id,
            "document_type": d.document_type,
            "fields": d.fields,
        }
        for d in payload.documents
    ]
    result = cross_document_service.compare_documents(doc_list)
    return schemas.CrossDocumentResponse(**result)


@router.get("/screenings", response_model=schemas.ScreeningListResponse)
async def list_screenings(db: Session = Depends(get_db), limit: int = 50):
    records = (
        db.query(models.Screening)
        .order_by(models.Screening.created_at.desc())
        .limit(limit)
        .all()
    )
    items = []
    low = medium = high = 0
    for rec in records:
        doc_types = [d.document_type for d in rec.documents]
        items.append(
            schemas.ScreeningListItem(
                screening_id=rec.id,
                created_at=rec.created_at,
                status=rec.status,
                document_types=doc_types,
                risk_level=rec.final_risk_level,
                risk_score=rec.final_risk_score,
            )
        )
        if rec.final_risk_level == "LOW RISK":
            low += 1
        elif rec.final_risk_level == "MEDIUM RISK":
            medium += 1
        elif rec.final_risk_level == "HIGH RISK":
            high += 1

    total = db.query(models.Screening).count()
    return schemas.ScreeningListResponse(
        total=total, low_risk_count=low, medium_risk_count=medium, high_risk_count=high, items=items
    )


@router.get("/screenings/{screening_id}", response_model=schemas.ScreeningResultResponse)
async def get_screening(screening_id: str, db: Session = Depends(get_db)):
    rec = db.query(models.Screening).filter(models.Screening.id == screening_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Screening not found.")

    doc_items = []
    for d in rec.documents:
        doc_items.append(
            schemas.ScreeningDocumentResult(
                document_id=d.id,
                original_filename=d.original_filename,
                document_type=d.document_type,
                classification_confidence=d.classification_confidence or 0.0,
                ocr_confidence=d.ocr_confidence or 0.0,
                extracted_fields=schemas.ExtractedFields(**(d.extracted_fields or {})),
                validation=schemas.ValidationResponse(
                    document_type=d.document_type,
                    validation_status=d.validation_status or "WARN",
                    issues=d.validation_issues or [],
                    expiry_status=d.expiry_status or "N/A",
                ),
                tampering=schemas.TamperingResponse(
                    tampering_score=d.tampering_score or 0.0,
                    tampering_level=d.tampering_level or "LOW",
                    suspicious_regions=d.suspicious_regions or [],
                    detected_indicators=d.tampering_indicators or [],
                    explanation="See detected_indicators for details.",
                ),
            )
        )

    risk = rec.risk_assessment
    risk_response = schemas.RiskAssessmentResponse(
        risk_score=rec.final_risk_score or 0.0,
        risk_level=rec.final_risk_level or "LOW RISK",
        breakdown=[
            {"category": "OCR Confidence", "points_awarded": risk.ocr_points if risk else 0, "max_points": settings.RISK_WEIGHT_OCR_CONFIDENCE, "reason": ""},
            {"category": "Document Validation", "points_awarded": risk.validation_points if risk else 0, "max_points": settings.RISK_WEIGHT_VALIDATION, "reason": ""},
            {"category": "Expiry Check", "points_awarded": risk.expiry_points if risk else 0, "max_points": settings.RISK_WEIGHT_EXPIRY, "reason": ""},
            {"category": "Tampering Analysis", "points_awarded": risk.tampering_points if risk else 0, "max_points": settings.RISK_WEIGHT_TAMPERING, "reason": ""},
            {"category": "Face Verification", "points_awarded": risk.face_points if risk else 0, "max_points": settings.RISK_WEIGHT_FACE, "reason": ""},
            {"category": "Cross-Document Consistency", "points_awarded": risk.cross_doc_points if risk else 0, "max_points": settings.RISK_WEIGHT_CROSS_DOC, "reason": ""},
        ],
        explanations=rec.risk_explanations or [],
        weights_used=risk.weights_used if risk else {},
    )

    return schemas.ScreeningResultResponse(
        screening_id=rec.id,
        created_at=rec.created_at,
        status=rec.status,
        demo_mode=rec.demo_mode,
        demo_scenario=rec.demo_scenario,
        documents=doc_items,
        face_verification=(
            schemas.FaceVerificationResponse(
                face_similarity=rec.face_similarity, match_status=rec.face_match_status, confidence=0.0
            )
            if rec.face_similarity is not None
            else None
        ),
        cross_document=(
            schemas.CrossDocumentResponse(
                consistency_level=rec.cross_document_consistency, comparisons=[], findings=rec.cross_document_findings or []
            )
            if rec.cross_document_consistency
            else None
        ),
        risk_assessment=risk_response,
    )
