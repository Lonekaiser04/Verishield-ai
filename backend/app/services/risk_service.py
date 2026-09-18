"""
Explainable Risk Engine (Module 8).

Combines signals from OCR confidence, validation, expiry status,
tampering analysis, face verification, and cross-document consistency
into a single transparent 0-100 risk score with a human-readable
breakdown. Weights are configurable via app/config/settings.py
(environment variables), not hardcoded magic numbers, so the scoring
policy can be tuned without touching this logic.

Score bands (configurable):
  0  - RISK_LOW_MAX      -> LOW RISK
  RISK_LOW_MAX+1 - RISK_MEDIUM_MAX -> MEDIUM RISK
  RISK_MEDIUM_MAX+1 - 100 -> HIGH RISK
"""
from __future__ import annotations

from app.config.settings import get_settings

settings = get_settings()


def _score_ocr_confidence(ocr_confidences: list[float], max_points: float) -> tuple[float, str]:
    """Low OCR confidence contributes risk points (the document may be low quality
    or fields may be misread) but only up to its allotted weight."""
    if not ocr_confidences:
        return max_points, "OCR confidence unavailable for one or more documents."
    avg_conf = sum(ocr_confidences) / len(ocr_confidences)
    if avg_conf >= 85:
        return 0.0, f"OCR confidence is high (avg {avg_conf:.0f}%)."
    if avg_conf >= 60:
        points = max_points * 0.4
        return round(points, 2), f"OCR confidence is moderate (avg {avg_conf:.0f}%); some fields may be uncertain."
    points = max_points
    return round(points, 2), f"OCR confidence is low (avg {avg_conf:.0f}%); extracted fields may be unreliable."


def _score_validation(validation_results: list[dict], max_points: float) -> tuple[float, str]:
    if not validation_results:
        return 0.0, "No validation results available."

    fail_count = sum(1 for v in validation_results if v["status"] == "FAIL")
    warn_count = sum(1 for v in validation_results if v["status"] == "WARN")

    if fail_count > 0:
        points = max_points
        reason = f"{fail_count} document(s) failed format/consistency validation."
    elif warn_count > 0:
        points = max_points * 0.4
        reason = f"{warn_count} document(s) had minor validation warnings."
    else:
        points = 0.0
        reason = "All documents passed format and consistency validation."
    return round(points, 2), reason


def _score_expiry(validation_results: list[dict], max_points: float) -> tuple[float, str]:
    expired = [v for v in validation_results if v.get("expiry_status") == "EXPIRED"]
    if expired:
        return max_points, f"{len(expired)} document(s) are expired."
    return 0.0, "No expired documents detected (or expiry not applicable)."


def _score_tampering(tampering_results: list[dict], max_points: float) -> tuple[float, str]:
    if not tampering_results:
        return 0.0, "No tampering analysis available."
    max_score = max(t["tampering_score"] for t in tampering_results)
    points = max_points * (max_score / 100.0)
    if max_score >= 55:
        reason = f"High tampering indicator score detected (peak {max_score:.0f}/100)."
    elif max_score >= 25:
        reason = f"Moderate tampering indicator score detected (peak {max_score:.0f}/100)."
    else:
        reason = f"Low tampering indicator score (peak {max_score:.0f}/100)."
    return round(points, 2), reason


def _score_face(face_result: dict | None, max_points: float) -> tuple[float, str]:
    if face_result is None:
        return 0.0, "No face verification was performed (no person photo supplied)."
    similarity = face_result["face_similarity"]
    status = face_result["match_status"]
    if status == "NO FACE DETECTED":
        return max_points, "No face could be detected for verification."
    if status == "LIKELY MISMATCH":
        return max_points, f"Face similarity is low ({similarity:.0f}%), suggesting a likely mismatch."
    if status == "MANUAL REVIEW REQUIRED":
        points = max_points * 0.5
        return round(points, 2), f"Face similarity ({similarity:.0f}%) falls in the manual-review range."
    return 0.0, f"Face similarity is high ({similarity:.0f}%), consistent with a match."


def _score_cross_doc(cross_doc_result: dict | None, max_points: float) -> tuple[float, str]:
    if cross_doc_result is None or cross_doc_result["consistency_level"] == "N/A":
        return 0.0, "Cross-document comparison not applicable (single document)."
    level = cross_doc_result["consistency_level"]
    if level == "LOW":
        return max_points, "Multiple fields are inconsistent across the submitted documents."
    if level == "MEDIUM":
        points = max_points * 0.5
        return round(points, 2), "Some fields are inconsistent across the submitted documents."
    return 0.0, "Submitted documents are consistent with each other."


def compute_risk(
    ocr_confidences: list[float],
    validation_results: list[dict],
    tampering_results: list[dict],
    face_result: dict | None,
    cross_doc_result: dict | None,
) -> dict:
    weights = {
        "ocr_confidence": settings.RISK_WEIGHT_OCR_CONFIDENCE,
        "validation": settings.RISK_WEIGHT_VALIDATION,
        "expiry": settings.RISK_WEIGHT_EXPIRY,
        "tampering": settings.RISK_WEIGHT_TAMPERING,
        "face": settings.RISK_WEIGHT_FACE,
        "cross_document": settings.RISK_WEIGHT_CROSS_DOC,
    }

    ocr_points, ocr_reason = _score_ocr_confidence(ocr_confidences, weights["ocr_confidence"])
    val_points, val_reason = _score_validation(validation_results, weights["validation"])
    exp_points, exp_reason = _score_expiry(validation_results, weights["expiry"])
    tamper_points, tamper_reason = _score_tampering(tampering_results, weights["tampering"])
    face_points, face_reason = _score_face(face_result, weights["face"])
    cross_points, cross_reason = _score_cross_doc(cross_doc_result, weights["cross_document"])

    total = round(ocr_points + val_points + exp_points + tamper_points + face_points + cross_points, 2)
    total = min(total, 100.0)

    # Escalation rule: certain individual findings are severe enough on
    # their own to warrant HIGH RISK regardless of the weighted total,
    # even if every other category looks clean. This mirrors how a human
    # reviewer would treat a confirmed face mismatch or a document that
    # actively fails validation as a hard stop rather than "average it
    # in with everything else that looked fine." The weighted score and
    # per-category breakdown are still reported in full for transparency;
    # this only affects the final LOW/MEDIUM/HIGH label.
    escalation_reasons: list[str] = []
    if face_result is not None and face_result["match_status"] in ("LIKELY MISMATCH", "NO FACE DETECTED"):
        escalation_reasons.append("A confirmed face mismatch was detected against the submitted person photo.")
    if cross_doc_result is not None and cross_doc_result["consistency_level"] == "LOW":
        escalation_reasons.append("Submitted documents show inconsistent identity fields with each other.")
    if any(t["tampering_level"] == "HIGH" for t in tampering_results):
        escalation_reasons.append("At least one document shows a high tampering indicator score.")

    if total <= settings.RISK_LOW_MAX:
        level = "LOW RISK"
    elif total <= settings.RISK_MEDIUM_MAX:
        level = "MEDIUM RISK"
    else:
        level = "HIGH RISK"

    if escalation_reasons and level != "HIGH RISK":
        level = "HIGH RISK"

    breakdown = [
        {"category": "OCR Confidence", "points_awarded": ocr_points, "max_points": weights["ocr_confidence"], "reason": ocr_reason},
        {"category": "Document Validation", "points_awarded": val_points, "max_points": weights["validation"], "reason": val_reason},
        {"category": "Expiry Check", "points_awarded": exp_points, "max_points": weights["expiry"], "reason": exp_reason},
        {"category": "Tampering Analysis", "points_awarded": tamper_points, "max_points": weights["tampering"], "reason": tamper_reason},
        {"category": "Face Verification", "points_awarded": face_points, "max_points": weights["face"], "reason": face_reason},
        {"category": "Cross-Document Consistency", "points_awarded": cross_points, "max_points": weights["cross_document"], "reason": cross_reason},
    ]

    # Explanations list: surface only the categories that actually
    # contributed risk points, ordered by contribution (highest first),
    # so the report reads like a prioritized list of reasons rather than
    # a rote recap of every category.
    explanations = [
        f"{item['category']}: {item['reason']}"
        for item in sorted(breakdown, key=lambda x: -x["points_awarded"])
        if item["points_awarded"] > 0
    ]
    if escalation_reasons:
        explanations = [f"Escalated to HIGH RISK: {r}" for r in escalation_reasons] + explanations
    if not explanations:
        explanations = ["No significant risk indicators were found across any screening category."]

    return {
        "risk_score": total,
        "risk_level": level,
        "breakdown": breakdown,
        "explanations": explanations,
        "weights_used": weights,
        "escalated": bool(escalation_reasons),
    }
