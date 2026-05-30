# Smart Invoice Engine

> Multi-Modal Document Data Extraction: Invoice-to-JSON Processor

An AI-powered pipeline that extracts structured data from PDF and image-based invoices, validates correctness, auto-corrects errors, and outputs clean JSON — without per-template configuration.

---

## What It Does

Upload any invoice (PDF or image) → get structured JSON with all fields extracted, validated, and corrected automatically.

```
Invoice (PDF/Image) → OCR → Extraction → Validation → Auto-Correction → JSON Output
```

---

## Features

- **OCR Agent** — Extracts text from PDFs (PyMuPDF) and images (Tesseract), with Gemini 1.5 Pro vision fallback
- **Extraction Agent** — LLM-powered structured data extraction (11 invoice fields)
- **Validation Agent** — Rule-based checks (arithmetic, required fields, format)
- **Correction Agent** — Auto-fixes errors via rules + LLM re-analysis (max 2 retries)
- **JSON Formatter** — Standardized output with metadata (confidence, timing, corrections)
- **LangGraph Orchestrator** — Stateful pipeline with conditional correction loop
- **REST API** — FastAPI with Swagger UI documentation
- **Web UI** — React upload + status tracker + JSON viewer + download

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, LangGraph, langchain-google-genai |
| LLM | Google Gemini 1.5 Pro (structured output, temperature 0) |
| OCR | PyMuPDF + Tesseract + Gemini Vision (fallback) |
| Frontend | React 18, TypeScript 5, Tailwind CSS, Vite |
| Infrastructure | Docker Compose |

---

## Quick Start

### Prerequisites

- Docker + Docker Compose
- Google AI API key (Gemini 1.5 Pro access, free tier)

### Run

```bash
# 1. Clone the repo
git clone <repo-url>
cd SmartInvoiceEngine

# 2. Set up environment
cp backend/.env.example backend/.env
# Edit backend/.env and add your GOOGLE_API_KEY

# 3. Start everything
docker-compose up --build

# 4. Open the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

### Without Docker (Development)

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/process` | Upload invoice file (PDF/PNG/JPEG) |
| GET | `/api/status/{job_id}` | Poll processing status |
| GET | `/api/result/{job_id}` | Get extraction result (JSON) |
| GET | `/api/health` | Health check |
| GET | `/docs` | Swagger UI (interactive API docs) |

---

## Project Structure

```
SmartInvoiceEngine/
├── backend/app/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Environment configuration
│   ├── api/                 # REST endpoints + schemas
│   ├── agents/              # OCR, Extraction, Validation, Correction, Formatter
│   ├── orchestrator/        # LangGraph workflow + state
│   ├── models/              # Pydantic domain models
│   ├── prompts/             # LLM prompt templates
│   └── utils/               # Logging utilities
├── frontend/src/
│   ├── components/          # Upload, Status, Result, Download
│   ├── services/            # API client (Axios)
│   ├── types/               # TypeScript interfaces
│   └── hooks/               # Processing hook
├── test-invoices/           # Sample invoices for testing
├── docs/                    # BRD, architecture diagram, plan
└── docker-compose.yml
```

---

## Architecture

See [docs/architecture.mmd](docs/architecture.mmd) for the full Mermaid diagram.

```
┌────────┐     ┌─────────┐     ┌───────────────────────────────────────┐
│  User  │────▶│ React UI│────▶│ FastAPI + LangGraph Orchestrator      │
└────────┘     └─────────┘     │                                       │
                               │  OCR → Extraction → Validation        │
                               │                        │               │
                               │                   pass/fail            │
                               │                    ↓    ↓              │
                               │              Formatter  Correction     │
                               │                        (loop back)     │
                               └───────────────────────────────────────┘
                                        │                    │
                                        ▼                    ▼
                                 Tesseract/PyMuPDF     Google Gemini 1.5 Pro
```

---

## Current Phase

| Phase | Status |
|-------|--------|
| Phase 0: Planning & Scaffolding | ⬜ In Progress |
| Phase 1: Core Agents | ⬜ Not Started |
| Phase 2: Correction + Orchestrator | ⬜ Not Started |
| Phase 3: API + Frontend | ⬜ Not Started |
| Phase 4: Integration Testing | ⬜ Not Started |

---

## Documentation

| Document | Description |
|----------|-------------|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Frozen scope contract |
| [SPEC.md](SPEC.md) | Technical specification (source of truth) |
| [docs/PLAN.md](docs/PLAN.md) | 2-week execution plan |
| [DEPENDENCIES.md](DEPENDENCIES.md) | Build order graph |
| [CHECKPOINTS.md](CHECKPOINTS.md) | Phase gate criteria |
| [DELIVERABLES.md](DELIVERABLES.md) | Demo checklist |
| [FUTURE_VISION.md](FUTURE_VISION.md) | Full product vision |
| [MVP_PREVIEW.md](MVP_PREVIEW.md) | What the demo looks like |
| [docs/BRD.md](docs/BRD.md) | Business requirements |
| [docs/architecture.mmd](docs/architecture.mmd) | Architecture diagram |

---

## License

Internal project — not for public distribution.
