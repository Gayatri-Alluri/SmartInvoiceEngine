# Business Requirements Document (BRD)

## Smart Invoice Engine — Multi-Modal Document Data Extraction: Invoice-to-JSON Processor

| Field | Detail |
|-------|--------|
| **Project Name** | Smart Invoice Engine |
| **Version** | 1.0 |
| **Date** | 2026-05-27 |
| **Author** | Gayatri A |
| **Status** | Draft |

---

## 1. Executive Summary

Build a production-grade system that accepts PDF and image-based invoices, extracts structured data using OCR and AI-powered extraction, validates correctness, auto-corrects errors, and outputs a standardized JSON representation. The system handles diverse invoice templates without manual configuration per template.

---

## 2. Business Objectives

| # | Objective |
|---|-----------|
| BO-1 | Eliminate manual data entry from invoices |
| BO-2 | Achieve high extraction accuracy across varied invoice formats |
| BO-3 | Reduce invoice processing time from minutes (manual) to seconds (automated) |
| BO-4 | Provide structured, machine-readable JSON output for downstream integration |
| BO-5 | Self-correct extraction errors without human intervention where possible |

---

## 3. Scope

### 3.1 In Scope

- PDF document ingestion (text-based and scanned)
- Image document ingestion (PNG, JPEG, TIFF)
- OCR text extraction
- AI-powered structured data extraction (key-value pairs, line items)
- Rule-based and AI-based validation
- Auto-correction with retry mechanism
- Structured JSON output
- Web-based UI for upload and result viewing
- Orchestrated workflow (end-to-end pipeline)

### 3.2 Out of Scope

- ERP/accounting system integration
- Multi-language invoice support (English only for v1.0)
- Batch processing of 1000+ documents simultaneously
- User authentication and multi-tenancy
- Invoice approval workflows

---

## 4. Stakeholders

| Role | Responsibility |
|------|---------------|
| Product Owner | Defines acceptance criteria, prioritization |
| Developer | Design, implementation, testing |
| End User | Uploads invoices, reviews extracted JSON |
| Evaluator | Assesses deliverable quality, architecture, demo |

---

## 5. Functional Requirements

### FR-1: Document Upload

| ID | Requirement |
|----|-------------|
| FR-1.1 | System shall accept PDF files (single and multi-page) |
| FR-1.2 | System shall accept image files (PNG, JPEG) |
| FR-1.3 | System shall validate file type and size before processing |
| FR-1.4 | Maximum file size: 10 MB |

### FR-2: OCR Feature

| ID | Requirement |
|----|-------------|
| FR-2.1 | System shall extract raw text from text-based PDFs |
| FR-2.2 | System shall extract raw text from scanned/image-based documents using OCR |
| FR-2.3 | System shall preserve spatial/positional context of text where possible |
| FR-2.4 | System shall handle low-quality scans gracefully (return partial text with confidence indicator) |

### FR-3: Data Extraction Feature

| ID | Requirement |
|----|-------------|
| FR-3.1 | System shall extract the following fields from invoice text: |
| | - Invoice Number |
| | - Invoice Date |
| | - Due Date |
| | - Vendor/Supplier Name |
| | - Vendor Address |
| | - Buyer/Customer Name |
| | - Line Items (description, quantity, unit price, amount) |
| | - Subtotal |
| | - Tax (percentage and amount) |
| | - Total Amount |
| | - Currency |
| FR-3.2 | System shall handle missing fields gracefully (mark as null, not fail) |
| FR-3.3 | System shall work across varied invoice templates without template-specific configuration |

### FR-4: Validation Feature

| ID | Requirement |
|----|-------------|
| FR-4.1 | System shall validate: sum of line item amounts = subtotal |
| FR-4.2 | System shall validate: subtotal + tax = total amount |
| FR-4.3 | System shall validate: required fields are present (invoice number, date, total) |
| FR-4.4 | System shall validate: date formats are parseable |
| FR-4.5 | System shall validate: numeric fields contain valid numbers |
| FR-4.6 | System shall return a list of validation errors with field-level detail |

### FR-5: Auto-Correction Feature

| ID | Requirement |
|----|-------------|
| FR-5.1 | If validation fails, system shall attempt auto-correction (max 2 retry attempts) |
| FR-5.2 | System shall use LLM re-analysis with error context for correction |
| FR-5.3 | System shall apply rule-based corrections for arithmetic errors |
| FR-5.4 | System shall log corrections applied for audit/transparency |
| FR-5.5 | If auto-correction fails after max retries, return best-effort result with error flags |

### FR-6: JSON Formatting Feature

| ID | Requirement |
|----|-------------|
| FR-6.1 | System shall output extracted data in a standardized JSON schema |
| FR-6.2 | JSON output shall include metadata (confidence score, processing time, corrections applied) |
| FR-6.3 | JSON output shall include validation status (passed/failed with details) |

### FR-7: Orchestrator Workflow

| ID | Requirement |
|----|-------------|
| FR-7.1 | System shall orchestrate the pipeline: Upload → OCR → Extraction → Validation → (Correction if needed) → JSON Output |
| FR-7.2 | System shall handle conditional branching (skip correction if validation passes) |
| FR-7.3 | System shall track workflow state at each stage |
| FR-7.4 | System shall provide status visibility to the user during processing |

### FR-8: User Interface

| ID | Requirement |
|----|-------------|
| FR-8.1 | System shall provide a web UI to upload documents |
| FR-8.2 | System shall display processing status/progress |
| FR-8.3 | System shall display the final JSON output in a readable format |
| FR-8.4 | System shall allow downloading the JSON result |

---

## 6. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Performance | Single invoice processing ≤ 30 seconds end-to-end |
| NFR-2 | Accuracy | ≥ 85% field-level extraction accuracy on varied templates |
| NFR-3 | Availability | System available during demo; no HA requirement for v1.0 |
| NFR-4 | Scalability | Handle 1 concurrent user for v1.0 |
| NFR-5 | Security | No sensitive data stored persistently; files processed in-memory or temp storage |
| NFR-6 | Usability | Intuitive upload → result flow, no training needed |
| NFR-7 | Maintainability | Clean architecture, modular agents, documented code |
| NFR-8 | Observability | Log each pipeline stage with timing and status |

---

## 7. JSON Output Schema (Target)

```json
{
  "metadata": {
    "processing_time_ms": 12500,
    "confidence_score": 0.92,
    "validation_status": "passed",
    "corrections_applied": [],
    "source_file": "invoice_001.pdf"
  },
  "invoice": {
    "invoice_number": "INV-2026-0042",
    "invoice_date": "2026-05-15",
    "due_date": "2026-06-15",
    "currency": "USD",
    "vendor": {
      "name": "Acme Corp",
      "address": "123 Business St, City, State 12345"
    },
    "buyer": {
      "name": "Client Inc",
      "address": "456 Client Ave, Town, State 67890"
    },
    "line_items": [
      {
        "description": "Consulting Services",
        "quantity": 10,
        "unit_price": 150.00,
        "amount": 1500.00
      },
      {
        "description": "Software License",
        "quantity": 1,
        "unit_price": 500.00,
        "amount": 500.00
      }
    ],
    "subtotal": 2000.00,
    "tax": {
      "percentage": 10,
      "amount": 200.00
    },
    "total_amount": 2200.00
  }
}
```

---

## 8. Workflow Diagram

```
┌──────────┐     ┌──────────┐     ┌─────────────┐     ┌────────────┐
│  Upload  │────▶│   OCR    │────▶│ Extraction  │────▶│ Validation │
│ (PDF/IMG)│     │  Agent   │     │   Agent     │     │   Agent    │
└──────────┘     └──────────┘     └─────────────┘     └─────┬──────┘
                                                             │
                                                    ┌────────┴────────┐
                                                    │                 │
                                                 PASS              FAIL
                                                    │                 │
                                                    ▼                 ▼
                                            ┌────────────┐   ┌──────────────┐
                                            │   JSON     │   │    Auto-     │
                                            │ Formatter  │   │  Correction  │
                                            └────────────┘   └──────┬───────┘
                                                    ▲                │
                                                    │                │
                                                    └────────────────┘
                                                      (re-validate)
```

---

## 9. Constraints

| # | Constraint |
|---|-----------|
| C-1 | 2-week delivery timeline |
| C-2 | Must use AI/LLM-based approach (not rule-only template matching) |
| C-3 | Must demonstrate with real invoices (not mocked data) |
| C-4 | Must use orchestration framework (LangGraph recommended) |
| C-5 | Single developer delivery |

---

## 10. Assumptions

| # | Assumption |
|---|-----------|
| A-1 | Invoices are in English |
| A-2 | Invoices follow standard business invoice structure (header, line items, totals) |
| A-3 | LLM API (OpenAI/Azure) access is available |
| A-4 | Internet connectivity available for LLM API calls |
| A-5 | Test invoices (varied templates) will be sourced or created for demo |

---

## 11. Success Criteria

| # | Criteria |
|---|---------|
| SC-1 | End-to-end demo: upload invoice → receive correct JSON |
| SC-2 | Works on at least 3 different invoice templates |
| SC-3 | Validation catches arithmetic inconsistencies |
| SC-4 | Auto-correction fixes at least 1 type of error in demo |
| SC-5 | Clean, documented codebase with clear architecture |
| SC-6 | Architecture diagram covers all components |

---

## 12. Risks

| # | Risk | Impact | Mitigation |
|---|------|--------|-----------|
| R-1 | LLM extraction accuracy varies across templates | Medium | Few-shot prompting, structured output mode |
| R-2 | OCR quality on poor scans | Medium | Use high-quality OCR engine, fallback to multimodal LLM |
| R-3 | 2-week timeline too tight | High | Prioritize core pipeline, defer UI polish |
| R-4 | LLM API rate limits / costs | Low | Cache results, limit retries to 2 |

---

## 13. Glossary (Ubiquitous Language)

| Term | Definition |
|------|-----------|
| **Document** | Input file (PDF or image) containing an invoice |
| **Raw Text** | Unstructured text output from OCR processing |
| **Extracted Data** | Structured key-value pairs and line items identified from raw text |
| **Validation Result** | Pass/fail status with field-level error details |
| **Correction** | Modified extracted data after auto-correction attempt |
| **Invoice JSON** | Final structured JSON output conforming to the defined schema |
| **Agent** | An independent processing unit responsible for one pipeline stage |
| **Orchestrator** | Workflow controller that sequences agents and handles conditional logic |
| **Confidence Score** | Numeric indicator (0-1) of extraction reliability |

---

## 14. Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Reviewer | | | |
| Approver | | | |
