import io
import fitz
import pytesseract
from PIL import Image
import structlog

from app.models.invoice import DocumentInput, OCRResult, OCRMethod
from app.config import settings

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

logger = structlog.get_logger()


def run_ocr(document: DocumentInput) -> OCRResult:
    log = logger.bind(filename=document.filename, mime_type=document.mime_type)
    log.info("ocr_started")

    if document.mime_type == "application/pdf":
        result = _try_pymupdf(document, log)
        if result and result.raw_text.strip():
            return result
        log.info("pymupdf_empty_fallback_tesseract")
        result = _try_tesseract_pdf(document, log)
    else:
        result = _try_tesseract_image(document, log)

    if result and result.confidence >= settings.ocr_confidence_threshold:
        return result

    log.info("low_confidence_fallback_vision", confidence=result.confidence if result else 0)
    vision_result = _try_gemini_vision(document, log)
    if vision_result:
        return vision_result

    if result:
        return result

    return OCRResult(
        raw_text="",
        confidence=0.0,
        method_used=OCRMethod.TESSERACT,
        error="All OCR methods failed",
    )


def _try_pymupdf(document: DocumentInput, log: structlog.BoundLogger) -> OCRResult | None:
    try:
        doc = fitz.open(stream=document.file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        if text.strip():
            log.info("pymupdf_success", chars=len(text))
            return OCRResult(
                raw_text=text,
                confidence=0.95,
                method_used=OCRMethod.PYMUPDF,
            )
        return None
    except Exception as e:
        log.warning("pymupdf_failed", error=str(e))
        return None


def _try_tesseract_pdf(document: DocumentInput, log: structlog.BoundLogger) -> OCRResult | None:
    try:
        doc = fitz.open(stream=document.file_bytes, filetype="pdf")
        text = ""
        confidences = []

        for page in doc:
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            page_text = " ".join(
                word for word, conf in zip(data["text"], data["conf"]) if int(conf) > 0
            )
            page_confs = [int(c) for c in data["conf"] if int(c) > 0]
            text += page_text + "\n"
            confidences.extend(page_confs)

        doc.close()
        avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

        log.info("tesseract_pdf_success", chars=len(text), confidence=avg_conf)
        return OCRResult(
            raw_text=text,
            confidence=avg_conf,
            method_used=OCRMethod.TESSERACT,
        )
    except Exception as e:
        log.warning("tesseract_pdf_failed", error=str(e))
        return None


def _try_tesseract_image(document: DocumentInput, log: structlog.BoundLogger) -> OCRResult | None:
    try:
        img = Image.open(io.BytesIO(document.file_bytes))
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        text = " ".join(
            word for word, conf in zip(data["text"], data["conf"]) if int(conf) > 0
        )
        confidences = [int(c) for c in data["conf"] if int(c) > 0]
        avg_conf = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0

        log.info("tesseract_image_success", chars=len(text), confidence=avg_conf)
        return OCRResult(
            raw_text=text,
            confidence=avg_conf,
            method_used=OCRMethod.TESSERACT,
        )
    except Exception as e:
        log.warning("tesseract_image_failed", error=str(e))
        return None


def _try_gemini_vision(document: DocumentInput, log: structlog.BoundLogger) -> OCRResult | None:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        import base64

        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )

        b64_data = base64.b64encode(document.file_bytes).decode()
        message = HumanMessage(
            content=[
                {"type": "text", "text": "Extract all text from this document image. Return only the raw text, preserving layout as much as possible."},
                {"type": "image_url", "image_url": {"url": f"data:{document.mime_type};base64,{b64_data}"}},
            ]
        )

        response = llm.invoke([message])
        text = response.content

        log.info("gemini_vision_success", chars=len(text))
        return OCRResult(
            raw_text=text,
            confidence=0.85,
            method_used=OCRMethod.GEMINI_VISION,
        )
    except Exception as e:
        log.warning("gemini_vision_failed", error=str(e))
        return None
