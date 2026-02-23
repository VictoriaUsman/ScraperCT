from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.scrape_job import JobStatus


class ScrapeJobResponse(BaseModel):
    id: int
    source_id: int
    status: JobStatus
    triggered_by: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    records_found: int
    records_new: int
    records_updated: int
    records_skipped: int
    error_message: Optional[str] = None
    log_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScrapeJobListResponse(BaseModel):
    id: int
    source_id: int
    status: JobStatus
    triggered_by: str
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    records_found: int
    records_new: int
    records_updated: int
    records_skipped: int
    error_message: Optional[str] = None
    log_text: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
