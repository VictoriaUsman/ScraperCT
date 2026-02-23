from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Any


class TaxRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    town: Optional[str] = None
    account_no: Optional[str] = None
    owner_name: Optional[str] = None
    property_address: Optional[str] = None
    levy_year: Optional[int] = None
    bill_type: Optional[str] = None
    original_amount: Optional[float] = None
    interest: Optional[float] = None
    penalty: Optional[float] = None
    total_due: Optional[float] = None
    paid_amount: Optional[float] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaxRecordStatsResponse(BaseModel):
    total: int
    by_town: dict[str, int]
    by_status: dict[str, int]
    total_delinquent_amount: Optional[float] = None
