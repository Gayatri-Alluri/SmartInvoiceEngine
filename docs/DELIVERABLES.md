# DELIVERABLES.md — Final Demo Checklist

> **Purpose:** Proves the project is COMPLETE. Every item must be checkable on demo day.  
> **Derived from:** REQUIREMENTS.md success criteria + evaluation expectations

---

## 1. Live Demo Checklist

### Demo Scenario A: Happy Path (Text PDF)

| # | Action | Expected Result | Status |
|---|--------|----------------|--------|
| A1 | Open `http://localhost:3000` | UI loads with upload area | ☐ |
| A2 | Upload `test-invoices/simple_invoice.pdf` | File accepted, "Process" button active | ☐ |
| A3 | Click "Process Invoice" | Pipeline status shows stages progressing | ☐ |
| A4 | Wait for completion | Status: all stages ✅ | ☐ |
| A5 | View JSON result | Syntax-highlighted JSON with all fields populated | ☐ |
| A6 | Verify metadata | `validation_status: "passed"`, processing_time < 30s | ☐ |
| A7 | Click "Download JSON" | .json file downloads to disk | ☐ |

### Demo Scenario B: Image Invoice (OCR)

| # | Action | Expected Result | Status |
|---|--------|----------------|--------|
| B1 | Upload `test-invoices/scanned_invoice.png` | File accepted | ☐ |
| B2 | Process completes | OCR method shows "tesseract" or "gpt4o_vision" in metadata | ☐ |
| B3 | Fields extracted correctly | invoice_number, date, total_amount populated | ☐ |

### Demo Scenario C: Validation Failure + Auto-Correction

| # | Action | Expected Result | Status |
|---|--------|----------------|--------|
| C1 | Upload `test-invoices/invoice_wrong_total.pdf` | File accepted | ☐ |
| C2 | Pipeline shows correction stage activating | Status: Validation ⚠️ → Correction ⚙️ | ☐ |
| C3 | Result shows correction applied | `validation_status: "corrected"` | ☐ |
| C4 | corrections_applied array is non-empty | Shows field, old_value, new_value, method | ☐ |

### Demo Scenario D: Template Generalization

| # | Action | Expected Result | Status |
|---|--------|----------------|--------|
| D1 | Upload invoice template #2 (different layout) | Extracts correctly | ☐ |
| D2 | Upload invoice template #3 (another layout) | Extracts correctly | ☐ |
| D3 | No code changes between uploads | Same code handles all templates | ☐ |

### Demo Scenario E: API Documentation

| # | Action | Expected Result | Status |
|---|--------|----------------|--------|
| E1 | Open `http://localhost:8000/docs` | Swagger UI renders | ☐ |
| E2 | Show all 3 endpoints documented | POST /process, GET /status, GET /result | ☐ |
| E3 | "Try it out" works | Upload file via Swagger → get result | ☐ |

---

## 2. Code Walkthrough Checklist

Walk through in this order:

| # | File/Area | Key Points to Highlight |
|---|-----------|------------------------|
| W1 | `SPEC.md` | Show spec-driven approach, schemas defined before code |
| W2 | `models/invoice.py` | Pydantic v2 models, nullable fields, typed line items |
| W3 | `agents/ocr_agent.py` | Multi-strategy OCR (PyMuPDF → Tesseract → Vision fallback) |
| W4 | `agents/extraction_agent.py` | `with_structured_output()`, temperature=0, retry logic |
| W5 | `agents/validation_agent.py` | Pure function, 5 rules, no external dependencies |
| W6 | `agents/correction_agent.py` | Rule-based fix + LLM re-prompt, max 2 retries |
| W7 | `orchestrator/graph.py` | LangGraph workflow, conditional edges, state management |
| W8 | `prompts/extraction.py` | Prompt engineering strategy, few-shot potential |
| W9 | `api/routes.py` | Async job pattern, background tasks, status polling |
| W10 | `frontend/src/components/` | React components, Tailwind, Axios service layer |
| W11 | `docker-compose.yml` | Single-command deployment |

---

## 3. Architecture Diagram Checklist

The `docs/architecture.mmd` diagram must show:

| # | Element | Present |
|---|---------|---------|
| 1 | User/Actor | ☐ |
| 2 | Frontend (React app) | ☐ |
| 3 | Backend (FastAPI) | ☐ |
| 4 | API endpoints (3 routes + /docs) | ☐ |
| 5 | LangGraph Orchestrator | ☐ |
| 6 | All 5 agents as distinct nodes | ☐ |
| 7 | Conditional edge (validation → correction loop) | ☐ |
| 8 | Google Gemini 1.5 Pro (external service) | ☐ |
| 9 | Tesseract + PyMuPDF (local tools) | ☐ |
| 10 | Data flow arrows with labels | ☐ |
| 11 | Docker Compose boundary | ☐ |

---

## 4. Framework & Tools Rationale

Must be able to explain:

| Choice | Rationale (one-liner) |
|--------|----------------------|
| **LangGraph** | Stateful graph with conditional edges — perfect for pipeline with retry loops |
| **Gemini 1.5 Pro** | Multimodal + structured output + free tier + high extraction accuracy |
| **FastAPI** | Async, Pydantic-native, auto-generates Swagger docs for free |
| **Tesseract** | Free, open-source OCR; no vendor lock-in |
| **PyMuPDF** | Fastest text extraction from native PDFs |
| **Pydantic v2** | Type-safe schemas shared between API ↔ agents ↔ LLM output |
| **React + Tailwind** | Fast UI development, no custom CSS maintenance |
| **Docker Compose** | One command runs everything, evaluator doesn't need local Python/Node setup |
| **Structured output** | Forces LLM to return valid JSON matching schema — no parsing errors |
| **Temperature 0** | Deterministic extraction — same input produces same output |

---

## 5. Completion Matrix

| Feature | ID | Status | Evidence |
|---------|-----|--------|----------|
| OCR Agent | F-1 | ☐ | test_ocr_agent.py GREEN + demo B |
| Extraction Agent | F-2 | ☐ | test_extraction_agent.py GREEN + demo A |
| Validation Agent | F-3 | ☐ | test_validation_agent.py GREEN + demo C |
| Correction Agent | F-4 | ☐ | test_correction_agent.py GREEN + demo C |
| JSON Formatter | F-5 | ☐ | Valid InvoiceJSON in demo output |
| LangGraph Orchestrator | F-6 | ☐ | Pipeline stages visible in demo |
| REST API | F-7 | ☐ | Swagger UI works (demo E) |
| Web UI | F-8 | ☐ | Browser demo (demo A) |

---

## 6. Known Limitations (Document Honestly)

| # | Limitation | Impact | Workaround |
|---|-----------|--------|-----------|
| 1 | Single concurrent user | Cannot demo with 2 parallel uploads | Acceptable for MVP |
| 2 | No persistent history | Results lost on server restart | Acceptable — ephemeral by design |
| 3 | Multi-page invoices | May only extract from first page | Document as known limitation |
| 4 | Very low-quality scans | OCR may return garbage text | Gemini vision fallback helps but not perfect |
| 5 | Non-English invoices | Will not extract correctly | Stated as out-of-scope in REQUIREMENTS.md |
