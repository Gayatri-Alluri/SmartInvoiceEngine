# PROMPT_SEQUENCES.md — Copilot Agent Mode Prompt Patterns

> **Purpose:** Exact prompts to feed Copilot Agent Mode for building each component.  
> **Strategy:** Specification-driven development — every prompt references SPEC.md sections.

---

## How to Use This Document

1. Open VS Code in Agent Mode
2. Copy the prompt for the current task
3. Paste into Copilot chat
4. Review generated code against SPEC.md
5. Run the gate check from CHECKPOINTS.md

---

## Phase 0: Scaffolding Prompts

### P0-1: Backend Scaffolding

```
Create the backend scaffolding for SmartInvoiceEngine following the project structure in SPEC.md §9.

Create these files:
- backend/app/__init__.py (empty)
- backend/app/main.py — FastAPI app with CORS middleware for localhost:3000, a /api/health endpoint returning {"status": "ok"}, and uvicorn runner
- backend/app/config.py — Pydantic Settings class reading from env vars per SPEC.md §8
- backend/requirements.txt — include: fastapi, uvicorn, pydantic, pydantic-settings, langchain-google-genai, langgraph, pymupdf, pytesseract, structlog, python-multipart, pytest, pytest-asyncio
- backend/.env.example — all variables from SPEC.md §8 with placeholder values
- backend/Dockerfile — Python 3.11 slim, install tesseract-ocr, copy app, run uvicorn

All empty __init__.py files for: api/, agents/, orchestrator/, models/, prompts/, utils/
```

### P0-2: Frontend Scaffolding

```
Create a Vite + React + TypeScript project in frontend/ with:
- Tailwind CSS configured
- Axios installed
- react-syntax-highlighter installed
- A minimal App.tsx that renders "Smart Invoice Engine" heading
- vite.config.ts with proxy to localhost:8000 for /api
- Dockerfile for production build (nginx)
- tsconfig with strict mode

Do not add any routing library. Single page app.
```

### P0-3: Docker Compose

```
Create docker-compose.yml at project root with two services:
- backend: builds from backend/Dockerfile, port 8000, env_file .env
- frontend: builds from frontend/Dockerfile, port 3000, depends_on backend

Include a .env file reference for GOOGLE_API_KEY.
```

---

## Phase 1: Core Agent Prompts

### P1-1: Domain Models

```
Create backend/app/models/invoice.py with ALL Pydantic v2 models from SPEC.md §3.
Copy the exact schemas: DocumentInput, OCRMethod, OCRResult, LineItem, TaxInfo, VendorInfo, BuyerInfo, ExtractedInvoice, ValidationError, ValidationResult, CorrectionEntry, CorrectionLog, ProcessingMetadata, InvoiceJSON.
Use proper Field validators where specified.
Do not add any extra models or fields beyond what SPEC.md defines.
```

### P1-2: OCR Agent

```
Implement backend/app/agents/ocr_agent.py following SPEC.md §2.1.

Function signature: def run_ocr(document: DocumentInput) -> OCRResult

Strategy:
1. Check mime_type: if "application/pdf" → try PyMuPDF first
2. If PyMuPDF returns empty text (scanned PDF) → try Tesseract
3. If mime_type is image (png/jpeg) → use Tesseract directly
4. If Tesseract confidence < config.OCR_CONFIDENCE_THRESHOLD → fallback to Gemini 1.5 Pro vision
5. If all fail → return OCRResult with empty text, confidence=0, error message

Import models from app.models.invoice. Import config from app.config.
Use structlog for logging each step.
Do not use classes. Pure function only.
```

### P1-3: Extraction Prompt Template

```
Create backend/app/prompts/extraction.py with two string constants:

EXTRACTION_SYSTEM_PROMPT — the system prompt from SPEC.md §6.1
EXTRACTION_USER_PROMPT_TEMPLATE — the user prompt template from SPEC.md §6.1, with {raw_text} placeholder

Export both as module-level constants. No functions needed.
```

### P1-4: Extraction Agent

```
Implement backend/app/agents/extraction_agent.py following SPEC.md §2.2.

Function signature: def run_extraction(ocr_result: OCRResult) -> ExtractedInvoice

Implementation:
- Use ChatGoogleGenerativeAI from langchain-google-genai with model from config, temperature=0
- Use .with_structured_output(ExtractedInvoice) for guaranteed schema compliance
- Construct messages from prompts/extraction.py templates, injecting ocr_result.raw_text
- If LLM call fails → retry once
- If both fail → return ExtractedInvoice with all fields None/empty
- Log token usage via structlog

Import models from app.models.invoice. Import prompts from app.prompts.extraction.
Pure function, no classes.
```

### P1-5: Validation Agent

```
Implement backend/app/agents/validation_agent.py following SPEC.md §2.3.

Function signature: def run_validation(invoice: ExtractedInvoice) -> ValidationResult

Implement ALL 5 rules from SPEC.md §10:
1. LINE_ITEMS_SUM: sum(line_items[].amount) == subtotal (±0.01 tolerance)
2. TOTAL_CALCULATION: subtotal + tax.amount == total_amount (±0.01)
3. REQUIRED_FIELDS: invoice_number, invoice_date, total_amount not None
4. DATE_FORMAT: dates are parseable (try ISO, then common formats)
5. NUMERIC_VALIDITY: all numeric fields >= 0

Return ValidationResult with is_valid=True only if zero errors.
Pure function — no LLM calls, no I/O, no imports beyond models and standard library.
```

### P1-6: Agent Tests

```
Create tests for Phase 1 agents:

backend/tests/test_ocr_agent.py:
- test_text_pdf: feed a text PDF → get non-empty raw_text, method=pymupdf
- test_image_ocr: feed a PNG → get non-empty raw_text, method=tesseract
- Use files from test-invoices/ folder

backend/tests/test_extraction_agent.py:
- test_extract_invoice: feed known OCRResult text → get ExtractedInvoice with key fields populated
- Mock the LLM call for unit test speed (use @pytest.mark.integration for real LLM test)

backend/tests/test_validation_agent.py:
- test_valid_invoice: all rules pass → is_valid=True
- test_line_items_sum_mismatch: wrong subtotal → catches error
- test_missing_required_field: no invoice_number → catches error
- test_total_calculation_mismatch: subtotal + tax ≠ total → catches error

Use pytest. Import models from app.models.invoice.
```

---

## Phase 2: Correction + Orchestrator Prompts

### P2-1: Correction Prompt Template

```
Create backend/app/prompts/correction.py with two string constants:

CORRECTION_SYSTEM_PROMPT — from SPEC.md §6.2
CORRECTION_USER_PROMPT_TEMPLATE — from SPEC.md §6.2, with {raw_text}, {extracted_json}, {errors_list} placeholders

Export as module-level constants.
```

### P2-2: Correction Agent

```
Implement backend/app/agents/correction_agent.py following SPEC.md §2.4.

Function signature: def run_correction(invoice: ExtractedInvoice, validation_result: ValidationResult, ocr_result: OCRResult) -> tuple[ExtractedInvoice, CorrectionLog]

Strategy:
1. For errors with auto_fixable=True (LINE_ITEMS_SUM, TOTAL_CALCULATION):
   - Apply rule-based fix: recalculate subtotal from line items, recalculate total from subtotal+tax
   - Log as method="rule_based"
2. For other errors:
   - Re-prompt Gemini 1.5 Pro with correction prompt template + error context
   - Use with_structured_output(ExtractedInvoice)
   - Log as method="llm_reanalysis"
3. Return corrected invoice + CorrectionLog

Pure function. Import models, prompts, config.
```

### P2-3: JSON Formatter

```
Implement backend/app/agents/formatter_agent.py following SPEC.md §2.5.

Function signature: def run_formatter(invoice: ExtractedInvoice, validation_result: ValidationResult, metadata: dict) -> InvoiceJSON

Pure data transformation:
- Calculate confidence_score from validation result + OCR confidence
- Determine validation_status: "passed" if no correction, "corrected" if corrections applied, "failed" if still invalid
- Package into InvoiceJSON model

No LLM calls. No I/O. Pure function.
```

### P2-4: LangGraph Orchestrator

```
Implement the LangGraph workflow in two files following SPEC.md §4:

backend/app/orchestrator/state.py:
- Define WorkflowState TypedDict matching SPEC.md §4 exactly

backend/app/orchestrator/graph.py:
- Import all agents from app.agents.*
- Define node functions that read/write WorkflowState
- Build StateGraph with nodes: ocr_node, extraction_node, validation_node, correction_node, formatter_node
- Add conditional edge after validation: if is_valid OR attempts >= 2 → formatter, else → correction
- After correction → back to validation (loop)
- Export compiled graph and a process_invoice(document: DocumentInput) -> InvoiceJSON function

Use langgraph StateGraph. Follow the graph structure from SPEC.md §4.
```

---

## Phase 3: API + Frontend Prompts

### P3-1: API Schemas

```
Create backend/app/api/schemas.py with request/response models for the API:

- ProcessResponse: job_id (str), status (str), message (str)
- StatusResponse: job_id (str), status (str), current_stage (str), stages_completed (list[str]), elapsed_ms (int)
- ResultResponse: job_id (str), status (str), result (Optional[InvoiceJSON]), error (Optional[str])

These are API-layer models (not domain models). Import InvoiceJSON from models.
```

### P3-2: API Routes

```
Implement backend/app/api/routes.py following SPEC.md §5:

Three endpoints:
1. POST /api/process — accept UploadFile, validate mime type + size, create job_id, start background task, return 202
2. GET /api/status/{job_id} — return current stage from in-memory job store, 404 if not found
3. GET /api/result/{job_id} — return InvoiceJSON when complete, error when failed, 404 if not found

Use in-memory dict for job store (module-level).
Use asyncio.create_task to run pipeline in background.
Import process_invoice from orchestrator.
All handlers are async def. Validate file type (pdf, png, jpeg) and size (< 10MB) before processing.
```

### P3-3: Frontend Types

```
Create frontend/src/types/invoice.ts with TypeScript interfaces mirroring the Pydantic models:

- ProcessResponse { job_id: string; status: string; message: string }
- StatusResponse { job_id: string; status: string; current_stage: string; stages_completed: string[]; elapsed_ms: number }
- InvoiceJSON { metadata: ProcessingMetadata; invoice: ExtractedInvoice }
- ProcessingMetadata { processing_time_ms: number; confidence_score: number; validation_status: string; corrections_applied: CorrectionEntry[]; source_file: string; ocr_method: string }
- ExtractedInvoice { invoice_number, invoice_date, due_date, currency, vendor, buyer, line_items, subtotal, tax, total_amount }
- All sub-types: LineItem, TaxInfo, VendorInfo, BuyerInfo, CorrectionEntry

Export all interfaces.
```

### P3-4: API Service

```
Create frontend/src/services/api.ts:

- Base URL: /api (proxied to backend via Vite config)
- processInvoice(file: File): POST /api/process with FormData → returns ProcessResponse
- getStatus(jobId: string): GET /api/status/{jobId} → returns StatusResponse
- getResult(jobId: string): GET /api/result/{jobId} → returns ResultResponse

Use Axios. Export all functions. No try/catch here — let components handle errors.
```

### P3-5: React Components

```
Create the frontend components following this spec:

frontend/src/components/UploadForm.tsx:
- Drag & drop zone + file input (accept .pdf, .png, .jpeg)
- Show file name when selected
- "Process Invoice" button (disabled until file selected)
- Calls onSubmit(file) prop when clicked
- Tailwind styling

frontend/src/components/PipelineStatus.tsx:
- Props: stages_completed (string[]), current_stage (string), status (string)
- Show 5 stage indicators: OCR, Extraction, Validation, Correction, Output
- Completed = green ✅, Current = spinning/blue, Pending = gray ○
- Tailwind styling

frontend/src/components/ResultViewer.tsx:
- Props: result (InvoiceJSON)
- Display JSON with react-syntax-highlighter (language="json", one of the dark themes)
- Tailwind container styling

frontend/src/components/DownloadButton.tsx:
- Props: result (InvoiceJSON), filename (string)
- Click → creates Blob → triggers browser download as .json file
- Tailwind button styling

frontend/src/hooks/useProcessInvoice.ts:
- Custom hook that manages: upload → poll status every 2s → fetch result on completion
- Returns: { upload, status, result, error, isProcessing }
- Uses api.ts service functions

frontend/src/App.tsx:
- Wire all components together using useProcessInvoice hook
- Layout: header → upload form → status (when processing) → result (when done) + download
- Tailwind responsive layout
```

---

## Prompt Patterns (Reusable)

### Pattern: Reference SPEC.md

```
Implement [file path] following SPEC.md §[section number].
[paste relevant spec section or key constraints]
```

### Pattern: Write Tests

```
Write pytest tests for [agent_name] covering:
- Happy path: [description]
- Error case: [description]
- Edge case: [description]
Mock LLM calls using unittest.mock.patch. Use fixtures for test data.
```

### Pattern: Fix Failing Gate

```
The following gate check is failing: [paste check command + error output]
The expected behavior per SPEC.md is: [paste spec]
Diagnose and fix the issue. Do not change the spec — fix the code.
```

### Pattern: Integration Debug

```
The end-to-end pipeline fails at [stage]. Error: [paste error]
Here is the WorkflowState at that point: [paste state]
The expected flow per SPEC.md §4 is: [paste graph structure]
Fix the issue while maintaining the agent contract.
```

---

## Anti-Patterns (Prompts to AVOID)

| Bad Prompt | Why It Fails |
|-----------|-------------|
| "Build me an invoice processor" | Too vague, Copilot will invent its own architecture |
| "Add error handling everywhere" | Over-engineers, adds try/catch to pure functions |
| "Make it production-ready" | Ambiguous — might add auth, DB, logging frameworks |
| "Refactor to be cleaner" | Subjective, may break working code |
| "Add comments to explain the code" | Violates copilot-instructions.md |
