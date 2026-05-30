# DEPENDENCIES.md — Build Order & Dependency Graph

> **Rule:** Never build a component before its dependencies exist and pass their gate.  
> **Derived from:** SPEC.md + PLAN.md

---

## 1. Dependency Graph (Visual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 0: SCAFFOLDING                               │
│                                                                             │
│  requirements.txt ──┐                                                       │
│  Dockerfile(s) ─────┼──► docker-compose.yml ──► Project runs locally        │
│  .env.example ──────┘                                                       │
│  config.py ─────────────────────────────────────────────────────────────┐   │
└─────────────────────────────────────────────────────────────────────────┼───┘
                                                                          │
┌─────────────────────────────────────────────────────────────────────────┼───┐
│                          PHASE 1: CORE AGENTS                           │   │
│                                                                         ▼   │
│  models/invoice.py ──────┬──► ocr_agent.py ──► extraction_agent.py      │   │
│  (all Pydantic schemas)  │                          │                   │   │
│                          │                          ▼                   │   │
│  prompts/extraction.py ──┘              validation_agent.py             │   │
└─────────────────────────────────────────────────────┬───────────────────────┘
                                                      │
┌─────────────────────────────────────────────────────┼───────────────────────┐
│                     PHASE 2: CORRECTION + ORCHESTRATOR                   │   │
│                                                      ▼                   │   │
│  prompts/correction.py ──► correction_agent.py                           │   │
│                                    │                                     │   │
│  formatter_agent.py ◄──────────────┘                                     │   │
│         │                                                                │   │
│         ▼                                                                │   │
│  orchestrator/state.py ──► orchestrator/graph.py                         │   │
│  (WorkflowState)              (wires all agents)                         │   │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
┌──────────────────────────────────┼───────────────────────────────────────────┐
│                     PHASE 3: API + FRONTEND                              │   │
│                                   ▼                                      │   │
│  api/schemas.py ──► api/routes.py                                        │   │
│                         │                                                │   │
│                         ▼                                                │   │
│  services/api.ts ──► UploadForm.tsx ──► PipelineStatus.tsx               │   │
│  types/invoice.ts      │                     │                           │   │
│                        ▼                     ▼                           │   │
│                   ResultViewer.tsx ──► DownloadButton.tsx                  │   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Per-File Dependencies

### Phase 0: Scaffolding

| File | Depends On | Blocks |
|------|-----------|--------|
| `requirements.txt` | Nothing | All Python code |
| `backend/Dockerfile` | requirements.txt | docker-compose.yml |
| `frontend/package.json` | Nothing | All frontend code |
| `frontend/Dockerfile` | package.json | docker-compose.yml |
| `docker-compose.yml` | Both Dockerfiles | Local development |
| `backend/app/config.py` | .env.example | All agents (reads settings) |
| `.env.example` | Nothing | config.py |

### Phase 1: Core Agents

| File | Depends On | Blocks |
|------|-----------|--------|
| `models/invoice.py` | Pydantic (requirements.txt) | Every agent, API schemas |
| `prompts/extraction.py` | Nothing (pure strings) | extraction_agent.py |
| `agents/ocr_agent.py` | models/invoice.py, config.py, pytesseract, pymupdf | extraction_agent.py, orchestrator |
| `agents/extraction_agent.py` | models/invoice.py, prompts/extraction.py, config.py, langchain-google-genai | validation_agent.py, orchestrator |
| `agents/validation_agent.py` | models/invoice.py | correction_agent.py, orchestrator |
| `tests/test_ocr_agent.py` | ocr_agent.py, test invoice files | Gate 1 |
| `tests/test_extraction_agent.py` | extraction_agent.py, GOOGLE_API_KEY | Gate 1 |
| `tests/test_validation_agent.py` | validation_agent.py | Gate 1 |

### Phase 2: Correction + Orchestrator

| File | Depends On | Blocks |
|------|-----------|--------|
| `prompts/correction.py` | Nothing (pure strings) | correction_agent.py |
| `agents/correction_agent.py` | models/invoice.py, prompts/correction.py, validation_agent.py, config.py | orchestrator |
| `agents/formatter_agent.py` | models/invoice.py | orchestrator |
| `orchestrator/state.py` | models/invoice.py | orchestrator/graph.py |
| `orchestrator/graph.py` | state.py, ALL agents, langgraph | api/routes.py |
| `tests/test_correction_agent.py` | correction_agent.py | Gate 2 |

### Phase 3: API + Frontend

| File | Depends On | Blocks |
|------|-----------|--------|
| `api/schemas.py` | models/invoice.py | api/routes.py |
| `api/routes.py` | api/schemas.py, orchestrator/graph.py | Frontend |
| `frontend/src/types/invoice.ts` | Nothing (mirrors Pydantic models) | All frontend components |
| `frontend/src/services/api.ts` | types/invoice.ts, axios | Components |
| `frontend/src/components/UploadForm.tsx` | api.ts | App.tsx |
| `frontend/src/components/PipelineStatus.tsx` | api.ts, types | App.tsx |
| `frontend/src/components/ResultViewer.tsx` | types, react-syntax-highlighter | App.tsx |
| `frontend/src/components/DownloadButton.tsx` | types | App.tsx |
| `frontend/src/hooks/useProcessInvoice.ts` | api.ts, types | Components |
| `frontend/src/App.tsx` | All components, hooks | main.tsx |

---

## 3. External Dependencies

| Dependency | Required By | Must Be Available |
|-----------|-------------|-------------------|
| **Tesseract binary** | ocr_agent.py | Day 3 (installed in Docker image) |
| **GOOGLE_API_KEY** | extraction_agent.py, correction_agent.py, ocr_agent.py (vision) | Day 4 (first LLM call) |
| **Test invoice files** | All tests, integration testing | Day 3 (place in test-invoices/) |
| **Docker + Docker Compose** | docker-compose.yml | Day 2 (scaffolding) |
| **Node.js 18+** | Frontend build | Day 2 (scaffolding) |
| **Python 3.11+** | Backend | Day 2 (scaffolding) |

---

## 4. Critical Path

The longest sequential chain that determines the minimum possible timeline:

```
models/invoice.py → ocr_agent.py → extraction_agent.py → validation_agent.py → correction_agent.py → orchestrator/graph.py → api/routes.py → Frontend components
      │                  │                 │                    │                     │                      │                    │                │
    Day 3             Day 3             Day 4               Day 5                 Day 6                  Day 7               Day 8            Day 9
```

**Critical path length: 7 days** (Day 3 → Day 9)  
**Total available: 8 days** (Day 3 → Day 10)  
**Buffer: 1 day** ← This is why Day 10 is reserved for testing/polish only.

---

## 5. Parallelizable Work

These can be done in parallel (no dependency between them):

| Group | Items | When |
|-------|-------|------|
| A | prompts/extraction.py + prompts/correction.py | Day 3-4 (write ahead) |
| B | models/invoice.py + frontend/types/invoice.ts | Day 3 (same schemas, different languages) |
| C | formatter_agent.py + correction_agent.py | Day 6 (both depend on validation, not each other) |
| D | api/schemas.py + frontend scaffold | Day 8 (backend API schema + frontend skeleton) |

---

## 6. Dependency Violations to Watch For

| Anti-Pattern | Why It's Dangerous |
|--------------|--------------------|
| Building API routes before orchestrator works | API will have nothing to call; you'll mock and then rewrite |
| Building frontend before API is testable | Frontend will target wrong response shapes |
| Writing orchestrator before all agents pass tests | Debugging agent bugs inside the graph is 5x harder |
| Skipping models/invoice.py | Every agent will define its own incompatible schemas |
| Using LLM calls in tests without mocking | Tests become slow, flaky, and expensive |
