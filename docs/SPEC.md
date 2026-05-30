# SPEC.md — Technical Specification

> **Source of truth** for implementation. If code contradicts this document, the code is wrong.  
> **Derived from:** REQUIREMENTS.md (frozen)

---

## 1. Tech Stack

### Backend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.11+ | LangChain/LangGraph ecosystem is Python-first |
| Framework | FastAPI | 0.115.x | Async, Pydantic-native, auto-generated OpenAPI docs |
| Orchestration | LangGraph | 0.2.x | Stateful graph, conditional edges, built-in retries |
| LLM Client | langchain-google-genai | 2.x | Native LangGraph integration, free tier available |
| LLM | Gemini 1.5 Pro (Google) | Latest | Multimodal, structured output, free tier (2 RPM), high accuracy |
| OCR (text PDF) | PyMuPDF (fitz) | 1.24.x | Fast native text extraction, no external dependency |
| OCR (scanned/image) | pytesseract | 0.3.x | Free, open-source, well-supported |
| Schemas/Validation | Pydantic v2 | 2.x | Type-safe, JSON serialization, FastAPI-native |
| Logging | structlog | 24.x | Structured JSON logs, per-stage tracing |
| Testing | pytest + pytest-asyncio | 8.x | Standard Python testing with async support |
| API Documentation | Swagger UI + ReDoc | (via FastAPI) | Auto-generated at `/docs` and `/redoc`, interactive testing |

### Frontend

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Framework | React | 18.x | Component-based, fast iteration |
| Language | TypeScript | 5.x | Type safety, better IDE support |
| Styling | Tailwind CSS | 3.x | Utility-first, no custom CSS needed |
| HTTP Client | Axios | 1.x | Multipart upload support, simple API |
| JSON Display | react-syntax-highlighter | 15.x | Syntax-highlighted JSON viewer |
| Build Tool | Vite | 5.x | Fast HMR, modern bundling |
| Runtime | Node.js | 18+ | LTS, stable |

### Infrastructure

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Containerization | Docker Compose | Single command startup, includes Tesseract |
| Package Management | pip + requirements.txt | Simple, no Poetry overhead for 2-week project |

---

## 2. Agent Specifications

### 2.1 OCR Agent

| Property | Value |
|----------|-------|
| **Responsibility** | Extract raw text from uploaded document |
| **Input** | `DocumentInput` (file bytes + filename + mime type) |
| **Output** | `OCRResult` (raw_text + confidence + method_used) |
| **Strategy** | 1. If PDF with embedded text → PyMuPDF extract. 2. If scanned PDF/image → Tesseract. 3. If Tesseract confidence < 0.6 → fallback to Gemini 1.5 Pro vision. |
| **Error Handling** | If all methods fail → return `OCRResult` with empty text + confidence 0 + error message |
| **Timeout** | 15 seconds |

### 2.2 Extraction Agent

| Property | Value |
|----------|-------|
| **Responsibility** | Extract structured invoice fields from raw text using LLM |
| **Input** | `OCRResult` (raw_text) |
| **Output** | `ExtractedInvoice` (all 11 fields, nullable) |
| **Strategy** | Gemini 1.5 Pro with structured output (response_mime_type=application/json). System prompt with field definitions + few-shot examples. Temperature 0. |
| **Error Handling** | If LLM call fails → retry once. If still fails → return partial extraction with nulls. |
| **Timeout** | 20 seconds |

### 2.3 Validation Agent

| Property | Value |
|----------|-------|
| **Responsibility** | Validate extracted data for correctness and consistency |
| **Input** | `ExtractedInvoice` |
| **Output** | `ValidationResult` (is_valid + errors list) |
| **Rules** | 1. sum(line_item.amount) == subtotal (±0.01 tolerance). 2. subtotal + tax.amount == total_amount (±0.01). 3. Required fields present: invoice_number, invoice_date, total_amount. 4. Dates parseable (ISO or common formats). 5. Numeric fields are valid numbers. |
| **Error Handling** | Pure function — cannot fail. Returns result always. |
| **Timeout** | < 1 second (no I/O) |

### 2.4 Correction Agent

| Property | Value |
|----------|-------|
| **Responsibility** | Fix extraction errors identified by validation |
| **Input** | `ExtractedInvoice` + `ValidationResult` + `OCRResult` (original text) |
| **Output** | `CorrectedInvoice` (same schema as ExtractedInvoice) + `CorrectionLog` |
| **Strategy** | 1. For arithmetic errors → apply rule-based fix (recalculate from line items). 2. For other errors → re-prompt Gemini 1.5 Pro with error context + original text. Temperature 0. |
| **Max Retries** | 2 attempts total |
| **Error Handling** | If correction fails after max retries → return best-effort data with error flags |
| **Timeout** | 20 seconds per attempt |

### 2.5 JSON Formatter

| Property | Value |
|----------|-------|
| **Responsibility** | Package validated data into final JSON schema with metadata |
| **Input** | `ExtractedInvoice` (or `CorrectedInvoice`) + `ValidationResult` + processing metadata |
| **Output** | `InvoiceJSON` (final output schema) |
| **Error Handling** | Pure function — cannot fail. |
| **Timeout** | < 1 second |

---

## 3. I/O Schemas (Pydantic Models)

```python
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# --- Input ---

class DocumentInput(BaseModel):
    file_bytes: bytes
    filename: str
    mime_type: str  # "application/pdf", "image/png", "image/jpeg"


# --- OCR ---

class OCRMethod(str, Enum):
    PYMUPDF = "pymupdf"
    TESSERACT = "tesseract"
    GPT4O_VISION = "gpt4o_vision"


class OCRResult(BaseModel):
    raw_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    method_used: OCRMethod
    error: Optional[str] = None


# --- Extraction ---

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float


class TaxInfo(BaseModel):
    percentage: Optional[float] = None
    amount: Optional[float] = None


class VendorInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class BuyerInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class ExtractedInvoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    vendor: Optional[VendorInfo] = None
    buyer: Optional[BuyerInfo] = None
    line_items: list[LineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[TaxInfo] = None
    total_amount: Optional[float] = None


# --- Validation ---

class ValidationError(BaseModel):
    field: str
    rule: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationError] = []


# --- Correction ---

class CorrectionEntry(BaseModel):
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    method: str  # "rule_based" or "llm_reanalysis"


class CorrectionLog(BaseModel):
    attempt_number: int
    corrections: list[CorrectionEntry] = []
    success: bool


# --- Final Output ---

class ProcessingMetadata(BaseModel):
    processing_time_ms: int
    confidence_score: float
    validation_status: str  # "passed", "corrected", "failed"
    corrections_applied: list[CorrectionEntry] = []
    source_file: str
    ocr_method: OCRMethod


class InvoiceJSON(BaseModel):
    metadata: ProcessingMetadata
    invoice: ExtractedInvoice
```

---

## 4. LangGraph State Schema

```python
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    # Input
    document: DocumentInput

    # Pipeline outputs (populated stage by stage)
    ocr_result: Optional[OCRResult]
    extracted_invoice: Optional[ExtractedInvoice]
    validation_result: Optional[ValidationResult]
    correction_log: list[CorrectionLog]
    correction_attempts: int

    # Final
    final_output: Optional[InvoiceJSON]

    # Metadata
    current_stage: str  # "ocr", "extraction", "validation", "correction", "formatting", "complete", "error"
    error: Optional[str]
    start_time: float
```

### Graph Structure

```
START → ocr_node → extraction_node → validation_node → should_correct?
                                                          │
                                            ┌─────────────┴──────────────┐
                                            │                            │
                                         is_valid=True              is_valid=False
                                            │                    AND attempts < 2
                                            ▼                            │
                                      formatter_node                     ▼
                                            │                    correction_node
                                            ▼                            │
                                           END                           ▼
                                                                 validation_node
                                                                   (loop back)
```

---

## 5. API Contracts

### Base URL: `http://localhost:8000/api`

---

### POST `/api/process`

Upload and process an invoice document.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (binary) — PDF, PNG, or JPEG

**Response (202 Accepted):**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "message": "Invoice processing started"
}
```

**Error (400):**
```json
{
  "detail": "Unsupported file type. Accepted: pdf, png, jpeg"
}
```

**Error (413):**
```json
{
  "detail": "File size exceeds 10 MB limit"
}
```

---

### GET `/api/status/{job_id}`

Poll processing status.

**Response (200):**
```json
{
  "job_id": "uuid-string",
  "status": "processing",
  "current_stage": "extraction",
  "stages_completed": ["ocr"],
  "elapsed_ms": 5200
}
```

**Status values:** `processing`, `completed`, `failed`

---

### GET `/api/result/{job_id}`

Get the final extraction result.

**Response (200) — when status=completed:**
```json
{
  "job_id": "uuid-string",
  "status": "completed",
  "result": {
    "metadata": { ... },
    "invoice": { ... }
  }
}
```

**Response (200) — when status=failed:**
```json
{
  "job_id": "uuid-string",
  "status": "failed",
  "error": "OCR extraction returned empty text",
  "partial_result": null
}
```

**Response (404):**
```json
{
  "detail": "Job not found"
}
```

---

### GET `/docs`

Swagger UI — interactive API documentation.

### GET `/redoc`

ReDoc — alternative API documentation.

---

## 6. Prompt Templates

### 6.1 Extraction Prompt

**System:**
```
You are an invoice data extraction specialist. Extract structured data from the provided invoice text.
Return ONLY valid JSON matching the specified schema. If a field is not present in the invoice, set it to null.
Do not invent or hallucinate data. Extract only what is explicitly stated in the text.
```

**User:**
```
Extract the following fields from this invoice text:

INVOICE TEXT:
---
{raw_text}
---

Return a JSON object with these fields:
- invoice_number (string or null)
- invoice_date (ISO date string or null)
- due_date (ISO date string or null)
- currency (3-letter ISO code or null)
- vendor: {name, address} (or null)
- buyer: {name, address} (or null)
- line_items: [{description, quantity, unit_price, amount}] (array, may be empty)
- subtotal (number or null)
- tax: {percentage, amount} (or null)
- total_amount (number or null)
```

### 6.2 Correction Prompt

**System:**
```
You are an invoice data correction specialist. The previous extraction had validation errors.
Re-analyze the original invoice text and fix the identified errors.
Return the COMPLETE corrected invoice data as JSON. Do not hallucinate — only fix what is provably wrong.
```

**User:**
```
The following extraction has validation errors. Please correct them.

ORIGINAL INVOICE TEXT:
---
{raw_text}
---

CURRENT EXTRACTION:
{extracted_json}

VALIDATION ERRORS:
{errors_list}

Return the corrected complete invoice JSON.
```

### 6.3 Vision OCR Prompt (fallback)

**System:**
```
You are an OCR specialist. Extract ALL text visible in this invoice image.
Preserve the layout structure as much as possible. Include all numbers, dates, and labels exactly as shown.
```

**User:**
```
Extract all text from this invoice image. Return only the raw text, preserving layout.
```

---

## 7. Error Handling Strategy

| Stage | Failure Mode | Action |
|-------|-------------|--------|
| Upload | Invalid file type | Return 400 immediately |
| Upload | File too large | Return 413 immediately |
| OCR | PyMuPDF returns empty text | Fallback to Tesseract |
| OCR | Tesseract confidence < 0.6 | Fallback to Gemini 1.5 Pro vision |
| OCR | All methods fail | Set status=failed, return error |
| Extraction | LLM timeout | Retry once |
| Extraction | LLM returns invalid JSON | Retry once with stricter prompt |
| Extraction | Both retries fail | Set status=failed |
| Validation | N/A (pure function) | Always succeeds |
| Correction | LLM fails | Decrement remaining attempts, retry or give up |
| Correction | Max retries exhausted | Return best-effort with validation_status="failed" |
| Formatter | N/A (pure function) | Always succeeds |

---

## 8. Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | — | Google AI API key for Gemini |
| `LLM_MODEL` | No | `gemini-1.5-pro` | Model name |
| `MAX_FILE_SIZE_MB` | No | `10` | Maximum upload file size |
| `MAX_CORRECTION_RETRIES` | No | `2` | Max auto-correction attempts |
| `OCR_CONFIDENCE_THRESHOLD` | No | `0.6` | Below this → fallback to vision |
| `API_HOST` | No | `0.0.0.0` | Backend host |
| `API_PORT` | No | `8000` | Backend port |
| `FRONTEND_PORT` | No | `3000` | Frontend port |
| `LOG_LEVEL` | No | `INFO` | Logging level |

---

## 9. Project Structure

```
SmartInvoiceEngine/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings from env vars
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py             # API endpoints
│   │   │   └── schemas.py            # Request/response models
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_agent.py          # OCR processing logic
│   │   │   ├── extraction_agent.py   # LLM extraction
│   │   │   ├── validation_agent.py   # Rule-based validation
│   │   │   ├── correction_agent.py   # LLM + rule correction
│   │   │   └── formatter_agent.py    # JSON packaging
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py              # LangGraph definition
│   │   │   └── state.py              # WorkflowState schema
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── invoice.py            # Pydantic domain models
│   │   ├── prompts/
│   │   │   ├── extraction.py         # Extraction prompt templates
│   │   │   └── correction.py         # Correction prompt templates
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logging.py            # Structured logging setup
│   ├── tests/
│   │   ├── test_ocr_agent.py
│   │   ├── test_extraction_agent.py
│   │   ├── test_validation_agent.py
│   │   ├── test_correction_agent.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── components/
│   │   │   ├── UploadForm.tsx
│   │   │   ├── PipelineStatus.tsx
│   │   │   ├── ResultViewer.tsx
│   │   │   └── DownloadButton.tsx
│   │   ├── services/
│   │   │   └── api.ts               # Axios API client
│   │   ├── types/
│   │   │   └── invoice.ts           # TypeScript interfaces
│   │   └── hooks/
│   │       └── useProcessInvoice.ts  # Polling hook
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── docs/
│   ├── BRD.md
│   └── architecture.mmd
├── test-invoices/                     # Sample invoices for demo
├── REQUIREMENTS.md
├── SPEC.md
├── PLAN.md
├── DEPENDENCIES.md
├── CHECKPOINTS.md
├── DELIVERABLES.md
├── FUTURE_VISION.md
├── MVP_PREVIEW.md
├── PROMPT_SEQUENCES.md
├── .github/
│   └── copilot-instructions.md
└── README.md
```

---

## 10. Validation Rules (Detailed)

```python
VALIDATION_RULES = [
    {
        "id": "LINE_ITEMS_SUM",
        "rule": "sum(line_items[].amount) == subtotal",
        "tolerance": 0.01,
        "severity": "error",
        "auto_fixable": True,  # Recalculate subtotal from line items
    },
    {
        "id": "TOTAL_CALCULATION",
        "rule": "subtotal + tax.amount == total_amount",
        "tolerance": 0.01,
        "severity": "error",
        "auto_fixable": True,  # Recalculate total
    },
    {
        "id": "REQUIRED_FIELDS",
        "rule": "invoice_number AND invoice_date AND total_amount are not null",
        "severity": "error",
        "auto_fixable": False,  # Needs LLM re-extraction
    },
    {
        "id": "DATE_FORMAT",
        "rule": "invoice_date and due_date are parseable dates",
        "severity": "warning",
        "auto_fixable": False,
    },
    {
        "id": "NUMERIC_VALIDITY",
        "rule": "all numeric fields are valid numbers >= 0",
        "severity": "error",
        "auto_fixable": False,
    },
]
```
