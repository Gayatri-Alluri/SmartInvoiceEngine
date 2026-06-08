from pydantic import BaseModel
from typing import Optional

from app.models.invoice import InvoiceJSON


class ProcessResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    current_stage: str
    stages_completed: list[str]
    elapsed_ms: int


class ResultResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[InvoiceJSON] = None
    error: Optional[str] = None
