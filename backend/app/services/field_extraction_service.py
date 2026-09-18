"""
Structured Field Extraction (Module 3, continued).

Parses document-specific fields out of raw OCR text lines using
regex/heuristic rules per document type. Kept separate from
ocr_service.py so the OCR engine can be swapped without touching
field-parsing logic, and so each document type's parsing rules are
easy to audit and extend independently (e.g. adding "visa" later).
"""
from __future__ import annotations

import re
from typing import Optional


_DATE_PATTERN = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")
_AADHAAR_PATTERN = re.compile(r"\b(\d{4}\s?\d{4}\s?\d{4})\b")
_PAN_PATTERN = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b")
_PASSPORT_NO_PATTERN = re.compile(r"\b([A-Z][0-9]{7})\b")
_DL_NO_PATTERN = re.compile(r"\b([A-Z]{2}\d{2}\s?\d{11,13})\b")
_EPIC_PATTERN = re.compile(r"\b([A-Z]{3}\d{7})\b")
_MRZ_LINE_PATTERN = re.compile(r"^[A-Z0-9<]{20,}$")


def _find_after_label(lines: list[str], labels: list[str]) -> Optional[str]:
    """Find a value on the same line after a 'Label: value' pattern."""
    for line in lines:
        for label in labels:
            m = re.search(rf"{label}\s*[:\-]\s*(.+)", line, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
    return None


def _find_date(lines: list[str], labels: list[str] | None = None) -> Optional[str]:
    if labels:
        for line in lines:
            for label in labels:
                if label.lower() in line.lower():
                    m = _DATE_PATTERN.search(line)
                    if m:
                        return m.group(1)
    for line in lines:
        m = _DATE_PATTERN.search(line)
        if m:
            return m.group(1)
    return None


def extract_aadhaar_fields(lines: list[str]) -> dict:
    text = "\n".join(lines)
    fields = {
        "name": _find_after_label(lines, ["name"]),
        "date_of_birth": _find_date(lines, ["dob", "birth"]),
        "gender": _find_after_label(lines, ["gender", "sex"]),
        "address": _find_after_label(lines, ["address"]),
        "document_number": None,
        "photograph_region_detected": True,  # assumed present on ID-style cards
    }
    m = _AADHAAR_PATTERN.search(text)
    if m:
        fields["document_number"] = m.group(1)
    return fields


def extract_pan_fields(lines: list[str]) -> dict:
    text = "\n".join(lines)
    fields = {
        "name": _find_after_label(lines, ["name"]),
        "parent_name": _find_after_label(lines, ["father's name", "fathers name", "father name"]),
        "date_of_birth": _find_date(lines, ["dob", "date of birth"]),
        "document_number": None,
        "photograph_region_detected": True,
    }
    m = _PAN_PATTERN.search(text)
    if m:
        fields["document_number"] = m.group(1)
    return fields


def extract_passport_fields(lines: list[str]) -> dict:
    text = "\n".join(lines)
    mrz_lines = [l for l in lines if _MRZ_LINE_PATTERN.match(l.replace(" ", ""))]
    fields = {
        "name": _find_after_label(lines, ["given name", "surname"]) or _find_after_label(lines, ["name"]),
        "date_of_birth": _find_date(lines, ["dob"]),
        "gender": _find_after_label(lines, ["sex"]),
        "nationality": _find_after_label(lines, ["nationality"]),
        "expiry_date": _find_date(lines, ["date of expiry", "expiry"]),
        "document_number": None,
        "mrz_raw": "\n".join(mrz_lines) if mrz_lines else None,
        "photograph_region_detected": True,
    }
    m = _PASSPORT_NO_PATTERN.search(text)
    if m:
        fields["document_number"] = m.group(1)
    return fields


def extract_dl_fields(lines: list[str]) -> dict:
    text = "\n".join(lines)
    fields = {
        "name": _find_after_label(lines, ["name"]),
        "date_of_birth": _find_date(lines, ["dob"]),
        "issue_date": _find_date(lines, ["issue date"]),
        "expiry_date": _find_date(lines, ["valid till", "expiry", "valid upto"]),
        "document_number": None,
        "photograph_region_detected": True,
    }
    m = _DL_NO_PATTERN.search(text)
    if m:
        fields["document_number"] = m.group(1)
    return fields


def extract_voter_id_fields(lines: list[str]) -> dict:
    text = "\n".join(lines)
    fields = {
        "name": _find_after_label(lines, ["name"]),
        "parent_name": _find_after_label(lines, ["father's name", "fathers name"]),
        "date_of_birth": _find_after_label(lines, ["age"]),  # Voter ID often shows age, not DOB
        "gender": _find_after_label(lines, ["gender", "sex"]),
        "document_number": None,
        "photograph_region_detected": True,
    }
    m = _EPIC_PATTERN.search(text)
    if m:
        fields["document_number"] = m.group(1)
    return fields


_EXTRACTORS = {
    "aadhaar": extract_aadhaar_fields,
    "pan": extract_pan_fields,
    "passport": extract_passport_fields,
    "driving_licence": extract_dl_fields,
    "voter_id": extract_voter_id_fields,
}


def extract_fields(document_type: str, lines: list[str]) -> dict:
    extractor = _EXTRACTORS.get(document_type)
    if not extractor:
        return {"photograph_region_detected": False}
    return extractor(lines)


def parse_mrz(mrz_raw: str | None) -> dict | None:
    """
    Very small MRZ (Machine Readable Zone) parser for TD3 passport format
    (2 lines x 44 chars). Extracts document number, DOB, sex, and expiry
    from the second MRZ line for cross-checking against visual OCR fields.
    """
    if not mrz_raw:
        return None
    lines = [l.replace(" ", "") for l in mrz_raw.splitlines() if l.strip()]
    if len(lines) < 2:
        return None
    line2 = lines[1]
    if len(line2) < 20:
        return None
    try:
        doc_number = line2[0:9].replace("<", "")
        dob_raw = line2[13:19]  # YYMMDD
        sex = line2[20] if len(line2) > 20 else None
        expiry_raw = line2[21:27] if len(line2) > 27 else None
        return {
            "document_number": doc_number,
            "dob_yymmdd": dob_raw,
            "sex": sex,
            "expiry_yymmdd": expiry_raw,
        }
    except Exception:  # noqa: BLE001
        return None
