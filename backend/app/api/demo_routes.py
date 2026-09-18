"""
Demo Mode API routes.

Lets the frontend list bundled synthetic scenarios and run one
end-to-end through the exact same pipeline used for real uploads
(this is not a separate "fake" code path — the same OCR/validation/
tampering/face/risk services run, just against bundled synthetic
images, so the demo faithfully reflects the real pipeline).
"""
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import screening as models
from app.schemas import screening as schemas
from app.services import demo_data, storage_service, pipeline_service
from app.config.settings import get_settings

import os

router = APIRouter()
settings = get_settings()

# Resolve the bundled demo assets directory. Supports two layouts:
#   1. Local dev / source checkout: backend/app/api/demo_routes.py
#      -> ../../../../datasets/demo_documents (project root sibling of backend/)
#   2. Docker image: datasets/ copied to /app/datasets alongside the
#      backend app code (see docker/Dockerfile.backend)
# An explicit DEMO_ASSETS_DIR environment variable always wins.
_env_override = os.getenv("DEMO_ASSETS_DIR")
if _env_override:
    DATASETS_DIR = Path(_env_override)
else:
    _project_root_candidate = Path(__file__).resolve().parent.parent.parent.parent / "datasets" / "demo_documents"
    _docker_candidate = Path(__file__).resolve().parent.parent.parent / "datasets" / "demo_documents"
    DATASETS_DIR = _project_root_candidate if _project_root_candidate.exists() else _docker_candidate


@router.get("/demo/scenarios")
async def list_demo_scenarios():
    return {"scenarios": demo_data.DEMO_SCENARIOS, "datasets_notice": (
        "All demo documents are synthetic placeholder images generated for this "
        "hackathon prototype. They do not represent real people or real government records."
    )}


@router.post("/demo/seed/{scenario_id}", response_model=schemas.ScreeningResultResponse)
async def run_demo_scenario(scenario_id: str, db: Session = Depends(get_db)):
    scenario = next((s for s in demo_data.DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Unknown demo scenario '{scenario_id}'.")

    screening = models.Screening(status="processing", demo_mode=True, demo_scenario=scenario_id)
    db.add(screening)
    db.commit()
    db.refresh(screening)

    saved_paths = []
    document_results = []
    document_records = []

    try:
        for doc_filename in scenario["documents"]:
            source_path = DATASETS_DIR / doc_filename
            if not source_path.exists():
                raise HTTPException(
                    status_code=500,
                    detail=f"Demo asset '{doc_filename}' is missing from datasets/demo_documents.",
                )
            saved_path = storage_service.save_demo_file(source_path)
            saved_paths.append(saved_path)
            result = pipeline_service.process_single_document(saved_path)
            result["_file_path"] = saved_path
            result["_original_filename"] = doc_filename
            document_results.append(result)

        person_photo_path = None
        if scenario.get("person_photo"):
            source_path = DATASETS_DIR / scenario["person_photo"]
            if source_path.exists():
                person_photo_path = storage_service.save_demo_file(source_path)
                saved_paths.append(person_photo_path)

        face_result = pipeline_service.run_face_verification(document_results, person_photo_path)

        for result in document_results:
            doc_record = models.Document(
                screening_id=screening.id,
                original_filename=result["_original_filename"],
                document_type=result["document_type"],
                classification_confidence=result["classification_confidence"],
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

        return schemas.ScreeningResultResponse(
            screening_id=screening.id,
            created_at=screening.created_at,
            status=screening.status,
            demo_mode=True,
            demo_scenario=scenario_id,
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
    except HTTPException:
        screening.status = "failed"
        db.commit()
        raise
    except Exception as exc:  # noqa: BLE001
        screening.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Demo scenario failed: {exc}") from exc
    finally:
        # Demo assets are bundled sample files, not real identity documents,
        # but we still respect AUTO_DELETE_UPLOADS for the working copies.
        for path in saved_paths:
            storage_service.delete_file(path)
