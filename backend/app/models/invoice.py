from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DocumentInput(BaseModel):
    file_bytes: bytes
    filename: str
    mime_type: str


class OCRMethod(str, Enum):
    PYMUPDF = "pymupdf"
    TESSERACT = "tesseract"
    GEMINI_VISION = "gemini_vision"


class OCRResult(BaseModel):
    raw_text: str
    confidence: float = Field(ge=0.0, le=1.0)
    method_used: OCRMethod
    error: Optional[str] = None


class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: float


class TaxInfo(BaseModel):
    percentage: Optional[float] = None
    amount: Optional[float] = None


class VendorInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class BuyerInfo(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None


class ExtractedInvoice(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: Optional[str] = None
    vendor: Optional[VendorInfo] = None
    buyer: Optional[BuyerInfo] = None
    line_items: list[LineItem] = []
    subtotal: Optional[float] = None
    tax: Optional[TaxInfo] = None
    total_amount: Optional[float] = None


class ValidationError(BaseModel):
    field: str
    rule: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[ValidationError] = []


class CorrectionEntry(BaseModel):
    field: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    method: str


class CorrectionLog(BaseModel):
    attempt_number: int
    corrections: list[CorrectionEntry] = []
    success: bool


class ProcessingMetadata(BaseModel):
    processing_time_ms: int
    confidence_score: float
    validation_status: str
    corrections_applied: list[CorrectionEntry] = []
    source_file: str
    ocr_method: OCRMethod


class InvoiceJSON(BaseModel):
    metadata: ProcessingMetadata
    invoice: ExtractedInvoice
