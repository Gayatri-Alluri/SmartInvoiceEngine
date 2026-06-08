import pytest
from unittest.mock import patch, MagicMock
from app.models.invoice import DocumentInput, OCRResult, OCRMethod


SAMPLE_PDF_TEXT = "Invoice #12345\nDate: 2024-01-01\nTotal: $100.00"


@patch("app.agents.ocr_agent.fitz")
def test_text_pdf(mock_fitz):
    mock_page = MagicMock()
    mock_page.get_text.return_value = SAMPLE_PDF_TEXT
    mock_doc = MagicMock()
    mock_doc.__iter__ = lambda self: iter([mock_page])
    mock_fitz.open.return_value = mock_doc

    from app.agents.ocr_agent import run_ocr

    document = DocumentInput(
        file_bytes=b"fake-pdf-bytes",
        filename="test.pdf",
        mime_type="application/pdf",
    )
    result = run_ocr(document)

    assert result.raw_text == SAMPLE_PDF_TEXT
    assert result.method_used == OCRMethod.PYMUPDF
    assert result.confidence == 0.95
    assert result.error is None


@patch("app.agents.ocr_agent.pytesseract")
@patch("app.agents.ocr_agent.Image")
def test_image_ocr(mock_image, mock_tesseract):
    mock_tesseract.Output.DICT = "dict"
    mock_tesseract.image_to_data.return_value = {
        "text": ["Invoice", "#123", "Total", "$50"],
        "conf": ["95", "90", "92", "88"],
    }
    mock_image.open.return_value = MagicMock()

    from app.agents.ocr_agent import run_ocr

    document = DocumentInput(
        file_bytes=b"fake-png-bytes",
        filename="test.png",
        mime_type="image/png",
    )
    result = run_ocr(document)

    assert "Invoice" in result.raw_text
    assert result.method_used == OCRMethod.TESSERACT
    assert result.confidence > 0.8
    assert result.error is None


@patch("app.agents.ocr_agent.fitz")
def test_pdf_empty_text_falls_back_to_tesseract(mock_fitz):
    mock_page = MagicMock()
    mock_page.get_text.return_value = ""
    mock_page.get_pixmap.return_value = MagicMock(tobytes=lambda fmt: b"fake-png")
    mock_doc = MagicMock()
    mock_doc.__iter__ = lambda self: iter([mock_page])
    mock_fitz.open.return_value = mock_doc

    with patch("app.agents.ocr_agent.pytesseract") as mock_tess, \
         patch("app.agents.ocr_agent.Image") as mock_img:
        mock_tess.Output.DICT = "dict"
        mock_tess.image_to_data.return_value = {
            "text": ["Scanned", "text"],
            "conf": ["85", "80"],
        }
        mock_img.open.return_value = MagicMock()

        from app.agents.ocr_agent import run_ocr

        document = DocumentInput(
            file_bytes=b"fake-scanned-pdf",
            filename="scanned.pdf",
            mime_type="application/pdf",
        )
        result = run_ocr(document)

        assert result.method_used == OCRMethod.TESSERACT
        assert "Scanned" in result.raw_text
