# AI-Based Fake Identity and Document Screening System

> **VeriShield AI** — An explainable, multi-document preliminary screening and anomaly detection system.  
> Developed for **Smart India Hackathon (SIH) 2026**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

---

> [!IMPORTANT]
> **System Purpose & Disclaimer**: VeriShield AI is an **AI-assisted preliminary document-screening and decision-support tool**. It inspects image files and document fields for formatting anomalies, image manipulation signatures, biometric mismatches, and cross-document inconsistencies. It does **not** connect to official government databases (such as UIDAI/Aadhaar, Income Tax Department/PAN, Passport Seva, RTO/Sarathi, or the Election Commission of India), and it does **not** issue a final, legally binding certification of document authenticity or fraud. All outputs are intended to assist human reviewers in prioritizing high-risk cases.

---

## Table of Contents

1. [Project Overview and Problem](#project-overview-and-problem)
2. [Proposed Solution](#proposed-solution)
3. [Features](#features)
4. [Complete Architecture and Workflow](#complete-architecture-and-workflow)
   - [End-to-End Processing Pipeline](#end-to-end-processing-pipeline)
   - [Repository Layout](#repository-layout)
5. [Actual Technology Stack](#actual-technology-stack)
6. [Installation and Setup](#installation-and-setup)
   - [Prerequisites](#prerequisites)
   - [Backend Setup](#backend-setup)
   - [Frontend Setup](#frontend-setup)
   - [Docker Setup](#docker-setup)
7. [API Endpoints](#api-endpoints)
8. [Demo Mode](#demo-mode)
9. [Dataset](#dataset)
10. [Risk Scoring and Forensics](#risk-scoring-and-forensics)
    - [5-Signal Tampering Analysis](#5-signal-tampering-analysis)
    - [3-Stage Face Verification](#3-stage-face-verification)
    - [Cross-Document Consistency Engine](#cross-document-consistency-engine)
    - [Weighted Scoring and Escalation Rules](#weighted-scoring-and-escalation-rules)
11. [Privacy and Security](#privacy-and-security)
12. [Limitations](#limitations)
13. [Future Roadmap](#future-roadmap)
14. [Team HackHive](#team-hackhive)

---

## Project Overview and Problem

Identity verification is a critical bottleneck across civic administration, banking KYC, institutional onboarding, and border management. Traditional verification workflows face several compounding challenges:

1. **Volume and Fatigue**: Human officers process hundreds of digital uploads daily, increasing the likelihood that subtle digital manipulations go unnoticed.
2. **Multi-Faceted Forgeries**: Modern forgers rarely rely on simple text replacement alone; they alter photograph regions, modify dates of birth across single documents, and submit partially conflicting sets of documents (e.g., matching name on Aadhaar and PAN, but diverging birth years or photos).
3. **Black-Box AI Skepticism**: Automated solutions that output a single opaque probability score without interpretable visual evidence or plain-language justifications cannot be safely relied upon in compliance-driven workflows.
4. **Data Privacy and Leakage**: Sending sensitive citizen identity credentials to third-party cloud AI APIs creates serious data privacy, jurisdictional, and regulatory compliance risks.

---

## Proposed Solution

**VeriShield AI** is an on-premise, explainable preliminary screening system designed to act as an intelligent co-pilot for document verification officers:

- **Local Multi-Document Ingestion**: Accepts one or multiple government-issued identity documents (Aadhaar, PAN, Passport, Driving Licence, Voter ID) along with an optional person photograph.
- **Explainable Multi-Stage Pipeline**: Combines image preprocessing, local OCR, structured field parsing, format validation, 5-signal forensic tampering detection, deep convolutional face verification, and cross-document identity consistency checks.
- **Transparent Risk Scoring**: Replaces opaque predictions with a calibrated **0–100 risk score** categorized into **LOW RISK**, **MEDIUM RISK**, or **HIGH RISK**, accompanied by highlighted anomaly bounding boxes and prioritized plain-language explanations.
- **Hard-Stop Escalations**: Enforces non-linear escalation rules so that critical security violations (such as a confirmed face mismatch or conflicting biographical fields) immediately escalate the assessment to HIGH RISK.
- **Privacy by Default**: Uploads are processed locally and automatically deleted immediately after analysis, persisting only derived audit metadata.

---

## Features

- **5 Supported Indian Document Types**:
  - **Aadhaar Card**: 12-digit format check, name, DOB, gender, and address parsing.
  - **PAN Card**: 10-character alphanumeric structure (`[A-Z]{5}[0-9]{4}[A-Z]`), name, father's name, and DOB parsing.
  - **Passport**: 8-character document number (`[A-Z][0-9]{7}`), expiry date verification, and two-line TD3 Machine Readable Zone (MRZ) parsing and cross-check.
  - **Driving Licence**: State code and number validation, issue date and validity/expiry parsing, and logical order verification (expiry > issue date).
  - **Voter ID (EPIC)**: 10-character EPIC format (`[A-Z]{3}\d{7}`), name, father's name, age plausibility check (18–120 years), and gender parsing.
- **Automated Document Classification**:
  - Keyword and regular expression pattern matcher that detects document types from OCR text with confidence scoring.
  - Flags documents requiring manual operator confirmation when confidence falls below threshold (`CLASSIFIER_CONFIDENCE_THRESHOLD = 0.55`).
  - Supports explicit manual document type override.
- **Computer Vision Image Preprocessing**:
  - Automatic downscaling (max dimension 1600 px) for performance.
  - Fast non-local means colored denoising (`cv2.fastNlMeansDenoisingColored`).
  - Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L channel of LAB color space.
  - Orientation deskewing (0.5° to 15°) via Otsu thresholding and minimum area bounding rectangle calculation.
  - Native multi-page PDF rendering at 2x resolution via PyMuPDF.
- **Local OCR Extraction**:
  - Primary engine: **EasyOCR** (PyTorch CRAFT text detection + CRNN text recognition) running locally.
  - Fallback engine: **Tesseract OCR** via `pytesseract`.
  - Honest reporting: returns empty results flagged for manual review rather than simulating text if no engine can read the document.
- **5-Signal Forensic Tampering Detection**:
  - **Error Level Analysis (ELA)**: re-compresses image to JPEG (quality 90) and isolates localized compression anomalies with bounding-box hotspot localization.
  - **Noise Inconsistency Analysis**: 4x4 spatial grid evaluating standard deviation of high-frequency Laplacian residuals against median blurring.
  - **Copy-Move Forgery Detection**: 16x16 sliding block-matching detector looking for spatially separated duplicated textures.
  - **Photograph Boundary Analysis**: Canny edge detection and contour rectangularity analysis around portrait photograph regions to detect cut-and-paste seams.
  - **Metadata & Compression Inspection**: EXIF analysis identifying known image editing software tags (Photoshop, GIMP, Paint.NET, Affinity, Pixlr).
- **3-Stage Biometric Face Verification**:
  - *Stage 1 (Detection)*: OpenCV Haar Cascade face localization (`haarcascade_frontalface_default.xml`), with aspect-ratio fallback for card photograph areas.
  - *Stage 2 (Representation)*: MobileNetV3-Small deep feature embedding model (classifier truncated to Identity) producing a 1024-dimensional normalized vector.
  - *Stage 3 (Matching)*: Cosine similarity comparison yielding a calibrated 0–100% match score categorized into *LIKELY MATCH* (≥70%), *MANUAL REVIEW REQUIRED* (50%–69.9%), *LIKELY MISMATCH* (<50%), or *NO FACE DETECTED*.
- **Cross-Document Identity Consistency**:
  - Multi-document comparison comparing Name, Date of Birth, and Gender across 2 or more uploaded documents.
  - Fuzzy string matching for names using Python's `difflib.SequenceMatcher` (threshold 0.82) after case normalization and whitespace stripping.
  - Multi-format date parsing and normalization to ISO format (`YYYY-MM-DD`).
- **Interactive Modern Web Dashboard**:
  - Built with React 18, Vite, and Tailwind CSS.
  - Drag-and-drop multi-file uploader with live preview.
  - Interactive risk gauge, risk category badges, and visual bounding-box overlays for detected tampering regions.
  - Searchable and filterable screening history log.
  - Dedicated system info page detailing active risk weights, supported document types, and disclaimers.
- **Audit Logging & Storage Lifecycle**:
  - SQLite database (configurable to PostgreSQL via SQLAlchemy).
  - Ephemeral file storage: uploaded image files are deleted immediately after screening completes when `AUTO_DELETE_UPLOADS=true`.

---

## Complete Architecture and Workflow

### End-to-End Processing Pipeline

The screening pipeline (`backend/app/services/pipeline_service.py`) orchestrates the end-to-end execution flow:

```
[User Ingestion]
  │  1+ Document Images / PDFs (Aadhaar, PAN, Passport, DL, Voter ID)
  │  + Optional Person Selfie Photo
  ▼
[Module 1: Storage & Preprocessing]
  │  - PyMuPDF rendering (if PDF)
  │  - Max-dimension resize (1600px)
  │  - Non-local means denoising
  │  - CLAHE contrast enhancement (LAB color space)
  │  - Otsu deskewing (0.5° - 15°)
  ▼
[Module 2: Optical Character Recognition]
  │  - EasyOCR (PyTorch CRAFT + CRNN)
  │  - Fallback: Tesseract OCR
  │  - Extracts text lines, bounding boxes, mean confidence
  ▼
[Module 3: Document Type Classification]
  │  - Regex & keyword signal detection
  │  - Manual type override support
  │  - Flags low confidence (< 0.55) for manual review
  ▼
[Module 4: Structured Field Extraction & MRZ Parsing]
  │  - Per-document regex & label parsers
  │  - Passport 2-line TD3 MRZ parsing (second line decoding)
  ▼
[Module 5: Format & Consistency Validation]
  │  - Aadhaar: 12-digit format check
  │  - PAN: 10-char alphanumeric regex
  │  - Passport: 8-char regex + expiry check + printed vs MRZ match
  │  - DL: expiry check + issue date < expiry date logic
  │  - Voter ID: 10-char EPIC regex + age range check (18-120)
  ▼
┌─────────────────────────────────────────────────────────────┐
│ Concurrent Forensic & Biometric Analysis                    │
│                                                             │
│  [Module 6: Image Forensics]                                │
│    • Error Level Analysis (Q=90 JPEG diff + hotspot boxes)  │
│    • Noise Inconsistency (4x4 Laplacian grid variance)      │
│    • Copy-Move Detection (16x16 block descriptor matching)  │
│    • Boundary Analysis (Canny rectangularity around photo)  │
│    • Metadata Inspection (EXIF software tags)               │
│                                                             │
│  [Module 7: Face Biometrics (if person photo supplied)]     │
│    • Detection: OpenCV Haar Cascade                         │
│    • Representation: PyTorch MobileNetV3-Small embeddings   │
│    • Comparison: Cosine similarity (0-100% calibrated)      │
│                                                             │
│  [Module 8: Cross-Document Consistency (if 2+ documents)]   │
│    • Name fuzzy similarity (difflib SequenceMatcher >= 82%) │
│    • DOB date normalization (YYYY-MM-DD)                    │
│    • Gender code comparison                                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[Module 9: Explainable Risk Engine]
  │  - Weighted category score computation (0-100)
  │  - Non-linear hard escalation checks:
  │      * Confirmed face mismatch
  │      * Cross-document identity conflict
  │      * High tampering score on any document
  │  - Prioritized human-readable explanations list
  ▼
[Module 10: Persistence & Response]
  │  - Save derived metadata and results to SQLite / PostgreSQL
  │  - Auto-delete uploaded raw image files (if configured)
  │  - Return complete ScreeningResultResponse to React Frontend
```

### Repository Layout

```
VeriShield AI/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application, CORS, lifespan & health routes
│   │   ├── api/
│   │   │   ├── screening_routes.py     # End-to-end /screen and individual module endpoints
│   │   │   └── demo_routes.py          # /demo/scenarios and /demo/seed/{id} endpoints
│   │   ├── config/
│   │   │   └── settings.py             # App configuration, env variables & risk weights
│   │   ├── database/
│   │   │   ├── session.py              # SQLAlchemy engine, session maker & init_db
│   │   │   └── .gitkeep
│   │   ├── models/
│   │   │   └── screening.py            # SQLAlchemy Screening & Document ORM models
│   │   ├── schemas/
│   │   │   └── screening.py            # Pydantic schemas for requests, responses & enums
│   │   ├── services/
│   │   │   ├── pipeline_service.py     # Orchestrates modules 2-8 into screening pipeline
│   │   │   ├── document_classifier.py  # Rule-based regex/keyword document classifier
│   │   │   ├── ocr_service.py          # EasyOCR & Tesseract text extraction service
│   │   │   ├── field_extraction_service.py # Per-document field extractors & TD3 MRZ parser
│   │   │   ├── validation_service.py   # Document format, checksum, and date validators
│   │   │   ├── tampering_service.py    # 5-signal forensic tampering & anomaly detector
│   │   │   ├── face_service.py         # Haar cascade detector & MobileNetV3 face embedding
│   │   │   ├── cross_document_service.py # Multi-document identity cross-checking service
│   │   │   ├── risk_service.py         # 6-category weighted scoring & escalation engine
│   │   │   ├── storage_service.py      # Upload validation, saving, and auto-deletion
│   │   │   └── demo_data.py            # Synthetic demo scenarios & ground-truth text
│   │   └── utils/
│   │       └── image_utils.py          # OpenCV preprocessing (resize, denoise, CLAHE, deskew)
│   ├── tests/
│   │   ├── test_screening.py           # 12 automated pytest suites covering all modules
│   │   └── verify_e2e.py               # Standalone end-to-end pipeline verification script
│   ├── requirements.txt                # Python backend dependencies
│   └── .env.example                    # Backend environment configuration template
├── frontend/
│   ├── src/
│   │   ├── components/                 # UI components: DropZone, RiskGauge, RiskBadge, Layout...
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx           # Aggregate stats, charts, recent screenings list
│   │   │   ├── NewScreening.jsx        # File upload form & demo scenario selector tabs
│   │   │   ├── Results.jsx             # Comprehensive forensic report & visual inspection
│   │   │   ├── History.jsx             # Filterable and searchable past screening history
│   │   │   └── SystemInfo.jsx          # System configuration, capabilities & disclaimers
│   │   ├── services/
│   │   │   └── api.js                  # Axios client calling backend API endpoints
│   │   ├── App.jsx                     # Route definitions & navigation
│   │   ├── main.jsx                    # React application entrypoint
│   │   └── index.css                   # Tailwind CSS imports & global styles
│   ├── package.json                    # Node dependencies & build scripts
│   ├── vite.config.js                  # Vite server & backend API proxy configuration
│   ├── tailwind.config.js              # Tailwind CSS theme settings
│   └── .env.example                    # Frontend environment configuration template
├── datasets/
│   ├── demo_documents/                 # Bundled synthetic watermarked test documents
│   └── README.md                       # Synthetic dataset ethics and generation documentation
├── docker/
│   ├── Dockerfile.backend              # Python 3.11-slim backend container definition
│   ├── Dockerfile.frontend             # Multi-stage Node 20 build -> Nginx frontend container
│   └── nginx.conf                      # Nginx reverse proxy configuration
├── docs/
│   └── ARCHITECTURE.md                 # Technical extension guide for new document types
├── docker-compose.yml                  # Full-stack container deployment orchestrator
├── .gitignore                          # Exclusion rules for secrets, DBs, caches & artifacts
├── LICENSE                             # MIT License
└── README.md                           # Comprehensive project documentation
```

---

## Actual Technology Stack

### Frontend
- **React 18.3.1**: Component-based user interface.
- **Vite 6.0.5**: Build tool and development server with API proxying.
- **Tailwind CSS 3.4.17**: Utility-first styling for layouts, cards, and risk badges.
- **React Router DOM 6.28.0**: Client-side routing (`/`, `/screen`, `/results/:id`, `/history`, `/system`).
- **Recharts 2.13.3**: Interactive risk distribution and dashboard analytics charts.
- **Lucide React 0.468.0**: Icons across all navigation, status badges, and forensic panels.
- **Axios 1.7.9**: Promise-based HTTP client for backend REST communication.

### Backend
- **Python 3.10 / 3.11**: Primary runtime language.
- **FastAPI 0.115.6**: Asynchronous web framework with automatic OpenAPI/Swagger generation.
- **Uvicorn 0.34.0**: ASGI web server.
- **Pydantic 2.10.4**: Data validation and request/response serialization.
- **SQLAlchemy 2.0.36**: Database ORM and schema management.
- **python-multipart 0.0.20**: Streaming multipart form-data parser for file uploads.
- **python-dotenv 1.0.1**: Environment variable management.

### Computer Vision, OCR & Biometrics
- **OpenCV (`opencv-python-headless` 4.10.0.84)**: Image loading, denoising, CLAHE enhancement, deskewing, Canny edge detection, and Haar Cascade face detection.
- **NumPy 1.26.4**: Numerical arrays for image manipulation, DCT variance, and embedding normalization.
- **Pillow (PIL) 11.0.0**: Image format conversion, Error Level Analysis (ELA) re-compression, and EXIF extraction.
- **PyMuPDF (`fitz` 1.25.1)**: Multi-page PDF document page rasterization.
- **EasyOCR 2.9.1**: CRAFT text detection and CRNN character recognition running on CPU/GPU.
- **Tesseract OCR (`pytesseract`)**: Secondary local OCR fallback engine.
- **PyTorch & Torchvision (`torch`, `torchvision`)**: MobileNetV3-Small convolutional neural network for 1024-dimensional face embedding extraction.
- **Python Standard Library `difflib`**: SequenceMatcher for fuzzy name similarity comparison.

### Database & Deployment
- **SQLite**: Default zero-setup local persistent database.
- **PostgreSQL**: Supported via `DATABASE_URL` DSN configuration without code changes.
- **Docker & Docker Compose**: Multi-container orchestration (Backend on port 8000, Frontend on port 8080 via Nginx).

---

## Installation and Setup

### Prerequisites

- **Python**: Version 3.10 or 3.11 installed.
- **Node.js**: Version 18 or higher with `npm`.
- *(Optional)* **Docker** & **Docker Compose** for containerized execution.

---

### Backend Setup

1. Open a terminal and navigate to the `backend/` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment settings:
   ```bash
   cp .env.example .env
   ```
   *(The default values work immediately out of the box).*

5. Start the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The backend is accessible at `http://localhost:8000`.  
Open the interactive Swagger UI at `http://localhost:8000/docs`.

---

### Frontend Setup

1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Create local environment configuration:
   ```bash
   cp .env.example .env
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

The application interface will open at `http://localhost:5173`.

To verify a production build:
```bash
npm run build
npm run preview
```

---

### Docker Setup

To build and run the entire stack using Docker Compose:

```bash
docker compose up --build
```

- **Frontend Application**: `http://localhost:8080` (served via Nginx)
- **Backend API**: `http://localhost:8000`
- **Interactive Documentation**: `http://localhost:8000/docs`

To stop containers:
```bash
docker compose down
```

---

## API Endpoints

FastAPI auto-generates comprehensive interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

| HTTP Method | Path | Summary / Description |
|---|---|---|
| `POST` | `/api/screen` | **Full End-to-End Screening**: Ingests 1+ document files (`documents`) and an optional selfie (`person_photo`), executes the full pipeline, and returns a comprehensive `ScreeningResultResponse`. |
| `POST` | `/api/documents/detect` | Standalone document classification from an uploaded image. |
| `POST` | `/api/documents/extract` | Standalone OCR text extraction and structured field parsing. |
| `POST` | `/api/documents/validate` | Standalone format, checksum, and date validation for a given document type and field dictionary. |
| `POST` | `/api/tampering/analyze` | Standalone 5-signal forensic tampering and anomaly detection. |
| `POST` | `/api/face/verify` | Standalone biometric face verification comparing a document photo and selfie. |
| `POST` | `/api/identity/compare` | Standalone cross-document consistency check across 2+ document field dictionaries. |
| `GET`  | `/api/screenings` | Retrieves past screening records and dashboard summary statistics. |
| `GET`  | `/api/screenings/{id}` | Retrieves full stored forensic report for a specific screening ID. |
| `GET`  | `/api/demo/scenarios` | Lists all bundled synthetic demo scenarios. |
| `POST` | `/api/demo/seed/{scenario_id}` | Runs a bundled synthetic demo scenario through the full pipeline. |
| `GET`  | `/api/system/info` | Returns system metadata, active risk weights, supported document types, and disclaimers. |
| `GET`  | `/api/health` | Health check endpoint returning `{"status": "healthy"}`. |
| `GET`  | `/` | Root endpoint returning application name, version, demo status, and disclaimer. |

---

## Demo Mode

To allow judges, evaluators, and developers to test the full pipeline immediately without requiring real citizen credentials, VeriShield includes a built-in **Demo Mode** (`DEMO_MODE=true` by default):

### Bundled Synthetic Scenarios

1. **`genuine_single`** (*Genuine Document*):
   - A single, well-formed synthetic Aadhaar card paired with a matching selfie.
   - Expected Result: **LOW RISK** (format pass, low tampering score, face match ~93.5%).
2. **`tampered_field`** (*Potentially Tampered Field*):
   - A synthetic PAN card where the Date of Birth field exhibits ELA localized compression artifacts and conflicts with an Aadhaar record.
   - Expected Result: **HIGH RISK** (tampering indicators + cross-document inconsistency).
3. **`face_mismatch`** (*Face Biometric Mismatch*):
   - A synthetic document paired with a completely different individual's portrait photograph.
   - Expected Result: **HIGH RISK** (hard-stop escalation triggered by face similarity ~12.0%).
4. **`cross_doc_inconsistency`** (*Cross-Document Inconsistency*):
   - Multiple documents submitted with mismatched biographical information and conflicting photographs.
   - Expected Result: **HIGH RISK** (hard-stop escalation triggered by cross-document conflict).

> **Architectural Note**: Demo scenarios run through the **exact same pipeline** as real uploads (`pipeline_service.py`). They exercise real image decoding, validation functions, cross-document matching, risk scoring, and database persistence.

---

## Dataset

- **Zero Real PII**: The repository contains **no real citizen identity documents, real photographs, or private personal data**.
- **Synthetic Test Documents**: All test documents in `datasets/demo_documents/` are 100% synthetic, programmatically rendered mockups created for verification testing.
- **Visible Watermarking**: Every bundled demo document contains an explicit, visible watermark:  
  `"SYNTHETIC SAMPLE — NOT A REAL DOCUMENT"`.
- **Format Compliance**: Mock document numbers (e.g. `ABCDE1234F` for PAN, `1234 5678 9012` for Aadhaar, `N1234567` for Passport) were chosen solely to test regular expression and format parsing rules. They do not correspond to real government records.
- See [`datasets/README.md`](datasets/README.md) for data governance policies.

---

## Risk Scoring and Forensics

### 5-Signal Tampering Analysis

The tampering service (`backend/app/services/tampering_service.py`) calculates an anomaly score (0–100) by combining five weighted forensic signals:

$$\text{Tampering Score} = 0.35 \times S_{\text{ELA}} + 0.20 \times S_{\text{Noise}} + 0.20 \times S_{\text{CopyMove}} + 0.15 \times S_{\text{Boundary}} + 0.10 \times S_{\text{Metadata}}$$

- **Error Level Analysis (ELA) [35%]**: Re-saves the image as JPEG at Q=90 and calculates absolute pixel error against the original. Evaluates contrast between top 5th percentile error pixels (`p95`) and median error (`p50`). Identifies localized hotspot contours (area ≥ 150 px).
- **Noise Inconsistency [20%]**: Subdivides the image into a 4x4 grid. Computes high-frequency residual standard deviation via 3x3 median blur subtraction, scoring the coefficient of variation across cells.
- **Copy-Move Duplication [20%]**: Evaluates 16x16 pixel blocks (stride 16) with variance ≥ 6.0, downsamples to 4x4 descriptors, and counts matching block pairs separated by spatial distance ≥ 48 px.
- **Boundary Analysis [15%]**: Canny edge detection (thresholds 80, 200) seeking portrait-sized rectangular contours (2%–25% of image area, aspect ratio 0.6–1.1) with sharpness score > 92.
- **Metadata Inspection [10%]**: Evaluates EXIF tags for absence (common in screenshots) or presence of known editing tools (Photoshop, GIMP, Paint.NET, Affinity, Pixlr).

Score Bands: **LOW** (< 25), **MEDIUM** (25–54.9), **HIGH** (≥ 55).

### 3-Stage Face Verification

The face verification service (`backend/app/services/face_service.py`) follows three distinct stages:
1. **Detection**: OpenCV Haar Cascade detects the largest face rectangle in both the document and person image.
2. **Representation**: Faces are cropped with a 10% margin, resized to 128x128 px, normalized, and passed through a **MobileNetV3-Small** deep CNN to extract dense unit-normalized embedding vectors.
3. **Comparison**: Cosine similarity between embeddings is calibrated to a 0–100% scale:
   - **≥ 70.0%**: `LIKELY MATCH`
   - **50.0% – 69.9%**: `MANUAL REVIEW REQUIRED`
   - **< 50.0%**: `LIKELY MISMATCH`
   - Face localization failure: `NO FACE DETECTED` (0.0% similarity)

### Cross-Document Consistency Engine

When 2 or more documents are uploaded (`backend/app/services/cross_document_service.py`):
- **Name**: Normalized (uppercase, alphabet-only, single-spaced) and compared using `difflib.SequenceMatcher.ratio()`. Flagged as inconsistent if pairwise similarity < 82%.
- **Date of Birth**: Parsed from formats (`%d/%m/%Y`, `%d-%m-%Y`, `%d/%m/%y`, `%d-%m-%y`) and normalized to ISO `YYYY-MM-DD`. Flagged if values differ.
- **Gender**: Normalized to single-character code (`M` / `F`) and checked for equality.
- **Consistency Levels**: **HIGH** (0 inconsistencies), **MEDIUM** (< 50% inconsistent fields), **LOW** (≥ 50% inconsistent fields).

### Weighted Scoring and Escalation Rules

The risk engine (`backend/app/services/risk_service.py`) computes a composite score (0–100) based on configurable weights:

| Risk Category | Max Points | Evaluation Basis |
|---|---|---|
| **Tampering Analysis** | **30** | Maximum tampering score across submitted documents |
| **Document Validation** | **20** | Format failures (20 pts), minor warnings (8 pts), all pass (0 pts) |
| **Face Verification** | **15** | Mismatch / no face (15 pts), manual review (7.5 pts), match (0 pts) |
| **Cross-Document Consistency** | **15** | Low consistency (15 pts), medium (7.5 pts), high/single doc (0 pts) |
| **Expiry Status** | **10** | Expired documents (10 pts), valid / not applicable (0 pts) |
| **OCR Confidence** | **10** | Average confidence: <60% (10 pts), 60%–84% (4 pts), ≥85% (0 pts) |

#### Non-Linear Escalation Rules
A case is automatically escalated to **HIGH RISK** regardless of the numerical total if any of the following critical triggers occur:
1. **Confirmed Face Mismatch**: Face verification yields `LIKELY MISMATCH` or `NO FACE DETECTED`.
2. **Cross-Document Identity Conflict**: Cross-document consistency evaluates to `LOW`.
3. **High Tampering Score**: Any individual document exhibits a `HIGH` tampering level (score ≥ 55).

---

## Privacy and Security

- **Ephemeral File Storage**: Uploaded files are saved to `backend/app/uploads_tmp/` solely for the duration of pipeline processing. By default (`AUTO_DELETE_UPLOADS=true`), raw image files are automatically deleted from disk upon completion.
- **Audit Metadata Persistence**: The database stores only derived analysis results (extracted text, validation outcomes, tampering scores, bounding boxes, risk breakdowns) — never raw citizen image bytes.
- **100% Local Inference**: All OCR, image processing, forensics, and face embedding calculations run entirely on the host machine or container. No citizen data or document images are transmitted to external third-party cloud APIs.
- **Environment Isolation**: Production deployments can isolate the backend within a private network, persisting only audit records to an encrypted PostgreSQL database.

---

## Limitations

- **Preliminary Screening Tool**: VeriShield AI is designed for preliminary risk scoring and triage; it is not a legal substitute for official government identity verification.
- **No Direct Government Registry Integration**: The system performs format, structure, and forensic checks. It does not verify whether an identity number is currently active in UIDAI, Income Tax, or Passport Seva databases.
- **Heuristic Image Forensics**: Classical image forensics (ELA, noise analysis, copy-move detection) provide valuable anomaly signals but can produce false positives on heavily re-compressed or low-resolution scans, and may not detect sophisticated generative AI deepfakes.
- **Language Scope**: Document classification and OCR extraction are currently optimized for English alphanumeric text. Non-Latin Indian regional scripts require language-specific OCR model extensions.
- **Passport MRZ Scope**: MRZ parsing is currently implemented for standard two-line TD3 passport formats and does not cover TD1 or TD2 identity card standards.

---

## Future Roadmap

- [ ] **Deep Learning Forgery Detectors**: Integration of neural network models (such as CAT-Net or TruFor) alongside classical heuristics for enhanced splicing and manipulation detection.
- [ ] **Multilingual Indic OCR**: Support for Indian regional languages (Hindi, Tamil, Telugu, Bengali, Marathi, etc.) using Indic-specialized OCR models.
- [ ] **Government Sandbox Integration**: Integration with official DigiLocker and authorized verification gateways where regulatory access is granted.
- [ ] **Batch Processing & Asynchronous Queues**: Celery/Redis background task queues for bulk enterprise screening workflows.
- [ ] **Role-Based Access Control (RBAC)**: Fine-grained user permissions and tamper-evident audit logging for fraud investigation teams.

---

## Team HackHive

* Kaiser Mohiuddin — Team Lead
* Nawazish Nabi
* Nabeel Mushtaq
* Ovais Shabir Sheirgojrie
* Suhani Mahajan
* Md Altabuddin

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
