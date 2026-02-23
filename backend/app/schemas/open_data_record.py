from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class OpenDataRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    dataset_id: str
    dataset_name: Optional[str] = None
    row_id: str
    data_json: Optional[Any] = None
    tags: Optional[Any] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DatasetInfo(BaseModel):
    dataset_id: str
    dataset_name: Optional[str] = None
    record_count: int
