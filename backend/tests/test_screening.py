"""
VeriShield automated test suite.

Tests:
1. System Info & Health endpoints
2. Document Type Classifier (all 5 document types)
3. Structured Field Extraction & MRZ parsing
4. Document Validation rules (valid, invalid, expired)
5. Tampering & Forensics Detection (ELA, noise, copy-move, metadata)
6. Face Verification pipeline (detection, representation, cosine similarity)
7. Cross-Document Identity Checking (fuzzy name, DOB, gender)
8. Explainable Risk Engine (weights, thresholds, escalation rules)
9. End-to-end API screening (demo seeds & standalone modules)
"""
import pytest
from pathlib import Path
import numpy as np
from fastapi.testclient import TestClient

from app.main import app
from app.config.settings import get_settings
from app.services import (
    document_classifier,
    field_extraction_service,
    validation_service,
    tampering_service,
    face_service,
    cross_document_service,
    risk_service,
)

client = TestClient(app)
settings = get_settings()


# ---------------------------------------------------------------------------
# 1. System Info & Naming
# ---------------------------------------------------------------------------


def test_system_info_and_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}

    info_resp = client.get("/api/system/info")
    assert info_resp.status_code == 200
    info = info_resp.json()
    assert info["app_name"] == "VeriShield"
    assert "aadhaar" in info["supported_document_types"]
    assert "pan" in info["supported_document_types"]
    assert "passport" in info["supported_document_types"]


# ---------------------------------------------------------------------------
# 2. Document Classifier
# ---------------------------------------------------------------------------


def test_document_classifier():
    aadhaar_lines = ["GOVERNMENT OF INDIA", "Name: Aarav Sharma", "1234 5678 9012"]
    res = document_classifier.classify_document(aadhaar_lines)
    assert res.document_type == "aadhaar"
    assert res.confidence > 0.5

    pan_lines = ["INCOME TAX DEPARTMENT", "Permanent Account Number", "ABCDE1234F"]
    res = document_classifier.classify_document(pan_lines)
    assert res.document_type == "pan"
    assert res.confidence > 0.5

    passport_lines = ["REPUBLIC OF INDIA", "PASSPORT", "N1234567", "P<INDSHARMA<<AARAV"]
    res = document_classifier.classify_document(passport_lines)
    assert res.document_type == "passport"

    dl_lines = ["DRIVING LICENCE", "Licence No: MH12 20150012345", "Valid Till: 09/06/2035"]
    res = document_classifier.classify_document(dl_lines)
    assert res.document_type == "driving_licence"

    voter_lines = ["ELECTION COMMISSION OF INDIA", "EPIC No: ABC1234567"]
    res = document_classifier.classify_document(voter_lines)
    assert res.document_type == "voter_id"


# ---------------------------------------------------------------------------
# 3. Field Extraction
# ---------------------------------------------------------------------------


def test_field_extraction_and_mrz():
    aadhaar_lines = [
        "Government of India",
        "Name: Aarav Sharma",
        "DOB: 14/03/1995",
        "Gender: Male",
        "1234 5678 9012",
        "Address: 12 MG Road, Pune",
    ]
    fields = field_extraction_service.extract_fields("aadhaar", aadhaar_lines)
    assert fields["name"] == "Aarav Sharma"
    assert fields["date_of_birth"] == "14/03/1995"
    assert fields["document_number"] == "1234 5678 9012"
    assert fields["gender"] == "Male"

    # Test MRZ parsing
    mrz_raw = (
        "P<INDSHARMA<<AARAV<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
        "N1234567<4IND9503148M3105202<<<<<<<<<<<<<<08"
    )
    parsed_mrz = field_extraction_service.parse_mrz(mrz_raw)
    assert parsed_mrz is not None
    assert parsed_mrz["document_number"] == "N1234567"
    assert parsed_mrz["sex"] == "M"


# ---------------------------------------------------------------------------
# 4. Document Validation
# ---------------------------------------------------------------------------


def test_document_validation():
    # Valid Aadhaar
    val = validation_service.validate_document(
        "aadhaar",
        {"name": "Aarav Sharma", "date_of_birth": "14/03/1995", "document_number": "1234 5678 9012"},
    )
    assert val["status"] == "PASS"
    assert len(val["issues"]) == 0

    # Invalid PAN format
    val_pan = validation_service.validate_document(
        "pan",
        {"name": "Aarav Sharma", "document_number": "INVALID123", "date_of_birth": "14/03/1995"},
    )
    assert val_pan["status"] == "FAIL"
    assert any("format" in issue.lower() for issue in val_pan["issues"])

    # Expired Passport
    val_pass = validation_service.validate_document(
        "passport",
        {
            "name": "Aarav Sharma",
            "document_number": "N1234567",
            "expiry_date": "01/01/2010",
        },
    )
    assert val_pass["expiry_status"] == "EXPIRED"
    assert val_pass["status"] == "FAIL"


# ---------------------------------------------------------------------------
# 5. Tampering Detection
# ---------------------------------------------------------------------------


def test_tampering_analysis():
    # Synthetic flat image
    img = np.full((200, 300, 3), 240, dtype=np.uint8)
    res = tampering_service.analyze_tampering(Path("test_dummy.png"), img)
    assert "tampering_score" in res
    assert "tampering_level" in res
    assert "explanation" in res
    assert "potential tampering indicators" in res["explanation"].lower() or "no significant" in res["explanation"].lower()
    assert res["tampering_score"] >= 0.0


# ---------------------------------------------------------------------------
# 6. Face Verification
# ---------------------------------------------------------------------------


def test_face_verification():
    # Synthetic portraits
    face1 = np.full((128, 128, 3), 200, dtype=np.uint8)
    face2 = np.full((128, 128, 3), 200, dtype=np.uint8)

    emb1 = face_service.extract_face_embedding(face1)
    emb2 = face_service.extract_face_embedding(face2)

    if emb1 is not None and emb2 is not None:
        sim = face_service.compute_cosine_similarity(emb1, emb2)
        assert 0.0 <= sim <= 100.0

    # Test verify_faces call
    res = face_service.verify_faces(
        document_image_path="test_doc.png",
        person_image_path="test_person.png",
        document_img_bgr=face1,
        person_img_bgr=face2,
    )
    assert "face_similarity" in res
    assert "match_status" in res
    assert res["match_status"] in ("LIKELY MATCH", "MANUAL REVIEW REQUIRED", "LIKELY MISMATCH", "NO FACE DETECTED")


# ---------------------------------------------------------------------------
# 7. Cross-Document Consistency
# ---------------------------------------------------------------------------


def test_cross_document_comparison():
    # Consistent docs
    docs_match = [
        {"document_id": "1", "document_type": "aadhaar", "fields": {"name": "Aarav Sharma", "date_of_birth": "14/03/1995"}},
        {"document_id": "2", "document_type": "pan", "fields": {"name": "AARAV SHARMA", "date_of_birth": "14/03/1995"}},
    ]
    res_match = cross_document_service.compare_documents(docs_match)
    assert res_match["consistency_level"] == "HIGH"

    # Conflicting DOB docs
    docs_diff = [
        {"document_id": "1", "document_type": "aadhaar", "fields": {"name": "Aarav Sharma", "date_of_birth": "14/03/1995"}},
        {"document_id": "2", "document_type": "pan", "fields": {"name": "Aarav Sharma", "date_of_birth": "14/03/1998"}},
    ]
    res_diff = cross_document_service.compare_documents(docs_diff)
    assert res_diff["consistency_level"] in ("LOW", "MEDIUM")


# ---------------------------------------------------------------------------
# 8. Risk Engine & Escalation
# ---------------------------------------------------------------------------


def test_risk_engine():
    # Low risk clean scenario
    risk = risk_service.compute_risk(
        ocr_confidences=[95.0],
        validation_results=[{"status": "PASS", "issues": []}],
        tampering_results=[{"tampering_score": 5.0, "tampering_level": "LOW"}],
        face_result={"face_similarity": 95.0, "match_status": "LIKELY MATCH"},
        cross_doc_result=None,
    )
    assert risk["risk_level"] == "LOW RISK"
    assert risk["risk_score"] <= settings.RISK_LOW_MAX

    # High risk face mismatch escalation
    risk_escalated = risk_service.compute_risk(
        ocr_confidences=[95.0],
        validation_results=[{"status": "PASS", "issues": []}],
        tampering_results=[{"tampering_score": 5.0, "tampering_level": "LOW"}],
        face_result={"face_similarity": 15.0, "match_status": "LIKELY MISMATCH"},
        cross_doc_result=None,
    )
    assert risk_escalated["risk_level"] == "HIGH RISK"
    assert risk_escalated["escalated"] is True


# ---------------------------------------------------------------------------
# 9. API Routes End-to-End
# ---------------------------------------------------------------------------


def test_api_demo_seed_and_results():
    resp = client.post("/api/demo/seed/genuine_single")
    assert resp.status_code == 200
    data = resp.json()
    screening_id = data["screening_id"]
    assert data["status"] == "completed"
    assert len(data["documents"]) == 1
    assert data["risk_assessment"]["risk_level"] in ("LOW RISK", "MEDIUM RISK", "HIGH RISK")

    # Fetch result by ID
    get_resp = client.get(f"/api/screenings/{screening_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["screening_id"] == screening_id


def test_standalone_validate_api():
    req = {
        "document_type": "aadhaar",
        "fields": {
            "name": "Aarav Sharma",
            "date_of_birth": "14/03/1995",
            "document_number": "1234 5678 9012",
        },
    }
    resp = client.post("/api/documents/validate", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["validation_status"] == "PASS"


def test_standalone_compare_api():
    req = {
        "documents": [
            {
                "document_id": "doc1",
                "document_type": "aadhaar",
                "fields": {"name": "Aarav Sharma", "date_of_birth": "14/03/1995"},
            },
            {
                "document_id": "doc2",
                "document_type": "pan",
                "fields": {"name": "AARAV SHARMA", "date_of_birth": "14/03/1995"},
            },
        ]
    }
    resp = client.post("/api/identity/compare", json=req)
    assert resp.status_code == 200
    data = resp.json()
    assert data["consistency_level"] == "HIGH"


def test_screen_multipart_upload():
    doc_path = Path("datasets/demo_documents/demo_aadhaar_genuine.png")
    person_path = Path("datasets/demo_documents/demo_person_match.png")

    with open(doc_path, "rb") as df, open(person_path, "rb") as pf:
        files = [
            ("documents", ("test_aadhaar.png", df, "image/png")),
            ("person_photo", ("test_person.png", pf, "image/png")),
        ]
        data = {"document_types": "aadhaar"}
        resp = client.post("/api/screen", files=files, data=data)

    assert resp.status_code == 200
    res = resp.json()
    assert res["status"] == "completed"
    assert len(res["documents"]) == 1
    assert res["documents"][0]["document_type"] == "aadhaar"
    assert res["face_verification"] is not None
    assert "risk_assessment" in res
    assert res["risk_assessment"]["risk_score"] >= 0.0

