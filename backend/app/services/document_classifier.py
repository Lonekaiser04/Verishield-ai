"""
Document Type Detection (Module 2).

Implements a modular, keyword/pattern-based classifier over OCR text.
This is intentionally a transparent, explainable rule-based classifier
rather than a black-box CNN, which suits a screening tool that must
justify its outputs — and it requires no additional model weights to
run in demo environments. The interface (`classify_document`) is the
integration point: a trained image classifier could replace the
internals without changing callers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.config.settings import get_settings

settings = get_settings()


@dataclass
class ClassificationResult:
    document_type: str
    confidence: float
    scores: dict[str, float]


# Keyword and regex signals per document type. Each match adds weight;
# the final confidence is normalized against the strongest competing type.
_SIGNALS: dict[str, dict] = {
    "aadhaar": {
        "keywords": ["government of india", "aadhaar", "unique identification"],
        "patterns": [r"\b\d{4}\s?\d{4}\s?\d{4}\b"],  # 12-digit Aadhaar number format
        "weight_keyword": 0.35,
        "weight_pattern": 0.45,
    },
    "pan": {
        "keywords": ["income tax department", "permanent account number", "pan"],
        "patterns": [r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"],  # PAN format
        "weight_keyword": 0.3,
        "weight_pattern": 0.5,
    },
    "passport": {
        "keywords": ["republic of india", "passport", "nationality", "type: p"],
        "patterns": [r"\bP<[A-Z<]+\b", r"\b[A-Z][0-9]{7}\b"],  # MRZ / passport no.
        "weight_keyword": 0.3,
        "weight_pattern": 0.4,
    },
    "driving_licence": {
        "keywords": ["driving licence", "driving license", "valid till", "licence no"],
        "patterns": [r"\b[A-Z]{2}\d{2}\s?\d{11,13}\b"],
        "weight_keyword": 0.4,
        "weight_pattern": 0.4,
    },
    "voter_id": {
        "keywords": ["election commission", "epic no", "electoral"],
        "patterns": [r"\b[A-Z]{3}\d{7}\b"],  # EPIC number format
        "weight_keyword": 0.4,
        "weight_pattern": 0.4,
    },
}


def classify_document(ocr_lines: list[str]) -> ClassificationResult:
    text = "\n".join(ocr_lines).lower()

    scores: dict[str, float] = {doc_type: 0.0 for doc_type in _SIGNALS}

    for doc_type, cfg in _SIGNALS.items():
        for kw in cfg["keywords"]:
            if kw in text:
                scores[doc_type] += cfg["weight_keyword"]
        for pattern in cfg["patterns"]:
            if re.search(pattern, "\n".join(ocr_lines)):  # patterns are case-sensitive
                scores[doc_type] += cfg["weight_pattern"]

    if not any(scores.values()):
        return ClassificationResult(document_type="unknown", confidence=0.0, scores=scores)

    best_type = max(scores, key=scores.get)
    best_score = min(scores[best_type], 1.0)

    return ClassificationResult(document_type=best_type, confidence=round(best_score, 3), scores=scores)


def needs_manual_selection(result: ClassificationResult) -> bool:
    return result.confidence < settings.CLASSIFIER_CONFIDENCE_THRESHOLD
