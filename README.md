# VeriShield

An AI-assisted, multi-document identity preliminary screening system that analyzes
Aadhaar, PAN, Passport, Driving Licence, and Voter ID documents for
formatting issues, potential tampering indicators, and cross-document
inconsistencies — producing a **LOW / MEDIUM / HIGH** risk assessment with
transparent, human-readable explanations.

> **VeriShield is an AI-assisted screening and decision-support tool.** It does
> **not** verify documents against any government database, and it does
> **not** guarantee that any document is genuine or fraudulent. All outputs
> are risk indicators intended to support human review — not a final
> determination.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Technology Stack](#technology-stack)
5. [Installation](#installation)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
   - [Docker Setup](#docker-setup)
6. [API Documentation](#api-documentation)
7. [Demo Mode](#demo-mode)
8. [Dataset Guidance](#dataset-guidance)
9. [Configuration](#configuration)
10. [Limitations](#limitations)
11. [Privacy Considerations](#privacy-considerations)
12. [Future Roadmap](#future-roadmap)

---

## Project Overview

The system accepts one or more identity document images (or PDFs), runs them
through an explainable AI/CV pipeline, and produces a screening report
covering:

- Document type detection
- OCR-based structured field extraction
- Document format & logical-consistency validation
- Multi-signal tampering/anomaly analysis with visual region highlighting
- Optional face verification against a supplied person photo
- Cross-document identity consistency checking (when 2+ documents are given)
- A weighted, explainable overall risk score (0–100) mapped to LOW / MEDIUM
  / HIGH RISK, with a full breakdown and plain-language reasons

It ships with a **Demo Mode** containing four synthetic scenarios so the
whole pipeline can be demonstrated without any real identity documents.

## Features

- ✅ Supports Aadhaar, PAN, Passport, Driving Licence, Voter ID (modular —
  new types can be added by extending the classifier/extractor/validator)
- ✅ Drag-and-drop multi-file upload with live preview
- ✅ Automatic document type detection with manual override
- ✅ OCR + structured field extraction per document type
- ✅ Format validation (clearly distinguished from official verification)
- ✅ MRZ parsing & cross-check for passports
- ✅ 5-signal tampering analysis (ELA, noise inconsistency, copy-move,
  boundary analysis, metadata inspection) with bounding-box visualization
- ✅ Face verification with similarity score and match status
- ✅ Cross-document consistency checking with fuzzy name matching
- ✅ Transparent, configurable, weighted risk engine with plain-language
  explanations
- ✅ Screening history with dashboard statistics
- ✅ Demo Mode with 4 curated synthetic scenarios (genuine, tampered, face
  mismatch, cross-document inconsistency)
- ✅ Auto-deletion of uploaded files after processing (configurable)

## Architecture

```
USER UPLOADS DOCUMENT
        ↓
DOCUMENT TYPE DETECTION           (app/services/document_classifier.py)
        ↓
IMAGE PREPROCESSING               (app/utils/image_utils.py)
        ↓
OCR EXTRACTION                    (app/services/ocr_service.py)
        ↓
STRUCTURED FIELD EXTRACTION       (app/services/field_extraction_service.py)
        ↓
DOCUMENT-SPECIFIC VALIDATION      (app/services/validation_service.py)
        ↓
TAMPERING / ANOMALY ANALYSIS      (app/services/tampering_service.py)
        ↓
FACE VERIFICATION                 (app/services/face_service.py)
        ↓
CROSS-DOCUMENT CONSISTENCY CHECK  (app/services/cross_document_service.py)
        ↓
EXPLAINABLE RISK ENGINE           (app/services/risk_service.py)
        ↓
FINAL SCREENING REPORT
```

`app/services/pipeline_service.py` orchestrates the above for both the
`/api/screen` (real uploads) and `/api/demo/seed/{id}` (demo scenarios)
endpoints — both run through the *identical* pipeline.

### Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI entrypoint
│   │   ├── api/                       # Route handlers
│   │   │   ├── screening_routes.py
│   │   │   └── demo_routes.py
│   │   ├── services/                  # Business logic (Modules 2-8)
│   │   │   ├── ocr_service.py
│   │   │   ├── document_classifier.py
│   │   │   ├── field_extraction_service.py
│   │   │   ├── validation_service.py
│   │   │   ├── tampering_service.py
│   │   │   ├── face_service.py
│   │   │   ├── cross_document_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── pipeline_service.py    # Orchestrator
│   │   │   ├── storage_service.py     # Upload lifecycle / auto-delete
│   │   │   └── demo_data.py           # Synthetic demo scenario data
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── database/                  # DB session/engine setup
│   │   ├── utils/                     # Image preprocessing helpers
│   │   └── config/                    # Settings & risk-weight configuration
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/                # Reusable UI components
│   │   ├── pages/                     # Dashboard, NewScreening, Results, etc.
│   │   ├── services/api.js            # Backend API client
│   ├── package.json
│   └── .env.example
├── datasets/
│   ├── demo_documents/                # Synthetic demo images
│   ├── generate_demo_assets.py        # Regenerates synthetic images
│   └── README.md
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
├── docs/
├── docker-compose.yml
└── README.md
```

## Technology Stack

**Frontend:** React 18, Vite, Tailwind CSS, React Router, Recharts, Lucide icons

**Backend:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy

**AI / Computer Vision:**
- OpenCV (preprocessing, forensic signal computation)
- PaddleOCR (text extraction — optional; see [Demo Mode](#demo-mode))
- PyMuPDF (PDF page rendering)
- DeepFace (pretrained face-verification models — optional; see fallback)
- Custom heuristic image-forensics pipeline (ELA, noise analysis, copy-move
  detection, boundary analysis)

**Database:** SQLite by default; swappable to PostgreSQL via `DATABASE_URL`
(no code changes needed — see `backend/app/database/session.py`)

**Other:** Docker, Docker Compose, python-dotenv

---

## Installation

### Prerequisites

- Python 3.11+ (3.10+ should also work)
- Node.js 18+ and npm
- (Optional) Docker & Docker Compose

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
# ⚠️ paddleocr + paddlepaddle are heavyweight (100-300MB of model downloads
# on first use). The app runs correctly WITHOUT them via a documented
# fallback (see "Demo Mode" below and app/services/ocr_service.py).
# They are included in requirements.txt but you may comment them out for
# a faster setup if you only need to run Demo Mode.

cp .env.example .env
# edit .env if needed (defaults work out of the box)

python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`, with interactive docs
at `http://localhost:8000/docs`.

The database tables are created automatically on startup (SQLite file at
`backend/app/database/screening.db`).

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env   # optional — dev proxy works without it
npm run dev
```

The app will be available at `http://localhost:5173`. The Vite dev server
proxies `/api/*` requests to `http://localhost:8000` (see
`frontend/vite.config.js`), so make sure the backend is running first.

To build for production:

```bash
npm run build
npm run preview   # serves the production build locally for a quick check
```

### Docker Setup

The easiest way to run the full stack:

```bash
docker compose up --build
```

This builds and starts:
- **backend** on `http://localhost:8000`
- **frontend** (served via Nginx, which also proxies `/api` to the backend)
  on `http://localhost:8080`

To stop: `docker compose down` (add `-v` to also remove the persisted SQLite
volume).

> **Note:** The Docker backend image does **not** install PaddleOCR/
> PaddlePaddle/DeepFace by default (to keep build times and image size
> reasonable for a hackathon demo). The system runs correctly in
> **Demo Mode** using the documented fallbacks. To enable real OCR and face
> verification in Docker, uncomment the relevant lines in
> `backend/requirements.txt` and rebuild.

---

## API Documentation

Interactive OpenAPI/Swagger docs are auto-generated by FastAPI at
`/docs` (and ReDoc at `/redoc`) once the backend is running.

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/screen` | End-to-end screening: upload 1+ documents (+ optional person photo) and get a full risk report |
| `POST` | `/api/documents/detect` | Document type detection only |
| `POST` | `/api/documents/extract` | OCR + structured field extraction only |
| `GET`  | `/api/screenings` | List past screenings + dashboard counts |
| `GET`  | `/api/screenings/{id}` | Full detail for one past screening |
| `GET`  | `/api/demo/scenarios` | List bundled synthetic demo scenarios |
| `POST` | `/api/demo/seed/{scenario_id}` | Run a demo scenario through the real pipeline |
| `GET`  | `/api/system/info` | System capabilities, risk bands, disclaimers |
| `GET`  | `/api/health` | Health check |

### Example: `POST /api/screen`

```bash
curl -X POST http://localhost:8000/api/screen \
  -F "documents=@aadhaar.jpg" \
  -F "documents=@pan.jpg" \
  -F "person_photo=@selfie.jpg"
```

Returns a `ScreeningResultResponse` (see `backend/app/schemas/screening.py`)
containing per-document OCR/validation/tampering results, face verification,
cross-document consistency, and the final risk assessment.

---

## Demo Mode

Because real identity documents and government databases are (correctly)
unavailable in this environment, **Demo Mode** (`DEMO_MODE=true`, the
default) provides four end-to-end scenarios, all using **synthetic,
watermarked placeholder images** (see `datasets/README.md`):

| Scenario | ID | Expected Result |
|---|---|---|
| Genuine document | `genuine_single` | **LOW RISK** |
| Potentially tampered field | `tampered_field` | **HIGH RISK** |
| Face mismatch | `face_mismatch` | **HIGH RISK** |
| Multiple document inconsistency | `cross_doc_inconsistency` | **HIGH RISK** |

Run them from the UI ("New Screening" → "Demo Scenarios" tab) or directly:

```bash
curl -X POST http://localhost:8000/api/demo/seed/genuine_single
```

Demo scenarios run through **the exact same pipeline** as real uploads —
they are not a separate mocked code path. The only "shortcuts" taken are:
1. If PaddleOCR isn't installed, a documented OCR fallback returns the
   bundled ground-truth text for these specific known demo images (see
   `app/services/ocr_service.py`) — any *other* uploaded image still goes
   through OCR honestly and returns an empty result rather than fabricated
   text if no OCR engine is available.
2. If DeepFace isn't installed, face similarity for these specific bundled
   demo image pairs uses a curated value for presentation consistency (see
   `DEMO_FACE_SIMILARITY_OVERRIDES` in `app/services/demo_data.py`) — real
   uploads always go through actual face detection/comparison (via DeepFace
   or the OpenCV histogram fallback).

## Dataset Guidance

See [`datasets/README.md`](datasets/README.md) for full details. In short:

- All bundled demo images are **synthetic and clearly watermarked**. No real
  person, real document template, or real government record is used.
- **Do not** upload other people's real government-issued ID documents
  without their consent. Only use your own documents, consented test data,
  or synthetic/mock data with this prototype.
- This system never connects to, queries, or requires access to any
  government identity database (Aadhaar/UIDAI, Income Tax/PAN, Passport
  Seva, RTO, or Election Commission systems).

## Configuration

All configuration lives in `backend/.env` (copy from `.env.example`).
Key settings:

| Variable | Default | Description |
|---|---|---|
| `DEMO_MODE` | `true` | Enables synthetic-scenario fallbacks |
| `DATABASE_URL` | SQLite path | Swap to a `postgresql+psycopg2://...` DSN for Postgres |
| `AUTO_DELETE_UPLOADS` | `true` | Delete uploaded files from disk after processing |
| `MAX_UPLOAD_MB` | `15` | Max file size per upload |
| `FACE_MATCH_THRESHOLD` | `70` | % similarity above which faces are "LIKELY MATCH" |
| `FACE_REVIEW_THRESHOLD` | `50` | % similarity above which faces need "MANUAL REVIEW" |
| `RISK_WEIGHT_*` | see `.env.example` | Points-out-of-100 each risk category can contribute |
| `RISK_LOW_MAX` / `RISK_MEDIUM_MAX` | `30` / `60` | Score thresholds for risk bands |
| `CLASSIFIER_CONFIDENCE_THRESHOLD` | `0.55` | Below this, manual document-type selection is required |

The risk engine also applies an **escalation rule**: a confirmed face
mismatch, a cross-document identity conflict, or a high tampering score on
any document will escalate the case to HIGH RISK regardless of the
weighted total — mirroring how a human reviewer would treat these as hard
stops rather than averaging them away. The full weighted breakdown is
always shown for transparency (see `backend/app/services/risk_service.py`).

## Limitations

- **This is a prototype**, not a production fraud-detection system. The
  document classifier and field extractors use transparent rule-based
  heuristics (regex/keyword matching), not trained deep-learning models —
  this makes the system's reasoning auditable but less robust to
  significant variation in document layouts, lighting, or image quality
  than a production system would need to be.
- **Tampering detection is heuristic**, not a guaranteed forgery detector.
  It combines several classical image-forensics signals (error level
  analysis, noise inconsistency, copy-move detection, boundary analysis,
  metadata inspection) that are well-established techniques but can
  produce false positives on flat, low-texture, or heavily
  re-compressed/re-scanned images, and false negatives against a
  sophisticated forger.
- **OCR and face verification require optional heavy dependencies**
  (PaddleOCR, DeepFace) that are not installed by default in this build to
  keep setup fast. Without them, the system runs correctly in Demo Mode via
  documented fallbacks, but real-world OCR accuracy and face-similarity
  results on arbitrary uploaded images will be limited until those
  packages are installed.
- **No government database verification** — by design. This tool cannot
  and does not confirm that a document number is actually issued, active,
  or belongs to the named individual in any official registry.
- **MRZ parsing** implements only the TD3 (passport) two-line format at a
  basic level; it does not perform full check-digit validation.
- English-language OCR only (`OCR_LANG=en`); multi-language support would
  require configuring PaddleOCR's language models.

## Privacy Considerations

- Uploaded document images are written to a temporary directory
  (`UPLOAD_DIR`) only for the duration of processing, then deleted when
  `AUTO_DELETE_UPLOADS=true` (the default).
- The database stores only **derived metadata**: extracted field values,
  validation results, tampering scores/indicators, face similarity scores,
  and risk assessments — never the raw uploaded image bytes.
- No data is sent to any third-party API or external service; all
  processing (OCR, CV, face comparison) runs locally within the backend
  container/process.
- Because extracted fields (name, DOB, document numbers) are still
  sensitive personal data, treat the SQLite/PostgreSQL database itself as
  containing PII and secure it accordingly in any real deployment
  (encryption at rest, access controls, retention policy).

## Future Roadmap

- [ ] Add visa, residence permit, and other document types (the modular
      classifier/extractor/validator design supports this without touching
      existing document logic)
- [ ] Replace the rule-based document classifier with a trained lightweight
      CNN/vision-transformer classifier
- [ ] Add deep-learning-based tampering/splicing detection (e.g. a
      trained ManTraNet/CAT-Net-style model) alongside the current
      classical-CV heuristics for improved robustness
- [ ] Full MRZ check-digit validation (TD1/TD2/TD3 formats)
- [ ] Multi-language OCR support
- [ ] Role-based access control and audit logging for reviewer actions
- [ ] Batch screening / CSV export of screening history
- [ ] Configurable per-organization risk-weight profiles
