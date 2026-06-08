CORRECTION_SYSTEM_PROMPT = """You are an invoice data correction specialist. The previous extraction had validation errors.
Re-analyze the original invoice text and fix the identified errors.
Return the COMPLETE corrected invoice data as JSON. Do not hallucinate — only fix what is provably wrong."""

CORRECTION_USER_PROMPT_TEMPLATE = """The following extraction has validation errors. Please correct them.

ORIGINAL INVOICE TEXT:
---
{raw_text}
---

CURRENT EXTRACTION:
{extracted_json}

VALIDATION ERRORS:
{errors_list}

Return the corrected complete invoice JSON."""
