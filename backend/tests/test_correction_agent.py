import pytest
from unittest.mock import patch, MagicMock

from app.models.invoice import (
    ExtractedInvoice,
    ValidationResult,
    ValidationError,
    OCRResult,
    OCRMethod,
    LineItem,
    TaxInfo,
    CorrectionLog,
    CorrectionEntry,
)
from app.agents.correction_agent import run_correction


def _make_invoice() -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_number="INV-001",
        invoice_date="2024-01-15",
        due_date="2024-02-15",
        currency="USD",
        line_items=[
            LineItem(description="Item A", quantity=2, unit_price=50.0, amount=100.0),
            LineItem(description="Item B", quantity=1, unit_price=75.0, amount=75.0),
        ],
        subtotal=200.0,  # Wrong: should be 175.0
        tax=TaxInfo(percentage=10.0, amount=17.50),
        total_amount=217.50,
    )


def _make_ocr_result() -> OCRResult:
    return OCRResult(
        raw_text="Invoice INV-001\nSubtotal: 175.00\nTax: 17.50\nTotal: 192.50",
        confidence=0.95,
        method_used=OCRMethod.PYMUPDF,
    )


def test_rule_based_subtotal_fix():
    invoice = _make_invoice()
    validation_result = ValidationResult(
        is_valid=False,
        errors=[ValidationError(
            field="subtotal",
            rule="LINE_ITEMS_SUM",
            message="Sum of line items does not equal subtotal",
            expected="175.0",
            actual="200.0",
        )],
    )

    corrected, log = run_correction(invoice, validation_result, _make_ocr_result())

    assert corrected.subtotal == 175.0
    assert log.success is True
    assert any(c.method == "rule_based" and c.field == "subtotal" for c in log.corrections)


def test_rule_based_total_fix():
    invoice = _make_invoice()
    invoice.subtotal = 175.0
    invoice.total_amount = 999.0  # Wrong

    validation_result = ValidationResult(
        is_valid=False,
        errors=[ValidationError(
            field="total_amount",
            rule="TOTAL_CALCULATION",
            message="subtotal + tax does not equal total_amount",
            expected="192.5",
            actual="999.0",
        )],
    )

    corrected, log = run_correction(invoice, validation_result, _make_ocr_result())

    assert corrected.total_amount == 192.5
    assert any(c.method == "rule_based" and c.field == "total_amount" for c in log.corrections)


@patch("app.agents.correction_agent.ChatGoogleGenerativeAI")
def test_llm_correction_for_non_fixable_errors(mock_llm_class):
    invoice = _make_invoice()
    invoice.subtotal = 175.0
    invoice.total_amount = 192.5
    invoice.invoice_number = None

    validation_result = ValidationResult(
        is_valid=False,
        errors=[ValidationError(
            field="invoice_number",
            rule="REQUIRED_FIELDS",
            message="invoice_number is required",
        )],
    )

    corrected_invoice = invoice.model_copy(deep=True)
    corrected_invoice.invoice_number = "INV-001"

    mock_chain = MagicMock()
    mock_chain.invoke.return_value = corrected_invoice
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_chain
    mock_llm_class.return_value = mock_llm

    corrected, log = run_correction(invoice, validation_result, _make_ocr_result())

    assert corrected.invoice_number == "INV-001"
    assert any(c.method == "llm_reanalysis" for c in log.corrections)
