# Architecture Notes

See the main [README.md](../README.md) for the full pipeline diagram,
tech stack, and setup instructions. This file adds a few implementation
details useful when extending the system.

## Adding a new document type (e.g. "visa")

The system was designed so a new document type touches exactly four files:

1. **`backend/app/services/document_classifier.py`** — add a new entry to
   `_SIGNALS` with keywords/regex patterns that identify the document type
   from OCR text.
2. **`backend/app/services/field_extraction_service.py`** — add an
   `extract_<type>_fields(lines)` function and register it in `_EXTRACTORS`.
3. **`backend/app/services/validation_service.py`** — add a
   `validate_<type>(fields)` function and register it in `_VALIDATORS`.
4. **`backend/app/schemas/screening.py`** — add the new value to the
   `DocumentType` enum.

No changes are needed to the tampering, face verification, cross-document,
or risk engine services — they operate generically on any document type's
extracted fields and image data.

## Swapping SQLite for PostgreSQL

Set `DATABASE_URL` in `backend/.env` to a PostgreSQL DSN, e.g.:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/verishield
```

...and uncomment `psycopg2-binary` in `backend/requirements.txt`. No model
or service code changes are required — `backend/app/database/session.py`
only uses standard SQLAlchemy ORM features with no SQLite-specific SQL.

## Swapping the OCR engine

`backend/app/services/ocr_service.py` exposes a single entry point,
`run_ocr(image_path, preprocessed_img=None) -> OCRResult`. To use a
different OCR engine (e.g. Tesseract, Azure Document Intelligence, Google
Vision), replace the internals of this function while keeping the
`OCRResult(lines, mean_confidence, boxes)` return shape — no other module
needs to change.

## Swapping the face verification model

Similarly, `backend/app/services/face_service.py` exposes
`verify_faces(document_image_path, person_image_path, document_img_bgr,
person_img_bgr) -> dict`. Any pretrained face-verification model can be
substituted as long as it returns a dict with `face_similarity`,
`match_status`, `confidence`, and `notes`.

## Risk engine weight tuning

All risk weights and score-band thresholds are environment variables (see
`backend/.env.example` and `backend/app/config/settings.py`) — no code
changes are needed to re-tune the scoring policy. The weighted score and
the escalation rule (severe individual findings forcing HIGH RISK) are
implemented in `backend/app/services/risk_service.py::compute_risk`.
