from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Any


class CourtRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    case_number: Optional[str] = None
    docket_id: Optional[str] = None
    court_location: Optional[str] = None
    case_type: Optional[str] = None
    plaintiff: Optional[str] = None
    defendant: Optional[str] = None
    filing_date: Optional[date] = None
    disposition: Optional[str] = None
    disposition_date: Optional[date] = None
    judge: Optional[str] = None
    amount_in_controversy: Optional[float] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CourtRecordStatsResponse(BaseModel):
    total: int
    by_case_type: dict[str, int]
    by_court_location: dict[str, int]
