"""
Cross-Document Identity Checking Service (Module 7).

Compares extracted fields across multiple uploaded documents (e.g.
Aadhaar vs PAN) and flags inconsistencies. Uses fuzzy string matching
for names to tolerate minor OCR noise (e.g. "Aarav Sharma" vs
"AARAV SHARMA" vs a single dropped character) without being so lenient
that genuinely different names are treated as a match.
"""
from __future__ import annotations

import re
from difflib import SequenceMatcher
from datetime import datetime


_NAME_SIMILARITY_THRESHOLD = 0.82


def _normalize_name(name: str | None) -> str:
    if not name:
        return ""
    name = name.upper()
    name = re.sub(r"[^A-Z\s]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _name_similarity(a: str | None, b: str | None) -> float:
    na, nb = _normalize_name(a), _normalize_name(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def _normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]:
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return value.strip()


def compare_documents(documents: list[dict]) -> dict:
    """
    documents: list of {"document_id": str, "document_type": str, "fields": dict}
    Returns a dict matching schemas.CrossDocumentResponse fields.
    """
    if len(documents) < 2:
        return {
            "consistency_level": "N/A",
            "comparisons": [],
            "findings": ["Only one document was provided; cross-document comparison requires 2 or more."],
        }

    comparisons = []
    findings = []
    inconsistency_count = 0
    comparable_fields = 0

    # --- Name comparison ---
    names = {d["document_id"]: d["fields"].get("name") for d in documents}
    name_values = [v for v in names.values() if v]
    if len(name_values) >= 2:
        comparable_fields += 1
        pairwise_min_similarity = 1.0
        for i in range(len(name_values)):
            for j in range(i + 1, len(name_values)):
                pairwise_min_similarity = min(
                    pairwise_min_similarity, _name_similarity(name_values[i], name_values[j])
                )
        consistent = pairwise_min_similarity >= _NAME_SIMILARITY_THRESHOLD
        if not consistent:
            inconsistency_count += 1
            findings.append(
                f"Name mismatch detected across documents (similarity {pairwise_min_similarity:.0%})."
            )
        comparisons.append(
            {
                "field_name": "name",
                "values": names,
                "consistent": consistent,
                "note": f"Fuzzy match similarity: {pairwise_min_similarity:.0%}",
            }
        )

    # --- Date of birth comparison ---
    dobs = {d["document_id"]: _normalize_date(d["fields"].get("date_of_birth")) for d in documents}
    dob_values = [v for v in dobs.values() if v]
    if len(dob_values) >= 2:
        comparable_fields += 1
        consistent = len(set(dob_values)) == 1
        if not consistent:
            inconsistency_count += 1
            findings.append("Date of Birth is inconsistent across documents.")
        comparisons.append(
            {
                "field_name": "date_of_birth",
                "values": {k: d["fields"].get("date_of_birth") for k, d in zip(dobs.keys(), documents)},
                "consistent": consistent,
                "note": None,
            }
        )

    # --- Gender comparison ---
    genders = {d["document_id"]: d["fields"].get("gender") for d in documents}
    gender_values = [v.strip().upper()[0] for v in genders.values() if v]  # normalize M/Male -> "M"
    if len(gender_values) >= 2:
        comparable_fields += 1
        consistent = len(set(gender_values)) == 1
        if not consistent:
            inconsistency_count += 1
            findings.append("Gender field is inconsistent across documents.")
        comparisons.append(
            {
                "field_name": "gender",
                "values": genders,
                "consistent": consistent,
                "note": None,
            }
        )

    if comparable_fields == 0:
        return {
            "consistency_level": "N/A",
            "comparisons": [],
            "findings": ["No overlapping comparable fields were extracted across the uploaded documents."],
        }

    inconsistency_ratio = inconsistency_count / comparable_fields
    if inconsistency_ratio == 0:
        level = "HIGH"  # HIGH consistency (not to be confused with risk level)
        findings.append("All comparable fields (name, DOB, gender where present) match across documents.")
    elif inconsistency_ratio < 0.5:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"consistency_level": level, "comparisons": comparisons, "findings": findings}
