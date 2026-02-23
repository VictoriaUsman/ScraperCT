from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Any
from ..models.land_record import LandRecordType


class LandRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    town: Optional[str] = None
    record_type: Optional[LandRecordType] = None
    grantor: Optional[str] = None
    grantee: Optional[str] = None
    recorded_date: Optional[date] = None
    book: Optional[str] = None
    page: Optional[str] = None
    instrument_no: Optional[str] = None
    consideration: Optional[float] = None
    parcel_id: Optional[str] = None
    description: Optional[str] = None
    document_url: Optional[str] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LandRecordStatsResponse(BaseModel):
    total: int
    towns: list[str]
    record_types: dict[str, int]
