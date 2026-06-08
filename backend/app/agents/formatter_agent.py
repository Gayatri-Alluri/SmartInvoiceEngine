from app.models.invoice import (
    ExtractedInvoice,
    ValidationResult,
    CorrectionEntry,
    ProcessingMetadata,
    InvoiceJSON,
    OCRMethod,
)


def run_formatter(
    invoice: ExtractedInvoice,
    validation_result: ValidationResult,
    metadata: dict,
) -> InvoiceJSON:
    ocr_confidence = metadata.get("ocr_confidence", 0.0)
    corrections = metadata.get("corrections_applied", [])
    was_corrected = len(corrections) > 0

    if validation_result.is_valid and not was_corrected:
        validation_status = "passed"
    elif validation_result.is_valid and was_corrected:
        validation_status = "corrected"
    else:
        validation_status = "failed"

    confidence_score = _calculate_confidence(ocr_confidence, validation_result, was_corrected)

    processing_metadata = ProcessingMetadata(
        processing_time_ms=metadata.get("processing_time_ms", 0),
        confidence_score=confidence_score,
        validation_status=validation_status,
        corrections_applied=corrections,
        source_file=metadata.get("source_file", "unknown"),
        ocr_method=metadata.get("ocr_method", OCRMethod.PYMUPDF),
    )

    return InvoiceJSON(metadata=processing_metadata, invoice=invoice)


def _calculate_confidence(
    ocr_confidence: float,
    validation_result: ValidationResult,
    was_corrected: bool,
) -> float:
    base = ocr_confidence

    if validation_result.is_valid and not was_corrected:
        score = base * 1.0
    elif validation_result.is_valid and was_corrected:
        score = base * 0.85
    else:
        score = base * 0.5

    return round(min(max(score, 0.0), 1.0), 3)
