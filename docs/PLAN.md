# PLAN.md — 2-Week Execution Plan

> **Derived from:** REQUIREMENTS.md (frozen) + SPEC.md  
> **Rule:** Only in-scope features (F-1 through F-8) are planned. No stretch goals in the timeline.

---

## Phases Overview

| Phase | Days | Focus | Gate |
|-------|------|-------|------|
| Phase 0 | Day 1-2 | Planning & Scaffolding | All docs frozen, project runs locally |
| Phase 1 | Day 3-5 | Core Agents (OCR + Extraction + Validation) | 3 agents pass unit tests |
| Phase 2 | Day 6-7 | Correction + Orchestrator | Full pipeline works end-to-end in terminal |
| Phase 3 | Day 8-9 | API + Frontend | Upload → JSON visible in browser |
| Phase 4 | Day 10 | Integration Testing + Demo Prep | Demo-ready with real invoices |

---

## Daily Milestones

### Phase 0: Planning & Scaffolding (Day 1-2)

| Day | Tasks | Deliverable | Maps to |
|-----|-------|-------------|---------|
| **Day 1** | - Finalize BRD, REQUIREMENTS.md | Frozen planning docs | — |
| | - Write SPEC.md, PLAN.md, DEPENDENCIES.md | | |
| | - Write CHECKPOINTS.md, DELIVERABLES.md | | |
| **Day 2** | - Create project folder structure per SPEC.md §9 | Scaffolding complete | — |
| | - Set up backend: FastAPI + requirements.txt + Dockerfile | `python -m app.main` starts |
| | - Set up frontend: Vite + React + Tailwind + Dockerfile | `npm run dev` starts |
| | - Create docker-compose.yml | `docker-compose up` runs both |
| | - Create .env.example, config.py | Config loads from env |
| | - Write copilot-instructions.md, README.md | Repo entry point ready |

**Gate 0:** `docker-compose up` starts both services with hello-world endpoints. All planning docs committed.

---

### Phase 1: Core Agents (Day 3-5)

| Day | Tasks | Deliverable | Maps to |
|-----|-------|-------------|---------|
| **Day 3** | - Implement Pydantic models (models/invoice.py) | All schemas importable | F-1, F-2 |
| | - Implement OCR Agent (ocr_agent.py) | | |
| | - PyMuPDF text extraction | | |
| | - Tesseract image extraction | | |
| | - GPT-4o vision fallback | | |
| | - Write test_ocr_agent.py | OCR agent passes tests | |
| **Day 4** | - Write extraction prompt templates | Prompts tested manually | F-2 |
| | - Implement Extraction Agent (extraction_agent.py) | | |
| | - GPT-4o structured output call | | |
| | - Response parsing into ExtractedInvoice | | |
| | - Write test_extraction_agent.py | Extraction agent passes tests | |
| **Day 5** | - Implement Validation Agent (validation_agent.py) | All 5 rules working | F-3 |
| | - All 5 validation rules | | |
| | - Write test_validation_agent.py | Validation agent passes tests | |
| | - Test agents together manually (OCR → Extraction → Validation) | Chain works in script | |

**Gate 1:** `pytest tests/test_ocr_agent.py tests/test_extraction_agent.py tests/test_validation_agent.py` — all green.

---

### Phase 2: Correction + Orchestrator (Day 6-7)

| Day | Tasks | Deliverable | Maps to |
|-----|-------|-------------|---------|
| **Day 6** | - Implement Correction Agent (correction_agent.py) | Correction fixes errors | F-4 |
| | - Rule-based arithmetic fixes | | |
| | - LLM re-prompt with error context | | |
| | - Retry logic (max 2) | | |
| | - Implement JSON Formatter (formatter_agent.py) | Formatter outputs schema | F-5 |
| | - Write test_correction_agent.py | Tests pass | |
| **Day 7** | - Implement LangGraph workflow (orchestrator/graph.py) | Pipeline runs end-to-end | F-6 |
| | - Define WorkflowState (orchestrator/state.py) | | |
| | - Wire all 5 agents as graph nodes | | |
| | - Implement conditional edge (should_correct?) | | |
| | - Test full pipeline via Python script | Upload file → get JSON in terminal | |

**Gate 2:** Run `python -c "from app.orchestrator.graph import process_invoice; ..."` with a real PDF → get valid InvoiceJSON output.

---

### Phase 3: API + Frontend (Day 8-9)

| Day | Tasks | Deliverable | Maps to |
|-----|-------|-------------|---------|
| **Day 8** | - Implement API routes (api/routes.py) | API functional | F-7 |
| | - POST /api/process (file upload → start job) | | |
| | - GET /api/status/{id} (poll state) | | |
| | - GET /api/result/{id} (get JSON) | | |
| | - In-memory job store (dict) | | |
| | - Background task for pipeline execution | | |
| | - Test via Swagger UI (/docs) | Upload works in Swagger | |
| **Day 9** | - Implement React components | UI functional | F-8 |
| | - UploadForm.tsx (drag & drop + file picker) | | |
| | - PipelineStatus.tsx (stage indicators) | | |
| | - ResultViewer.tsx (syntax-highlighted JSON) | | |
| | - DownloadButton.tsx | | |
| | - API client (services/api.ts) | | |
| | - Polling hook (useProcessInvoice.ts) | | |
| | - Wire end-to-end: upload in browser → see JSON | Works in browser | |

**Gate 3:** Open browser → upload PDF → see pipeline stages → view JSON result → download works.

---

### Phase 4: Integration Testing + Demo Prep (Day 10)

| Day | Tasks | Deliverable | Maps to |
|-----|-------|-------------|---------|
| **Day 10** | - Test with 5 different invoice templates | All pass or gracefully degrade | SC-2 |
| | - Test auto-correction demo scenario | Correction visible in output | SC-4 |
| | - Test validation failure detection | Error caught and shown | SC-3 |
| | - Fix any integration bugs | Stable pipeline | |
| | - Finalize architecture.mmd diagram | Diagram matches reality | SC-6 |
| | - Update README.md with final setup instructions | Repo ready for walkthrough | SC-5 |
| | - Prepare demo script (which invoices, what order) | Demo rehearsed | SC-1 |

**Gate 4:** Full demo rehearsal passes — all 5 success criteria met.

---

## Risk Buffer Strategy

| If Behind By | Cut This | Impact |
|---|---|---|
| 0.5 day | Reduce test coverage (keep happy path only) | Low — manual testing covers gaps |
| 1 day | Simplify UI (no status animation, basic layout) | Medium — functional but ugly |
| 1.5 days | Drop GPT-4o vision fallback (use Tesseract only) | Medium — some images may fail |
| 2+ days | **Red flag** — cut correction agent retries to 1 | High — demo scope reduced |

---

## Daily Standup Questions

Each day, answer:
1. What did I complete? (reference Day X tasks)
2. What's blocked?
3. Am I on track for the phase gate?

---

## Dependency Summary (from DEPENDENCIES.md)

```
Day 2: Scaffolding (no deps)
Day 3: Models → OCR Agent (models must exist first)
Day 4: OCR Agent → Extraction Agent (needs OCRResult as input)
Day 5: Extraction Agent → Validation Agent (needs ExtractedInvoice)
Day 6: Validation Agent → Correction Agent (needs ValidationResult)
Day 7: All Agents → Orchestrator (wires them together)
Day 8: Orchestrator → API (API triggers the graph)
Day 9: API → Frontend (frontend calls the API)
Day 10: Everything → Integration Tests
```
