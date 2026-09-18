"""
Document Validation Service (Module 4).

Performs FORMAT validation and internal logical consistency checks only.
This module explicitly does NOT and CANNOT verify a document against any
government database or authoritative record — that distinction is
surfaced in every response via the `disclaimer` field on
ValidationResponse (see schemas/screening.py).

A separate validator function exists per document type so rules can be
extended independently (e.g. adding a "visa" validator later).
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from app.services.field_extraction_service import parse_mrz

_DATE_FORMATS = ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"]


def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def _check_expiry(expiry_str: Optional[str]) -> str:
    dt = _parse_date(expiry_str)
    if dt is None:
        return "N/A" if not expiry_str else "UNKNOWN"
    return "VALID" if dt >= datetime.now() else "EXPIRED"


def validate_aadhaar(fields: dict) -> dict:
    issues: list[str] = []
    notes: list[str] = []

    if not fields.get("name"):
        issues.append("Name field could not be read or is missing.")
    dob = fields.get("date_of_birth")
    if not dob:
        issues.append("Date of Birth field could not be read or is missing.")
    elif _parse_date(dob) is None:
        issues.append(f"Date of Birth '{dob}' is not in a recognized date format.")

    number = fields.get("document_number")
    if not number:
        issues.append("Aadhaar number could not be read.")
    else:
        digits = re.sub(r"\s", "", number)
        if len(digits) != 12 or not digits.isdigit():
            issues.append("Aadhaar number does not match the expected 12-digit format.")

    status = "FAIL" if issues else "PASS"
    return {"status": status, "issues": issues, "expiry_status": "N/A", "notes": notes}


def validate_pan(fields: dict) -> dict:
    issues: list[str] = []
    notes: list[str] = []

    if not fields.get("name"):
        issues.append("Name field could not be read or is missing.")

    number = fields.get("document_number")
    if not number:
        issues.append("PAN number could not be read.")
    elif not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", number):
        issues.append("PAN number does not match the expected format (5 letters, 4 digits, 1 letter).")

    dob = fields.get("date_of_birth")
    if dob and _parse_date(dob) is None:
        issues.append(f"Date of Birth '{dob}' is not in a recognized date format.")

    status = "FAIL" if issues else "PASS"
    return {"status": status, "issues": issues, "expiry_status": "N/A", "notes": notes}


def validate_passport(fields: dict) -> dict:
    issues: list[str] = []
    notes: list[str] = []
    mrz_match: Optional[bool] = None

    if not fields.get("name"):
        issues.append("Name field could not be read or is missing.")

    number = fields.get("document_number")
    if not number:
        issues.append("Passport number could not be read.")
    elif not re.fullmatch(r"[A-Z][0-9]{7}", number):
        issues.append("Passport number does not match the expected format.")

    expiry_status = _check_expiry(fields.get("expiry_date"))
    if expiry_status == "EXPIRED":
        issues.append("Passport expiry date has passed.")

    mrz_raw = fields.get("mrz_raw")
    mrz_parsed = parse_mrz(mrz_raw)
    if mrz_parsed:
        mrz_match = True
        mrz_doc_no = mrz_parsed.get("document_number", "")
        if number and mrz_doc_no and number.replace(" ", "") != mrz_doc_no.replace(" ", ""):
            mrz_match = False
            issues.append(
                "Passport number in the visual (printed) zone does not match the "
                "number encoded in the Machine Readable Zone (MRZ)."
            )
        notes.append("MRZ fields were parsed and cross-checked against printed fields where possible.")
    else:
        notes.append("MRZ was not detected or could not be parsed; MRZ cross-check skipped.")

    status = "FAIL" if issues else "PASS"
    return {
        "status": status,
        "issues": issues,
        "expiry_status": expiry_status,
        "mrz_match": mrz_match,
        "notes": notes,
    }


def validate_driving_licence(fields: dict) -> dict:
    issues: list[str] = []
    notes: list[str] = []

    if not fields.get("name"):
        issues.append("Name field could not be read or is missing.")

    number = fields.get("document_number")
    if not number:
        issues.append("Driving licence number could not be read.")

    issue_date = _parse_date(fields.get("issue_date"))
    expiry_status = _check_expiry(fields.get("expiry_date"))
    if expiry_status == "EXPIRED":
        issues.append("Driving licence validity ('Valid Till') date has passed.")

    expiry_date = _parse_date(fields.get("expiry_date"))
    if issue_date and expiry_date and expiry_date <= issue_date:
        issues.append("Expiry date is not after the issue date — logically inconsistent.")

    status = "FAIL" if issues else "PASS"
    return {"status": status, "issues": issues, "expiry_status": expiry_status, "notes": notes}


def validate_voter_id(fields: dict) -> dict:
    issues: list[str] = []
    notes: list[str] = []

    if not fields.get("name"):
        issues.append("Name field could not be read or is missing.")

    number = fields.get("document_number")
    if not number:
        issues.append("EPIC (Voter ID) number could not be read.")
    elif not re.fullmatch(r"[A-Z]{3}\d{7}", number):
        issues.append("EPIC number does not match the expected format (3 letters + 7 digits).")

    age_or_dob = fields.get("date_of_birth")
    if age_or_dob and age_or_dob.isdigit():
        age = int(age_or_dob)
        if age < 18:
            issues.append("Stated age is below the legal voting age of 18.")
        if age > 120:
            issues.append("Stated age is implausibly high.")

    status = "FAIL" if issues else "PASS"
    return {"status": status, "issues": issues, "expiry_status": "N/A", "notes": notes}


_VALIDATORS = {
    "aadhaar": validate_aadhaar,
    "pan": validate_pan,
    "passport": validate_passport,
    "driving_licence": validate_driving_licence,
    "voter_id": validate_voter_id,
}


def validate_document(document_type: str, fields: dict) -> dict:
    validator = _VALIDATORS.get(document_type)
    if not validator:
        return {
            "status": "WARN",
            "issues": ["Unknown document type; only generic checks were applied."],
            "expiry_status": "N/A",
            "notes": [],
        }
    result = validator(fields)
    # A single missing/unreadable field is treated as WARN rather than FAIL
    # when it's the only issue, since OCR misses are common and shouldn't
    # alone imply fraud; multiple issues or a format violation is FAIL.
    if result["status"] == "FAIL" and len(result["issues"]) == 1 and "could not be read" in result["issues"][0]:
        result["status"] = "WARN"
    return result
