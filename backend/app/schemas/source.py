from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from typing import Optional, Any
from ..models.source import SourceType


class SourceBase(BaseModel):
    name: str
    source_type: SourceType
    base_url: str
    config_json: Optional[str] = None
    cron_schedule: Optional[str] = None
    is_active: bool = True


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    config_json: Optional[str] = None
    cron_schedule: Optional[str] = None
    is_active: Optional[bool] = None


class SourceResponse(SourceBase):
    id: int
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TriggerResponse(BaseModel):
    job_id: int
    message: str
