from typing import TypedDict, Optional

from app.models.invoice import (
    DocumentInput,
    OCRResult,
    ExtractedInvoice,
    ValidationResult,
    CorrectionLog,
    InvoiceJSON,
)


class WorkflowState(TypedDict):
    document: DocumentInput
    ocr_result: Optional[OCRResult]
    extracted_invoice: Optional[ExtractedInvoice]
    validation_result: Optional[ValidationResult]
    correction_log: list[CorrectionLog]
    correction_attempts: int
    final_output: Optional[InvoiceJSON]
    current_stage: str
    error: Optional[str]
    start_time: float
