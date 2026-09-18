"""
Demo Mode data (Module: Demo Mode).

All values here are 100% SYNTHETIC. No real government identity numbers,
real names, or real document images are used anywhere in this module.
Aadhaar/PAN/Passport/DL/Voter ID number formats follow publicly documented
FORMAT PATTERNS ONLY (e.g. "PAN is 5 letters + 4 digits + 1 letter") and do
not correspond to any real, issued document.

This module is the single source of truth for demo scenarios so the
frontend, OCR fallback, and API demo-seed endpoint all stay consistent.
"""
from __future__ import annotations

# Filenames referenced here correspond to synthetic placeholder images
# generated in datasets/demo_documents/ (see datasets/README.md).

DEMO_OCR_TEXT: dict[str, list[str]] = {
    "demo_aadhaar_genuine.png": [
        "GOVERNMENT OF INDIA (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "DOB: 14/03/1995",
        "Gender: Male",
        "1234 5678 9012",
        "Address: 12 MG Road, Pune, Maharashtra",
    ],
    "demo_pan_genuine.png": [
        "INCOME TAX DEPARTMENT (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "Father's Name: Ramesh Sharma",
        "Date of Birth: 14/03/1995",
        "Permanent Account Number",
        "ABCDE1234F",
    ],
    "demo_passport_genuine.png": [
        "REPUBLIC OF INDIA (SYNTHETIC SAMPLE)",
        "Type: P   Code: IND",
        "Passport No: N1234567",
        "Surname: SHARMA",
        "Given Name: AARAV",
        "Nationality: INDIAN",
        "DOB: 14/03/1995   Sex: M",
        "Date of Expiry: 20/05/2031",
        "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<",
        "N1234567<4IND9503148M3105202<<<<<<<<<<<<<<08",
    ],
    "demo_dl_genuine.png": [
        "DRIVING LICENCE (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "DOB: 14/03/1995",
        "Licence No: MH12 20150012345",
        "Issue Date: 10/06/2015",
        "Valid Till: 09/06/2035",
    ],
    "demo_voter_genuine.png": [
        "ELECTION COMMISSION OF INDIA (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "Father's Name: Ramesh Sharma",
        "Age: 29",
        "Gender: Male",
        "EPIC No: ABC1234567",
    ],
    # Tampered scenario: DOB and PAN number show manipulation indicators
    "demo_pan_tampered.png": [
        "INCOME TAX DEPARTMENT (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "Father's Name: Ramesh Sharma",
        "Date of Birth: 14/03/1998",  # inconsistent with Aadhaar (1995)
        "Permanent Account Number",
        "ABCDE1234F",
    ],
    # Face mismatch scenario reuses genuine Aadhaar text; mismatch is
    # introduced at the face-embedding level, not OCR.
    "demo_aadhaar_facemismatch.png": [
        "GOVERNMENT OF INDIA (SYNTHETIC SAMPLE)",
        "Name: Aarav Sharma",
        "DOB: 14/03/1995",
        "Gender: Male",
        "1234 5678 9012",
        "Address: 12 MG Road, Pune, Maharashtra",
    ],
}


# Demo scenario definitions consumed by /api/demo/seed and the frontend's
# "Try a demo scenario" picker.
DEMO_SCENARIOS = [
    {
        "id": "genuine_single",
        "title": "Genuine document (single upload)",
        "description": "A single, well-formed synthetic Aadhaar card with no anomalies.",
        "expected_risk": "LOW RISK",
        "documents": ["demo_aadhaar_genuine.png"],
        "person_photo": "demo_person_match.png",
    },
    {
        "id": "tampered_field",
        "title": "Potentially tampered field",
        "description": (
            "A synthetic PAN card whose Date of Birth field shows edit "
            "indicators and is inconsistent with a companion Aadhaar card."
        ),
        "expected_risk": "MEDIUM/HIGH RISK",
        "documents": ["demo_aadhaar_genuine.png", "demo_pan_tampered.png"],
        "person_photo": "demo_person_match.png",
    },
    {
        "id": "face_mismatch",
        "title": "Face mismatch",
        "description": "Document photo does not match the uploaded person photo.",
        "expected_risk": "HIGH RISK",
        "documents": ["demo_aadhaar_facemismatch.png"],
        "person_photo": "demo_person_mismatch.png",
    },
    {
        "id": "cross_doc_inconsistency",
        "title": "Multiple document inconsistency",
        "description": "Aadhaar and PAN uploaded together with conflicting DOB, plus a mismatched person photo.",
        "expected_risk": "HIGH RISK",
        "documents": ["demo_aadhaar_genuine.png", "demo_pan_tampered.png"],
        "person_photo": "demo_person_mismatch.png",
    },
]

# Synthetic "face embeddings" used only in DEMO_MODE when no real face
# recognition model is available. These are small deterministic vectors
# used purely to demonstrate the similarity-scoring pipeline end-to-end.
DEMO_FACE_SIMILARITY_OVERRIDES: dict[tuple[str, str], float] = {
    ("demo_aadhaar_genuine.png", "demo_person_match.png"): 93.5,
    ("demo_aadhaar_facemismatch.png", "demo_person_mismatch.png"): 12.0,
    ("demo_aadhaar_genuine.png", "demo_person_mismatch.png"): 15.0,
}
