import time
import structlog
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.models.invoice import (
    ExtractedInvoice,
    ValidationResult,
    OCRResult,
    CorrectionLog,
    CorrectionEntry,
)
from app.prompts.correction import CORRECTION_SYSTEM_PROMPT, CORRECTION_USER_PROMPT_TEMPLATE
from app.config import settings

logger = structlog.get_logger()


def run_correction(
    invoice: ExtractedInvoice,
    validation_result: ValidationResult,
    ocr_result: OCRResult,
) -> tuple[ExtractedInvoice, CorrectionLog]:
    log = logger.bind(error_count=len(validation_result.errors))
    log.info("correction_started")

    corrections: list[CorrectionEntry] = []
    corrected = invoice.model_copy(deep=True)

    auto_fixable_errors = [e for e in validation_result.errors if e.rule in ("LINE_ITEMS_SUM", "TOTAL_CALCULATION")]
    other_errors = [e for e in validation_result.errors if e.rule not in ("LINE_ITEMS_SUM", "TOTAL_CALCULATION")]

    for error in auto_fixable_errors:
        entry = _apply_rule_fix(corrected, error)
        if entry:
            corrections.append(entry)

    if other_errors:
        llm_result = _apply_llm_correction(corrected, other_errors, ocr_result, log)
        if llm_result:
            for field in ("invoice_number", "invoice_date", "due_date", "currency", "vendor", "buyer", "line_items", "subtotal", "tax", "total_amount"):
                old_val = getattr(corrected, field)
                new_val = getattr(llm_result, field)
                if old_val != new_val:
                    corrections.append(CorrectionEntry(
                        field=field,
                        old_value=str(old_val),
                        new_value=str(new_val),
                        method="llm_reanalysis",
                    ))
            corrected = llm_result

    log.info("correction_complete", corrections_count=len(corrections))
    return corrected, CorrectionLog(
        attempt_number=1,
        corrections=corrections,
        success=len(corrections) > 0,
    )


def _apply_rule_fix(invoice: ExtractedInvoice, error: ValidationResult) -> CorrectionEntry | None:
    if error.rule == "LINE_ITEMS_SUM" and invoice.line_items:
        old_value = str(invoice.subtotal)
        invoice.subtotal = sum(item.amount for item in invoice.line_items)
        return CorrectionEntry(
            field="subtotal",
            old_value=old_value,
            new_value=str(invoice.subtotal),
            method="rule_based",
        )

    if error.rule == "TOTAL_CALCULATION" and invoice.subtotal is not None:
        old_value = str(invoice.total_amount)
        tax_amount = invoice.tax.amount if invoice.tax and invoice.tax.amount is not None else 0.0
        invoice.total_amount = invoice.subtotal + tax_amount
        return CorrectionEntry(
            field="total_amount",
            old_value=old_value,
            new_value=str(invoice.total_amount),
            method="rule_based",
        )

    return None


def _apply_llm_correction(
    invoice: ExtractedInvoice,
    errors: list,
    ocr_result: OCRResult,
    log: structlog.BoundLogger,
) -> ExtractedInvoice | None:
    try:
        llm = ChatGoogleGenerativeAI(
            model=settings.llm_model,
            google_api_key=settings.google_api_key,
            temperature=0,
        )
        structured_llm = llm.with_structured_output(ExtractedInvoice)

        errors_text = "\n".join(f"- {e.field}: {e.message}" for e in errors)
        messages = [
            SystemMessage(content=CORRECTION_SYSTEM_PROMPT),
            HumanMessage(content=CORRECTION_USER_PROMPT_TEMPLATE.format(
                raw_text=ocr_result.raw_text,
                extracted_json=invoice.model_dump_json(indent=2),
                errors_list=errors_text,
            )),
        ]

        for attempt in range(3):
            try:
                result = structured_llm.invoke(messages)
                log.info("llm_correction_success")
                return result
            except Exception as e:
                log.warning("llm_correction_failed", attempt=attempt + 1, error=str(e))
                if "429" in str(e) and attempt < 2:
                    time.sleep(5)
                    continue
                break
        return None
    except Exception as e:
        log.error("llm_correction_setup_failed", error=str(e))
        return None
