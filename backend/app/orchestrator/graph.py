import time
import structlog
from langgraph.graph import StateGraph, END

from app.orchestrator.state import WorkflowState
from app.models.invoice import DocumentInput, InvoiceJSON, CorrectionEntry
from app.agents.ocr_agent import run_ocr
from app.agents.extraction_agent import run_extraction
from app.agents.validation_agent import run_validation
from app.agents.correction_agent import run_correction
from app.agents.formatter_agent import run_formatter
from app.config import settings

logger = structlog.get_logger()


def ocr_node(state: WorkflowState) -> dict:
    logger.info("node_ocr_started")
    state["current_stage"] = "ocr"
    result = run_ocr(state["document"])
    return {"ocr_result": result, "current_stage": "ocr"}


def extraction_node(state: WorkflowState) -> dict:
    logger.info("node_extraction_started")
    result = run_extraction(state["ocr_result"])
    return {"extracted_invoice": result, "current_stage": "extraction"}


def validation_node(state: WorkflowState) -> dict:
    logger.info("node_validation_started")
    result = run_validation(state["extracted_invoice"])
    return {"validation_result": result, "current_stage": "validation"}


def correction_node(state: WorkflowState) -> dict:
    logger.info("node_correction_started", attempt=state["correction_attempts"] + 1)
    corrected, log = run_correction(
        state["extracted_invoice"],
        state["validation_result"],
        state["ocr_result"],
    )
    correction_log = state.get("correction_log", [])
    correction_log.append(log)
    return {
        "extracted_invoice": corrected,
        "correction_log": correction_log,
        "correction_attempts": state["correction_attempts"] + 1,
        "current_stage": "correction",
    }


def formatter_node(state: WorkflowState) -> dict:
    logger.info("node_formatter_started")
    elapsed_ms = int((time.time() - state["start_time"]) * 1000)

    all_corrections: list[CorrectionEntry] = []
    for log in state.get("correction_log", []):
        all_corrections.extend(log.corrections)

    metadata = {
        "processing_time_ms": elapsed_ms,
        "ocr_confidence": state["ocr_result"].confidence,
        "corrections_applied": all_corrections,
        "source_file": state["document"].filename,
        "ocr_method": state["ocr_result"].method_used,
    }

    result = run_formatter(state["extracted_invoice"], state["validation_result"], metadata)
    return {"final_output": result, "current_stage": "complete"}


def should_correct(state: WorkflowState) -> str:
    if state["validation_result"].is_valid:
        return "formatter"
    if state["correction_attempts"] >= settings.max_correction_retries:
        return "formatter"
    return "correction"


graph = StateGraph(WorkflowState)

graph.add_node("ocr", ocr_node)
graph.add_node("extraction", extraction_node)
graph.add_node("validation", validation_node)
graph.add_node("correction", correction_node)
graph.add_node("formatter", formatter_node)

graph.set_entry_point("ocr")
graph.add_edge("ocr", "extraction")
graph.add_edge("extraction", "validation")
graph.add_conditional_edges("validation", should_correct, {
    "formatter": "formatter",
    "correction": "correction",
})
graph.add_edge("correction", "validation")
graph.add_edge("formatter", END)

compiled_graph = graph.compile()


def process_invoice(document: DocumentInput) -> InvoiceJSON:
    initial_state: WorkflowState = {
        "document": document,
        "ocr_result": None,
        "extracted_invoice": None,
        "validation_result": None,
        "correction_log": [],
        "correction_attempts": 0,
        "final_output": None,
        "current_stage": "starting",
        "error": None,
        "start_time": time.time(),
    }

    final_state = compiled_graph.invoke(initial_state)
    return final_state["final_output"]
