import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("VeriShield End-to-End Workflow Verification")
print("=" * 60)

# 1. Health & System Info
h_res = client.get("/api/health")
print("Health Check:", h_res.status_code, h_res.json())
assert h_res.status_code == 200

s_res = client.get("/api/system/info")
info = s_res.json()
print("System Info:", s_res.status_code, "App Name:", info["app_name"])
assert info["app_name"] == "VeriShield"

# 2. Demo Scenarios
scenarios = ["genuine_single", "tampered_field", "face_mismatch", "cross_doc_inconsistency"]
for sc in scenarios:
    res = client.post(f"/api/demo/seed/{sc}")
    assert res.status_code == 200, f"{sc} failed: {res.text}"
    data = res.json()
    risk = data["risk_assessment"]
    print(f"\n[Scenario: {sc}]")
    print(f"  Status: {data['status']}")
    print(f"  Risk Level: {risk['risk_level']} (Score: {risk['risk_score']}/100)")
    print(f"  Top Explanation: {risk['explanations'][0] if risk['explanations'] else 'None'}")
    if data.get("face_verification"):
        fv = data["face_verification"]
        print(f"  Face: {fv['match_status']} ({fv['face_similarity']}%)")
    if data.get("cross_document"):
        cd = data["cross_document"]
        print(f"  Cross-Doc: {cd['consistency_level']} consistency")

# 3. Real Multi-Part Document Upload
print("\n" + "=" * 60)
print("Testing Real Multipart Upload (/api/screen)...")
doc_path = backend_dir.parent / "datasets" / "demo_documents" / "demo_aadhaar_genuine.png"
person_path = backend_dir.parent / "datasets" / "demo_documents" / "demo_person_match.png"

with open(doc_path, "rb") as df, open(person_path, "rb") as pf:
    files = [
        ("documents", ("aadhaar_test.png", df, "image/png")),
        ("person_photo", ("person_test.png", pf, "image/png")),
    ]
    data = {"document_types": "aadhaar"}
    upload_res = client.post("/api/screen", files=files, data=data)

assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
res_data = upload_res.json()
print("Multipart Upload Status:", upload_res.status_code)
print("Screening ID:", res_data["screening_id"])
print("Documents Processed:", len(res_data["documents"]))
print("Extracted Name:", res_data["documents"][0]["extracted_fields"]["name"])
print("Validation Status:", res_data["documents"][0]["validation"]["validation_status"])
print("Tampering Score:", res_data["documents"][0]["tampering"]["tampering_score"])
print("Face Status:", res_data["face_verification"]["match_status"])
print("Risk Level:", res_data["risk_assessment"]["risk_level"], f"({res_data['risk_assessment']['risk_score']}/100)")

print("\n" + "=" * 60)
print("ALL VERISHIELD END-TO-END WORKFLOW CHECKS PASSED!")
print("=" * 60)
