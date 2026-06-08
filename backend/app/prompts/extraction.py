EXTRACTION_SYSTEM_PROMPT = """You are an invoice data extraction specialist. Extract structured data from the provided invoice text.
Return ONLY valid JSON matching the specified schema. If a field is not present in the invoice, set it to null.
Do not invent or hallucinate data. Extract only what is explicitly stated in the text."""

EXTRACTION_USER_PROMPT_TEMPLATE = """Extract the following fields from this invoice text:

INVOICE TEXT:
---
{raw_text}
---

Return a JSON object with these fields:
- invoice_number (string or null)
- invoice_date (ISO date string or null)
- due_date (ISO date string or null)
- currency (3-letter ISO code or null)
- vendor: {{name, address}} (or null)
- buyer: {{name, address}} (or null)
- line_items: [{{description, quantity, unit_price, amount}}] (array, may be empty)
- subtotal (number or null)
- tax: {{percentage, amount}} (or null)
- total_amount (number or null)"""
