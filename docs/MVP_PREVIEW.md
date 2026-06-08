# MVP_PREVIEW.md — What This Looks Like After 2 Weeks

> This document describes the exact experience an evaluator will see during the live demo. No aspirational features — only what will actually work.

---

## Demo Script (End-to-End)

### Step 1: Open the App
- Browser opens to `http://localhost:3000`
- Clean UI with a file upload area and "Process Invoice" button
- No login screen, no sidebar clutter

### Step 2: Upload an Invoice
- User drags a PDF or image file onto the upload zone (or clicks to browse)
- File name appears with a preview thumbnail
- "Process Invoice" button activates

### Step 3: Processing Begins
- User clicks "Process Invoice"
- A pipeline status tracker appears showing stages:
  ```
  ● OCR → ● Extraction → ● Validation → ○ Correction → ○ Output
  ```
- Each stage lights up as it completes (real-time via polling/SSE)

### Step 4: Result Displayed
- JSON result appears in a syntax-highlighted viewer
- Metadata section shows:
  - Processing time (e.g., "12.4s")
  - Confidence score (e.g., "0.92")
  - Validation status: ✅ Passed or ⚠️ Corrected
  - Corrections applied (if any)
- Invoice data section shows all extracted fields in readable JSON

### Step 5: Download
- User clicks "Download JSON" button
- Browser downloads the structured JSON file

---

## What the Evaluator Will See Working

| Capability | Demo Proof |
|-----------|-----------|
| PDF text extraction | Upload a text-based PDF → correct JSON output |
| Image OCR | Upload a scanned invoice image (PNG/JPEG) → correct JSON output |
| Varied templates | Process 3 visually different invoices → all produce valid JSON |
| Field extraction | All 11 fields populated correctly (or null if absent) |
| Validation pass | Invoice with correct totals → "validation_status: passed" |
| Validation failure detection | Invoice with mismatched totals → validation catches it |
| Auto-correction | Mismatched invoice → correction agent fixes it → "corrections_applied" shows what changed |
| Pipeline visibility | UI shows each stage progressing in real-time |
| Structured output | JSON matches the defined schema exactly |

---

## UI Wireframe (What It Looks Like)

```
┌─────────────────────────────────────────────────────────┐
│  Smart Invoice Engine                                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────┐                │
│  │                                     │                │
│  │   📄 Drop invoice here              │                │
│  │      or click to browse             │                │
│  │                                     │                │
│  │   Supported: PDF, PNG, JPEG         │                │
│  └─────────────────────────────────────┘                │
│                                                         │
│  [ Process Invoice ]                                    │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Pipeline Status                                        │
│  ✅ OCR → ✅ Extraction → ✅ Validation → ⏭ → ✅ Output │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Result                                     [Download]  │
│  ┌─────────────────────────────────────────────────┐    │
│  │ {                                               │    │
│  │   "metadata": {                                 │    │
│  │     "processing_time_ms": 12400,                │    │
│  │     "confidence_score": 0.92,                   │    │
│  │     "validation_status": "passed"               │    │
│  │   },                                            │    │
│  │   "invoice": {                                  │    │
│  │     "invoice_number": "INV-2026-0042",          │    │
│  │     "total_amount": 2200.00,                    │    │
│  │     ...                                         │    │
│  │   }                                             │    │
│  │ }                                               │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## What Will NOT Be in the Demo

| Missing Feature | Why It's OK |
|----------------|-------------|
| No login page | Out of scope — single user demo |
| No history of past uploads | Ephemeral processing — deliberate tradeoff |
| No batch upload | One-at-a-time is sufficient for demo |
| No mobile responsiveness | Desktop demo only |
| No loading skeleton animations | Functional status tracker is enough |
| No dark mode | Cosmetic — deferred |

---

## Test Invoices for Demo

| # | Invoice Template | Tests |
|---|-----------------|-------|
| 1 | Simple invoice (few line items, clear layout) | Baseline extraction accuracy |
| 2 | Complex invoice (10+ line items, tax breakdown) | Line item handling, arithmetic validation |
| 3 | Scanned image invoice (slightly rotated/noisy) | OCR robustness |
| 4 | Invoice with deliberate error (total ≠ sum) | Validation detection + auto-correction |
| 5 | Different visual layout (horizontal vs vertical) | Template generalization |

---

## Technical Stack Visible in Demo

| Layer | Technology | Visible How |
|-------|-----------|-------------|
| Frontend | React + Tailwind | The UI itself |
| Backend | FastAPI | API response speed shown in metadata |
| Orchestration | LangGraph | Pipeline stages visible in status tracker |
| OCR | Tesseract / PyMuPDF | Image invoices processed correctly |
| LLM | Gemini 2.5 Flash | Extraction quality across templates |
| Containerization | Docker Compose | Single `docker-compose up` starts everything |

---

## "Wow Factor" Moments in Demo

1. **Template-agnostic**: Same code processes visually different invoices — no configuration
2. **Self-healing**: Show a broken invoice → watch correction agent fix it → JSON comes out clean
3. **Transparent pipeline**: User sees exactly which stage is running — not a black box
4. **Speed**: Upload to JSON in under 30 seconds
5. **Real data**: Not mocked — actual invoice images producing real extractions
