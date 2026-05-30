# REQUIREMENTS.md — Frozen Contract

> **Status:** FROZEN  
> **Date Frozen:** 2026-05-28  
> **Rule:** Any change to this file triggers a full revision of SPEC.md, PLAN.md, DEPENDENCIES.md, and CHECKPOINTS.md.

---

## Problem Statement

Businesses receive invoices in inconsistent formats (PDFs, scanned images) and manually key data into systems — slow, error-prone, and expensive. There is no reliable automated way to extract structured data from arbitrary invoice layouts without per-template configuration. This project builds an AI-powered pipeline that accepts any invoice document, extracts structured fields, self-validates, auto-corrects errors, and outputs clean JSON — eliminating manual data entry.

---

## In-Scope Features (will be built and demoed)

| # | Feature | Description |
|---|---------|-------------|
| F-1 | **OCR Agent** | Extract raw text from PDFs (text-based + scanned) and images (PNG, JPEG) using Tesseract/PyMuPDF; fallback to Gemini 1.5 Pro vision for images |
| F-2 | **Extraction Agent** | LLM-powered (Gemini 1.5 Pro, structured output) extraction of invoice fields from raw text: invoice_number, date, due_date, vendor, buyer, line_items, subtotal, tax, total, currency |
| F-3 | **Validation Agent** | Rule-based checks: line_items sum = subtotal, subtotal + tax = total, required fields present, numeric/date format validity; outputs pass/fail + error list |
| F-4 | **Auto-Correction Agent** | On validation failure: re-prompt LLM with error context (max 2 retries); apply arithmetic rule fixes; log all corrections |
| F-5 | **JSON Formatter** | Output validated data as standardized JSON with metadata (confidence, timing, corrections, validation status) |
| F-6 | **LangGraph Orchestrator** | Stateful workflow: Upload → OCR → Extraction → Validation → (Correction loop if fail) → JSON Output; conditional edges, state tracking |
| F-7 | **REST API** | FastAPI backend: POST /process (upload file), GET /status/{id}, GET /result/{id} |
| F-8 | **Web UI** | React frontend: file upload, processing status indicator, JSON result display with syntax highlighting, download button |

---

## Out-of-Scope Features (will NOT be built)

| Feature | Reason |
|---------|--------|
| User authentication / multi-tenancy | Not required for demo; adds 2+ days |
| Batch upload (multiple files at once) | Sequential processing sufficient for MVP |
| ERP/accounting system integration | No target system defined |
| Multi-language invoices | English-only reduces LLM prompt complexity |
| Invoice approval workflows | Business process layer, not extraction |
| Persistent document storage / history | Files processed transiently; no DB archive |
| Custom training / fine-tuning | Use prompt engineering + structured output instead |
| PDF generation / export (non-JSON) | JSON is the only output format |
| Deployment to cloud (AWS/Azure/GCP) | Local demo; Docker-compose is sufficient |

---

## Assumptions

### Environment
- Development on Windows, deployment via Docker Compose (local)
- Python 3.11+ for backend, Node.js 18+ for frontend
- Tesseract OCR installed locally (or Docker image includes it)

### Data
- Invoices are in English
- Standard business invoice structure (header, line items, totals)
- Test invoices: 5+ varied templates sourced from public datasets or manually created
- Single-page invoices primary; multi-page as stretch

### User
- Single concurrent user during demo
- User uploads one file at a time
- No login required

### Integration
- Google AI API key available (Gemini 1.5 Pro access, free tier)
- Internet connectivity for LLM API calls
- No external system integrations

### LLM
- Gemini 1.5 Pro with structured output (JSON mode) for extraction
- Gemini 1.5 Pro vision for image-based fallback OCR
- Temperature 0 for deterministic extraction
- Max 2 correction retries to cap cost/latency

---

## Success Criteria

| # | Criteria | Measurement |
|---|----------|-------------|
| SC-1 | End-to-end pipeline works | Upload PDF/image → receive correct JSON via UI |
| SC-2 | Template generalization | Correctly extracts from ≥ 3 different invoice layouts without code changes |
| SC-3 | Validation catches errors | Demo shows validation detecting arithmetic mismatch |
| SC-4 | Auto-correction works | Demo shows correction fixing at least 1 extraction error |
| SC-5 | Response time acceptable | Single invoice processed in ≤ 30 seconds end-to-end |

---

## Deliverables List

> Elaborated in [DELIVERABLES.md](./DELIVERABLES.md)

1. Working application (backend + frontend + orchestrator)
2. Live demo with real invoices (not mocked)
3. Architecture diagram (Mermaid)
4. Code walkthrough documentation
5. README with setup/run instructions

---

## 2-Week Capacity Reality Check

### Available Time
- 10 working days × 6 productive hours = **60 hours**
- Planning/docs: ~8 hours (Days 1-2, already partially done)
- Remaining for implementation + testing: **52 hours**

### Effort Estimate

| Component | Hours | Days |
|-----------|-------|------|
| Project setup (scaffolding, Docker, CI) | 4 | 0.5 |
| OCR Agent (Tesseract + PyMuPDF + fallback) | 6 | 1 |
| Extraction Agent (prompts + structured output) | 8 | 1.5 |
| Validation Agent (rules engine) | 4 | 0.5 |
| Correction Agent (re-prompt logic) | 5 | 1 |
| JSON Formatter | 2 | 0.5 |
| LangGraph Orchestrator (wiring + state) | 8 | 1.5 |
| FastAPI REST API | 4 | 0.5 |
| React UI (upload + display) | 6 | 1 |
| Integration testing (real invoices) | 5 | 1 |
| **Total** | **52** | **9** |

### Buffer
- 1 day (Day 10) reserved for demo prep, bug fixes, documentation polish

### Verdict: **FEASIBLE** — tight but achievable with disciplined execution and no scope creep.

### Risk Mitigations for Timeline
- UI kept minimal (functional, not polished)
- No custom CSS framework; use Tailwind defaults
- No deployment; Docker Compose local only
- Prompts iterated during extraction agent development, not separately
