import asyncio
import time
import uuid
from typing import Any

from fastapi import APIRouter, UploadFile, HTTPException
import structlog

from app.api.schemas import ProcessResponse, StatusResponse, ResultResponse
from app.models.invoice import DocumentInput
from app.agents.ocr_agent import run_ocr
from app.agents.extraction_agent import run_extraction
from app.agents.validation_agent import run_validation
from app.agents.correction_agent import run_correction
from app.agents.formatter_agent import run_formatter
from app.config import settings

logger = structlog.get_logger()
router = APIRouter(prefix="/api")

job_store: dict[str, dict[str, Any]] = {}

ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg"}
STAGE_ORDER = ["ocr", "extraction", "validation", "correction", "formatting", "complete"]


@router.post("/process", response_model=ProcessResponse, status_code=202)
async def process(file: UploadFile) -> ProcessResponse:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type. Accepted: pdf, png, jpeg")

    file_bytes = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File size exceeds {settings.max_file_size_mb} MB limit")

    job_id = str(uuid.uuid4())
    job_store[job_id] = {
        "status": "processing",
        "current_stage": "queued",
        "stages_completed": [],
        "start_time": time.time(),
        "result": None,
        "error": None,
    }

    document = DocumentInput(
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        mime_type=file.content_type,
    )

    asyncio.create_task(_run_pipeline(job_id, document))

    return ProcessResponse(
        job_id=job_id,
        status="processing",
        message="Invoice processing started",
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str) -> StatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    elapsed_ms = int((time.time() - job["start_time"]) * 1000)

    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        current_stage=job["current_stage"],
        stages_completed=job["stages_completed"],
        elapsed_ms=elapsed_ms,
    )


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str) -> ResultResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return ResultResponse(
        job_id=job_id,
        status=job["status"],
        result=job["result"],
        error=job["error"],
    )


async def _run_pipeline(job_id: str, document: DocumentInput) -> None:
    log = logger.bind(job_id=job_id)
    job = job_store[job_id]
    try:
        log.info("pipeline_started")
        start_time = time.time()

        job["current_stage"] = "ocr"
        ocr_result = await asyncio.to_thread(run_ocr, document)
        job["stages_completed"].append("ocr")

        job["current_stage"] = "extraction"
        extracted = await asyncio.to_thread(run_extraction, ocr_result)
        job["stages_completed"].append("extraction")

        job["current_stage"] = "validation"
        validation_result = await asyncio.to_thread(run_validation, extracted)
        job["stages_completed"].append("validation")

        correction_attempts = 0
        all_corrections = []
        while not validation_result.is_valid and correction_attempts < settings.max_correction_retries:
            job["current_stage"] = "correction"
            extracted, correction_log = await asyncio.to_thread(
                run_correction, extracted, validation_result, ocr_result
            )
            all_corrections.extend(correction_log.corrections)
            correction_attempts += 1
            validation_result = await asyncio.to_thread(run_validation, extracted)

        job["stages_completed"].append("correction")

        job["current_stage"] = "formatting"
        elapsed_ms = int((time.time() - start_time) * 1000)
        metadata = {
            "processing_time_ms": elapsed_ms,
            "ocr_confidence": ocr_result.confidence,
            "corrections_applied": all_corrections,
            "source_file": document.filename,
            "ocr_method": ocr_result.method_used,
        }
        result = await asyncio.to_thread(run_formatter, extracted, validation_result, metadata)

        job["stages_completed"].append("formatting")
        job["status"] = "completed"
        job["current_stage"] = "complete"
        job["stages_completed"].append("complete")
        job["result"] = result
        log.info("pipeline_completed")
    except Exception as e:
        log.error("pipeline_failed", error=str(e))
        job["status"] = "failed"
        job["current_stage"] = "error"
        job["error"] = str(e)
