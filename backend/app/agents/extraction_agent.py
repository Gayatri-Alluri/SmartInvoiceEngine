import time
import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.models.invoice import OCRResult, ExtractedInvoice
from app.prompts.extraction import EXTRACTION_SYSTEM_PROMPT, EXTRACTION_USER_PROMPT_TEMPLATE
from app.config import settings

logger = structlog.get_logger()


def run_extraction(ocr_result: OCRResult) -> ExtractedInvoice:
    log = logger.bind(method=ocr_result.method_used, text_len=len(ocr_result.raw_text))
    log.info("extraction_started")

    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.google_api_key,
        temperature=0,
    )
    structured_llm = llm.with_structured_output(ExtractedInvoice)

    messages = [
        SystemMessage(content=EXTRACTION_SYSTEM_PROMPT),
        HumanMessage(content=EXTRACTION_USER_PROMPT_TEMPLATE.format(raw_text=ocr_result.raw_text)),
    ]

    for attempt in range(3):
        try:
            result = structured_llm.invoke(messages)
            log.info("extraction_success", attempt=attempt + 1)
            return result
        except Exception as e:
            log.warning("extraction_failed", attempt=attempt + 1, error=str(e))
            if "429" in str(e) and attempt < 2:
                time.sleep(5)
                continue
            if attempt == 2:
                break

    log.error("extraction_all_attempts_failed")
    return ExtractedInvoice()
