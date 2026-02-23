from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Any


class MunicipalRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    town: Optional[str] = None
    document_type: Optional[str] = None
    title: Optional[str] = None
    meeting_date: Optional[date] = None
    body_name: Optional[str] = None
    document_url: Optional[str] = None
    file_format: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[Any] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MunicipalRecordStatsResponse(BaseModel):
    total: int
    by_town: dict[str, int]
    by_document_type: dict[str, int]
