# FUTURE_VISION.md — Full Product Vision

> This document proves intentional scoping. It shows the full product potential and explicitly marks what ships now (MVP), what was deliberately deferred, and what the product becomes long-term.

---

## Vision Statement

Smart Invoice Engine evolves from a single-user extraction tool into an enterprise-grade, multi-tenant document intelligence platform that handles any structured document type (invoices, receipts, purchase orders, contracts) across languages, with learning capabilities that improve accuracy over time.

---

## Feature Horizon Map

### Now — MVP (2-Week Delivery)

| Feature | Scope |
|---------|-------|
| OCR Agent | Tesseract + PyMuPDF + Gemini 1.5 Pro vision fallback |
| Extraction Agent | Gemini 1.5 Pro structured output, 11 invoice fields |
| Validation Agent | 5 rule-based checks |
| Correction Agent | LLM re-prompt with error context, max 2 retries |
| JSON Formatter | Standardized schema with metadata |
| LangGraph Orchestrator | Linear pipeline with conditional correction loop |
| REST API | 3 endpoints (process, status, result) |
| Web UI | Upload, status, JSON viewer, download |

### Next — v1.1 (Month 2-3)

| Feature | Value |
|---------|-------|
| Batch processing | Upload ZIP/folder of invoices, process in parallel |
| Processing history | Persist results in PostgreSQL, view past extractions |
| Confidence-based routing | Low confidence → human review queue instead of auto-correct |
| Multi-page invoice support | Stitch pages before extraction |
| Template learning | Store successful extractions as few-shot examples per vendor |
| Export formats | CSV, Excel, XML in addition to JSON |
| Webhook notifications | Notify external systems on completion |

### Later — v2.0 (Month 4-6)

| Feature | Value |
|---------|-------|
| Multi-language support | OCR + extraction in 10+ languages |
| Multi-document types | Receipts, purchase orders, delivery notes, credit notes |
| User authentication | OAuth2 / SSO, role-based access |
| Multi-tenancy | Isolated workspaces per organization |
| Custom field configuration | Users define which fields to extract per document type |
| Feedback loop | User corrections feed back to improve prompts (RLHF-lite) |
| Analytics dashboard | Extraction accuracy trends, processing volumes, error patterns |
| ERP integrations | Push extracted data to SAP, QuickBooks, Xero via connectors |

### Horizon — v3.0+ (Month 7+)

| Feature | Value |
|---------|-------|
| Fine-tuned extraction model | Distill Gemini extractions into a smaller, faster, cheaper model |
| On-premise deployment | Air-gapped deployment with local LLM (Llama/Mistral) |
| Real-time processing | Watch folder / email inbox integration for auto-processing |
| Compliance & audit | Full audit trail, GDPR data handling, retention policies |
| Marketplace | Pluggable extractors for industry-specific document types |
| Mobile capture | Camera-based invoice capture from mobile app |

---

## Architecture Evolution

```
MVP (Now)                    v2.0                         v3.0
─────────────               ──────                       ──────
Monolith                    Modular Monolith             Microservices
(FastAPI + LangGraph)       (Domain modules)             (Event-driven)

Single LLM (Gemini 1.5 Pro)  Multi-LLM routing            Fine-tuned + Local LLM
                            (GPT-4o / Claude / Gemini)

Local Docker Compose        Cloud deployment (K8s)       Multi-region HA

No persistence              PostgreSQL + Redis           PostgreSQL + Vector DB + S3

Single user                 Multi-user + auth            Multi-tenant enterprise
```

---

## Technical Debt Accepted in MVP (Intentional)

| Debt | Why Accepted | When to Address |
|------|-------------|-----------------|
| No database — results ephemeral | Simplicity, 2-week constraint | v1.1 |
| No auth — open access | Single-user demo | v2.0 |
| No retry queue — sync processing | Low volume, single user | v1.1 |
| Hardcoded JSON schema | Only invoices for now | v2.0 (configurable schemas) |
| No rate limiting on API | Single user, no abuse risk | v2.0 |
| Prompts in code, not externalized | Fast iteration during MVP | v1.1 (prompt registry) |
| No automated tests for prompts | Prompt evaluation framework needed | v1.1 |

---

## Competitive Differentiation (Long-term)

| vs. Competitor | Our Advantage |
|---------------|---------------|
| Manual data entry | 100x faster, no human error |
| Template-based tools (ABBYY, Rossum) | No template configuration needed; works on unseen layouts |
| Pure OCR solutions | OCR + LLM understanding + validation + self-correction |
| Generic LLM APIs | Orchestrated pipeline with validation guarantees, not raw LLM output |

---

## Key Metrics (Future State)

| Metric | MVP Target | v2.0 Target |
|--------|-----------|-------------|
| Field extraction accuracy | ≥ 85% | ≥ 95% |
| Processing time (single doc) | ≤ 30s | ≤ 10s |
| Supported languages | 1 (English) | 10+ |
| Supported document types | 1 (Invoice) | 5+ |
| Concurrent users | 1 | 100+ |
| Uptime | Demo only | 99.9% |
