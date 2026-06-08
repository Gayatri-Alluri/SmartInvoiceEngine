import pytest
from app.models.invoice import (
    ExtractedInvoice,
    LineItem,
    TaxInfo,
    VendorInfo,
    BuyerInfo,
    ValidationResult,
)
from app.agents.validation_agent import run_validation


def _make_valid_invoice() -> ExtractedInvoice:
    return ExtractedInvoice(
        invoice_number="INV-001",
        invoice_date="2024-01-15",
        due_date="2024-02-15",
        currency="USD",
        vendor=VendorInfo(name="Acme Corp", address="123 Main St"),
        buyer=BuyerInfo(name="Client Inc", address="456 Oak Ave"),
        line_items=[
            LineItem(description="Widget A", quantity=2, unit_price=50.0, amount=100.0),
            LineItem(description="Widget B", quantity=1, unit_price=75.0, amount=75.0),
        ],
        subtotal=175.0,
        tax=TaxInfo(percentage=10.0, amount=17.50),
        total_amount=192.50,
    )


def test_valid_invoice():
    invoice = _make_valid_invoice()
    result = run_validation(invoice)
    assert result.is_valid is True
    assert result.errors == []


def test_line_items_sum_mismatch():
    invoice = _make_valid_invoice()
    invoice.subtotal = 200.0  # Wrong: should be 175.0
    invoice.total_amount = 217.50  # Adjust so TOTAL_CALCULATION passes

    result = run_validation(invoice)
    assert result.is_valid is False
    error_rules = [e.rule for e in result.errors]
    assert "LINE_ITEMS_SUM" in error_rules


def test_total_calculation_mismatch():
    invoice = _make_valid_invoice()
    invoice.total_amount = 999.99  # Wrong: should be 192.50

    result = run_validation(invoice)
    assert result.is_valid is False
    error_rules = [e.rule for e in result.errors]
    assert "TOTAL_CALCULATION" in error_rules


def test_missing_required_field_invoice_number():
    invoice = _make_valid_invoice()
    invoice.invoice_number = None

    result = run_validation(invoice)
    assert result.is_valid is False
    error_rules = [e.rule for e in result.errors]
    assert "REQUIRED_FIELDS" in error_rules


def test_missing_required_field_invoice_date():
    invoice = _make_valid_invoice()
    invoice.invoice_date = None

    result = run_validation(invoice)
    assert result.is_valid is False
    assert any(e.field == "invoice_date" for e in result.errors)


def test_missing_required_field_total_amount():
    invoice = _make_valid_invoice()
    invoice.total_amount = None

    result = run_validation(invoice)
    assert result.is_valid is False
    assert any(e.field == "total_amount" for e in result.errors)


def test_invalid_date_format():
    invoice = _make_valid_invoice()
    invoice.invoice_date = "not-a-date"

    result = run_validation(invoice)
    assert result.is_valid is False
    error_rules = [e.rule for e in result.errors]
    assert "DATE_FORMAT" in error_rules


def test_negative_amount():
    invoice = _make_valid_invoice()
    invoice.line_items[0].amount = -50.0
    invoice.subtotal = 25.0
    invoice.total_amount = 42.50

    result = run_validation(invoice)
    assert result.is_valid is False
    error_rules = [e.rule for e in result.errors]
    assert "NUMERIC_VALIDITY" in error_rules


def test_valid_alternative_date_formats():
    invoice = _make_valid_invoice()
    invoice.invoice_date = "15/01/2024"
    invoice.due_date = "January 15, 2024"

    result = run_validation(invoice)
    date_errors = [e for e in result.errors if e.rule == "DATE_FORMAT"]
    assert len(date_errors) == 0
