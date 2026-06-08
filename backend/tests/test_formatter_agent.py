import pytest
from app.models.invoice import (
    ExtractedInvoice,
    ValidationResult,
    LineItem,
    TaxInfo,
    VendorInfo,
    OCRMethod,
    CorrectionEntry,
)
from app.agents.formatter_agent import run_formatter


def _make_valid_invoice() -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_number="INV-001",
        invoice_date="2024-01-15",
        currency="USD",
        vendor=VendorInfo(name="Acme Corp"),
        line_items=[LineItem(description="Widget", quantity=1, unit_price=100.0, amount=100.0)],
        subtotal=100.0,
        tax=TaxInfo(percentage=10.0, amount=10.0),
        total_amount=110.0,
    )


def test_formatter_passed():
    invoice = _make_valid_invoice()
    validation = ValidationResult(is_valid=True, errors=[])
    metadata = {
        "processing_time_ms": 1500,
        "ocr_confidence": 0.95,
        "corrections_applied": [],
        "source_file": "test.pdf",
        "ocr_method": OCRMethod.PYMUPDF,
    }

    result = run_formatter(invoice, validation, metadata)

    assert result.metadata.validation_status == "passed"
    assert result.metadata.confidence_score == 0.95
    assert result.metadata.processing_time_ms == 1500
    assert result.invoice.invoice_number == "INV-001"


def test_formatter_corrected():
    invoice = _make_valid_invoice()
    validation = ValidationResult(is_valid=True, errors=[])
    corrections = [CorrectionEntry(field="subtotal", old_value="200", new_value="100", method="rule_based")]
    metadata = {
        "processing_time_ms": 3000,
        "ocr_confidence": 0.90,
        "corrections_applied": corrections,
        "source_file": "invoice.pdf",
        "ocr_method": OCRMethod.TESSERACT,
    }

    result = run_formatter(invoice, validation, metadata)

    assert result.metadata.validation_status == "corrected"
    assert result.metadata.confidence_score < 0.90


def test_formatter_failed():
    invoice = _make_valid_invoice()
    validation = ValidationResult(is_valid=False, errors=[])
    metadata = {
        "processing_time_ms": 5000,
        "ocr_confidence": 0.70,
        "corrections_applied": [],
        "source_file": "bad.png",
        "ocr_method": OCRMethod.GEMINI_VISION,
    }

    result = run_formatter(invoice, validation, metadata)

    assert result.metadata.validation_status == "failed"
    assert result.metadata.confidence_score == 0.35
