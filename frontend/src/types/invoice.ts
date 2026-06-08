export interface ProcessResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  job_id: string;
  status: string;
  current_stage: string;
  stages_completed: string[];
  elapsed_ms: number;
}

export interface LineItem {
  description: string;
  quantity: number | null;
  unit_price: number | null;
  amount: number;
}

export interface TaxInfo {
  percentage: number | null;
  amount: number | null;
}

export interface VendorInfo {
  name: string | null;
  address: string | null;
}

export interface BuyerInfo {
  name: string | null;
  address: string | null;
}

export interface CorrectionEntry {
  field: string;
  old_value: string | null;
  new_value: string | null;
  method: string;
}

export interface ExtractedInvoice {
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;
  currency: string | null;
  vendor: VendorInfo | null;
  buyer: BuyerInfo | null;
  line_items: LineItem[];
  subtotal: number | null;
  tax: TaxInfo | null;
  total_amount: number | null;
}

export interface ProcessingMetadata {
  processing_time_ms: number;
  confidence_score: number;
  validation_status: string;
  corrections_applied: CorrectionEntry[];
  source_file: string;
  ocr_method: string;
}

export interface InvoiceJSON {
  metadata: ProcessingMetadata;
  invoice: ExtractedInvoice;
}

export interface ResultResponse {
  job_id: string;
  status: string;
  result: InvoiceJSON | null;
  error: string | null;
}
