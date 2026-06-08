from datetime import datetime

from app.models.invoice import ExtractedInvoice, ValidationResult, ValidationError


def run_validation(invoice: ExtractedInvoice) -> ValidationResult:
    errors: list[ValidationError] = []

    _check_line_items_sum(invoice, errors)
    _check_total_calculation(invoice, errors)
    _check_required_fields(invoice, errors)
    _check_date_format(invoice, errors)
    _check_numeric_validity(invoice, errors)

    return ValidationResult(is_valid=len(errors) == 0, errors=errors)


def _check_line_items_sum(invoice: ExtractedInvoice, errors: list[ValidationError]) -> None:
    if not invoice.line_items or invoice.subtotal is None:
        return

    calculated = sum(item.amount for item in invoice.line_items)
    if abs(calculated - invoice.subtotal) > 0.01:
        errors.append(ValidationError(
            field="subtotal",
            rule="LINE_ITEMS_SUM",
            message="Sum of line items does not equal subtotal",
            expected=str(calculated),
            actual=str(invoice.subtotal),
        ))


def _check_total_calculation(invoice: ExtractedInvoice, errors: list[ValidationError]) -> None:
    if invoice.subtotal is None or invoice.total_amount is None:
        return

    tax_amount = invoice.tax.amount if invoice.tax and invoice.tax.amount is not None else 0.0
    expected_total = invoice.subtotal + tax_amount

    if abs(expected_total - invoice.total_amount) > 0.01:
        errors.append(ValidationError(
            field="total_amount",
            rule="TOTAL_CALCULATION",
            message="subtotal + tax does not equal total_amount",
            expected=str(expected_total),
            actual=str(invoice.total_amount),
        ))


def _check_required_fields(invoice: ExtractedInvoice, errors: list[ValidationError]) -> None:
    if invoice.invoice_number is None:
        errors.append(ValidationError(
            field="invoice_number",
            rule="REQUIRED_FIELDS",
            message="invoice_number is required",
        ))
    if invoice.invoice_date is None:
        errors.append(ValidationError(
            field="invoice_date",
            rule="REQUIRED_FIELDS",
            message="invoice_date is required",
        ))
    if invoice.total_amount is None:
        errors.append(ValidationError(
            field="total_amount",
            rule="REQUIRED_FIELDS",
            message="total_amount is required",
        ))


def _check_date_format(invoice: ExtractedInvoice, errors: list[ValidationError]) -> None:
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y"]

    for field_name in ("invoice_date", "due_date"):
        value = getattr(invoice, field_name)
        if value is None:
            continue

        parsed = False
        for fmt in date_formats:
            try:
                datetime.strptime(value, fmt)
                parsed = True
                break
            except ValueError:
                continue

        if not parsed:
            errors.append(ValidationError(
                field=field_name,
                rule="DATE_FORMAT",
                message=f"{field_name} is not a parseable date",
                actual=value,
            ))


def _check_numeric_validity(invoice: ExtractedInvoice, errors: list[ValidationError]) -> None:
    numeric_fields = [
        ("subtotal", invoice.subtotal),
        ("total_amount", invoice.total_amount),
    ]

    if invoice.tax and invoice.tax.amount is not None:
        numeric_fields.append(("tax.amount", invoice.tax.amount))
    if invoice.tax and invoice.tax.percentage is not None:
        numeric_fields.append(("tax.percentage", invoice.tax.percentage))

    for field_name, value in numeric_fields:
        if value is not None and value < 0:
            errors.append(ValidationError(
                field=field_name,
                rule="NUMERIC_VALIDITY",
                message=f"{field_name} must be >= 0",
                actual=str(value),
            ))

    for i, item in enumerate(invoice.line_items):
        if item.amount < 0:
            errors.append(ValidationError(
                field=f"line_items[{i}].amount",
                rule="NUMERIC_VALIDITY",
                message="line item amount must be >= 0",
                actual=str(item.amount),
            ))
        if item.quantity is not None and item.quantity < 0:
            errors.append(ValidationError(
                field=f"line_items[{i}].quantity",
                rule="NUMERIC_VALIDITY",
                message="line item quantity must be >= 0",
                actual=str(item.quantity),
            ))
        if item.unit_price is not None and item.unit_price < 0:
            errors.append(ValidationError(
                field=f"line_items[{i}].unit_price",
                rule="NUMERIC_VALIDITY",
                message="line item unit_price must be >= 0",
                actual=str(item.unit_price),
            ))
