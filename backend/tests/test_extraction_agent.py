import pytest
from unittest.mock import patch, MagicMock
from app.models.invoice import OCRResult, OCRMethod, ExtractedInvoice
from app.agents.extraction_agent import run_extraction


def _make_ocr_result() -> OCRResult:
    return OCRResult(
        raw_text="""INVOICE
Invoice Number: INV-2024-001
Date: 2024-03-15
Due Date: 2024-04-15

From: Acme Corp, 123 Main St
To: Client Inc, 456 Oak Ave

Description          Qty    Price    Amount
Widget A              2     50.00    100.00
Widget B              1     75.00     75.00

Subtotal: 175.00
Tax (10%): 17.50
Total: 192.50
Currency: USD""",
        confidence=0.95,
        method_used=OCRMethod.PYMUPDF,
    )


@patch("app.agents.extraction_agent.ChatGoogleGenerativeAI")
def test_extract_invoice(mock_llm_class):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = ExtractedInvoice(
        invoice_number="INV-2024-001",
        invoice_date="2024-03-15",
        due_date="2024-04-15",
        currency="USD",
        total_amount=192.50,
    )
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_chain
    mock_llm_class.return_value = mock_llm

    result = run_extraction(_make_ocr_result())

    assert result.invoice_number == "INV-2024-001"
    assert result.total_amount == 192.50
    mock_chain.invoke.assert_called_once()


@patch("app.agents.extraction_agent.ChatGoogleGenerativeAI")
def test_extract_invoice_retries_on_failure(mock_llm_class):
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = [
        Exception("API error"),
        ExtractedInvoice(invoice_number="INV-001", total_amount=100.0),
    ]
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_chain
    mock_llm_class.return_value = mock_llm

    result = run_extraction(_make_ocr_result())

    assert result.invoice_number == "INV-001"
    assert mock_chain.invoke.call_count == 2


@patch("app.agents.extraction_agent.ChatGoogleGenerativeAI")
def test_extract_invoice_returns_empty_on_all_failures(mock_llm_class):
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = Exception("API error")
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_chain
    mock_llm_class.return_value = mock_llm

    result = run_extraction(_make_ocr_result())

    assert result.invoice_number is None
    assert result.total_amount is None
