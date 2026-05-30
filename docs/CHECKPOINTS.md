# CHECKPOINTS.md — Phase Gate Criteria

> **Rule:** You CANNOT start the next phase until the current gate is GREEN.  
> **Derived from:** PLAN.md + SPEC.md

---

## Gate 0: Planning & Scaffolding (End of Day 2)

### Criteria

| # | Check | Command / Evidence | Status |
|---|-------|-------------------|--------|
| 0.1 | All planning docs committed | `git ls-files *.md` shows: REQUIREMENTS, SPEC, PLAN, DEPENDENCIES, CHECKPOINTS, DELIVERABLES, FUTURE_VISION, MVP_PREVIEW, README | ☐ |
| 0.2 | Backend starts | `cd backend && python -m app.main` → FastAPI running on :8000 | ☐ |
| 0.3 | Frontend starts | `cd frontend && npm run dev` → Vite running on :3000 | ☐ |
| 0.4 | Docker Compose works | `docker-compose up` → both services healthy | ☐ |
| 0.5 | Health endpoint responds | `curl http://localhost:8000/api/health` → `{"status": "ok"}` | ☐ |
| 0.6 | Swagger UI accessible | Open `http://localhost:8000/docs` → Swagger renders | ☐ |
| 0.7 | Config loads from env | `config.py` reads OPENAI_API_KEY without crash | ☐ |
| 0.8 | .env.example exists | File present with all required vars listed | ☐ |
| 0.9 | copilot-instructions.md exists | `.github/copilot-instructions.md` committed | ☐ |

### If FAIL
- Fix scaffolding issues before writing any agent code
- Common issues: missing dependencies in requirements.txt, Docker build errors, port conflicts

### Sign-off
- Date: ____
- Notes: ____

---

## Gate 1: Core Agents (End of Day 5)

### Criteria

| # | Check | Command / Evidence | Status |
|---|-------|-------------------|--------|
| 1.1 | Models importable | `python -c "from app.models.invoice import ExtractedInvoice, OCRResult, ValidationResult"` → no error | ☐ |
| 1.2 | OCR Agent — text PDF | `pytest tests/test_ocr_agent.py::test_text_pdf` → GREEN | ☐ |
| 1.3 | OCR Agent — image | `pytest tests/test_ocr_agent.py::test_image_ocr` → GREEN | ☐ |
| 1.4 | Extraction Agent — structured output | `pytest tests/test_extraction_agent.py::test_extract_invoice` → GREEN | ☐ |
| 1.5 | Extraction Agent — returns ExtractedInvoice | Output is valid Pydantic model with ≥ 8/11 fields populated | ☐ |
| 1.6 | Validation Agent — catches arithmetic error | `pytest tests/test_validation_agent.py::test_line_items_sum_mismatch` → detects error | ☐ |
| 1.7 | Validation Agent — passes valid data | `pytest tests/test_validation_agent.py::test_valid_invoice` → is_valid=True | ☐ |
| 1.8 | Chain test | Run OCR → Extraction → Validation on a real invoice in a script → produces ValidationResult | ☐ |
| 1.9 | Test invoices exist | `test-invoices/` folder has ≥ 3 sample files (PDF + image) | ☐ |

### If FAIL
- Do NOT start Phase 2
- Debug the failing agent in isolation
- If Extraction Agent accuracy is low → iterate on prompt (prompts/extraction.py)
- If OCR is poor on images → verify Tesseract installation, try different test image

### Sign-off
- Date: ____
- Notes: ____

---

## Gate 2: Correction + Orchestrator (End of Day 7)

### Criteria

| # | Check | Command / Evidence | Status |
|---|-------|-------------------|--------|
| 2.1 | Correction Agent — rule-based fix | `pytest tests/test_correction_agent.py::test_arithmetic_correction` → fixes subtotal | ☐ |
| 2.2 | Correction Agent — LLM re-prompt | `pytest tests/test_correction_agent.py::test_llm_correction` → corrects missing field | ☐ |
| 2.3 | Correction Agent — max retries respected | After 2 failed attempts → returns best-effort, does not loop forever | ☐ |
| 2.4 | Formatter outputs valid schema | `pytest tests/test_formatter.py` → output matches InvoiceJSON schema | ☐ |
| 2.5 | LangGraph compiles | `python -c "from app.orchestrator.graph import workflow; workflow.get_graph()"` → no error | ☐ |
| 2.6 | Pipeline — happy path | Feed valid invoice through full graph → status="completed", validation_status="passed" | ☐ |
| 2.7 | Pipeline — correction path | Feed invoice with wrong total → correction triggers → validation_status="corrected" | ☐ |
| 2.8 | Pipeline — failure path | Feed garbage text → status="failed", error message present | ☐ |
| 2.9 | State tracking works | WorkflowState.current_stage updates at each node | ☐ |

### If FAIL
- Do NOT start API layer
- If orchestrator won't compile → check agent function signatures match expected input/output
- If correction loops infinitely → verify `correction_attempts` counter increments
- If state tracking broken → check TypedDict field names match what agents write

### Sign-off
- Date: ____
- Notes: ____

---

## Gate 3: API + Frontend (End of Day 9)

### Criteria

| # | Check | Command / Evidence | Status |
|---|-------|-------------------|--------|
| 3.1 | POST /api/process accepts file | `curl -X POST -F "file=@invoice.pdf" http://localhost:8000/api/process` → 202 + job_id | ☐ |
| 3.2 | POST /api/process rejects bad file | Upload .txt file → 400 error | ☐ |
| 3.3 | GET /api/status returns stage | Poll with job_id → current_stage updates | ☐ |
| 3.4 | GET /api/result returns JSON | After completion → full InvoiceJSON response | ☐ |
| 3.5 | GET /api/result 404 for unknown | Random UUID → 404 | ☐ |
| 3.6 | Swagger UI works end-to-end | Upload file via /docs → see result | ☐ |
| 3.7 | Frontend — upload works | Drag file into browser UI → file accepted | ☐ |
| 3.8 | Frontend — status shows | Pipeline stages visible and update during processing | ☐ |
| 3.9 | Frontend — JSON displays | Result appears with syntax highlighting | ☐ |
| 3.10 | Frontend — download works | Click Download → .json file saves to disk | ☐ |
| 3.11 | End-to-end in browser | Upload real invoice in UI → see correct JSON → download it | ☐ |

### If FAIL
- If API works but frontend doesn't → demo via Swagger UI (acceptable fallback)
- If file upload fails → check multipart handling, CORS settings
- If polling doesn't update → check background task is writing to job store
- If CORS error → add `CORSMiddleware` to FastAPI

### Sign-off
- Date: ____
- Notes: ____

---

## Gate 4: Integration Testing + Demo Ready (End of Day 10)

### Criteria

| # | Check | Command / Evidence | Status |
|---|-------|-------------------|--------|
| 4.1 | Invoice Template 1 (simple) | Upload → correct JSON with all fields | ☐ |
| 4.2 | Invoice Template 2 (complex, 10+ items) | Upload → line items extracted, arithmetic valid | ☐ |
| 4.3 | Invoice Template 3 (different layout) | Upload → extracts correctly without code changes | ☐ |
| 4.4 | Image invoice (scanned) | Upload PNG/JPEG → OCR + extraction works | ☐ |
| 4.5 | Validation demo | Invoice with wrong total → validation catches it | ☐ |
| 4.6 | Correction demo | Same invoice → correction fixes it → "corrected" status | ☐ |
| 4.7 | Performance | End-to-end ≤ 30 seconds | ☐ |
| 4.8 | Architecture diagram final | docs/architecture.mmd matches actual implementation | ☐ |
| 4.9 | README complete | Setup instructions work on clean machine (or Docker) | ☐ |
| 4.10 | Demo rehearsal | Full walkthrough completed without issues | ☐ |

### If FAIL
- If 1-2 templates fail → document as known limitation, demo with working ones
- If performance > 30s → check if OCR or LLM call is bottleneck, consider removing vision fallback
- If correction doesn't demo well → use pre-crafted invoice with known fixable error

### Sign-off
- Date: ____
- Notes: ____

---

## Summary Dashboard

```
Gate 0: ☐ PENDING / ☐ GREEN / ☐ RED
Gate 1: ☐ PENDING / ☐ GREEN / ☐ RED
Gate 2: ☐ PENDING / ☐ GREEN / ☐ RED
Gate 3: ☐ PENDING / ☐ GREEN / ☐ RED
Gate 4: ☐ PENDING / ☐ GREEN / ☐ RED
```

Update this dashboard daily. If any gate is RED for > 1 day, invoke the risk buffer strategy from PLAN.md.
