from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Any


class BusinessRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    business_id: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    status: Optional[str] = None
    formation_date: Optional[date] = None
    dissolution_date: Optional[date] = None
    principal_office: Optional[str] = None
    registered_agent: Optional[str] = None
    agent_address: Optional[str] = None
    annual_report_year: Optional[int] = None
    naics_code: Optional[str] = None
    state_of_formation: Optional[str] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BusinessStatsResponse(BaseModel):
    total: int
    by_type: dict[str, int]
    by_status: dict[str, int]
