"""
Screening Pipeline Orchestrator.

Ties together Modules 2-8 for a single document, and Module 7 across
multiple documents, producing the data needed for the final
ScreeningResultResponse. Kept separate from the API layer so the same
pipeline can be invoked from the /api/screen endpoint and from the
demo-seed endpoint.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.services import (
    ocr_service,
    document_classifier,
    field_extraction_service,
    validation_service,
    tampering_service,
    face_service,
    cross_document_service,
    risk_service,
)
from app.utils.image_utils import load_image_any, preprocess_pipeline

logger = logging.getLogger(__name__)


def process_single_document(
    file_path: Path, manual_document_type: Optional[str] = None
) -> dict:
    """
    Runs Modules 2-5 for a single uploaded document.
    Returns a dict with all per-document fields needed downstream.
    """
    raw_img = load_image_any(file_path)
    preprocessed_img, preprocess_meta = preprocess_pipeline(raw_img)

    ocr_result = ocr_service.run_ocr(file_path, preprocessed_img=preprocessed_img)

    if manual_document_type:
        doc_type = manual_document_type
        classification_confidence = 1.0
        requires_manual = False
    else:
        classification = document_classifier.classify_document(ocr_result.lines)
        doc_type = classification.document_type
        classification_confidence = classification.confidence
        requires_manual = document_classifier.needs_manual_selection(classification)

    extracted_fields = field_extraction_service.extract_fields(doc_type, ocr_result.lines)
    validation_result = validation_service.validate_document(doc_type, extracted_fields)

    demo_override = tampering_service.analyze_tampering_demo_override(Path(file_path).name)
    if demo_override:
        tampering_result = demo_override
    else:
        tampering_result = tampering_service.analyze_tampering(file_path, preprocessed_img)

    return {
        "_file_path": file_path,
        "document_type": doc_type,
        "classification_confidence": classification_confidence,
        "requires_manual_selection": requires_manual,
        "ocr_confidence": ocr_result.mean_confidence,
        "raw_text_lines": ocr_result.lines,
        "extracted_fields": extracted_fields,
        "validation": validation_result,
        "tampering": tampering_result,
        "preprocess_meta": preprocess_meta,
        "preprocessed_img": preprocessed_img,
        "raw_img": raw_img,
    }


def run_face_verification(document_results: list[dict], person_photo_path: Optional[Path]) -> Optional[dict]:
    if not person_photo_path:
        return None

    # Use the first document with a detected photograph region as the reference.
    candidate = next(
        (d for d in document_results if d["extracted_fields"].get("photograph_region_detected")),
        document_results[0] if document_results else None,
    )
    if candidate is None:
        return None

    person_img = load_image_any(person_photo_path)
    candidate_doc_path = candidate.get("_file_path", "")
    return face_service.verify_faces(
        document_image_path=candidate_doc_path,
        person_image_path=person_photo_path,
        document_img_bgr=candidate["raw_img"],
        person_img_bgr=person_img,
    )


def run_cross_document_check(document_results: list[dict], document_ids: list[str]) -> Optional[dict]:
    if len(document_results) < 2:
        return {
            "consistency_level": "N/A",
            "comparisons": [],
            "findings": [] if len(document_results) < 1 else [
                "Only one document was provided; cross-document comparison requires 2 or more."
            ],
        }
    payload = [
        {"document_id": doc_id, "document_type": d["document_type"], "fields": d["extracted_fields"]}
        for doc_id, d in zip(document_ids, document_results)
    ]
    return cross_document_service.compare_documents(payload)


def run_risk_engine(
    document_results: list[dict],
    face_result: Optional[dict],
    cross_doc_result: Optional[dict],
) -> dict:
    ocr_confidences = [d["ocr_confidence"] for d in document_results]
    validation_results = [d["validation"] for d in document_results]
    tampering_results = [d["tampering"] for d in document_results]

    return risk_service.compute_risk(
        ocr_confidences=ocr_confidences,
        validation_results=validation_results,
        tampering_results=tampering_results,
        face_result=face_result,
        cross_doc_result=cross_doc_result,
    )
