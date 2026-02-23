from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any


class PropertyRecordResponse(BaseModel):
    id: int
    source_id: int
    scrape_job_id: Optional[int] = None
    fingerprint: str
    town: Optional[str] = None
    parcel_id: Optional[str] = None
    map_lot: Optional[str] = None
    street_number: Optional[str] = None
    street_name: Optional[str] = None
    unit: Optional[str] = None
    zip_code: Optional[str] = None
    owner_name: Optional[str] = None
    owner_address: Optional[str] = None
    assessed_value: Optional[float] = None
    land_value: Optional[float] = None
    building_value: Optional[float] = None
    assessment_year: Optional[int] = None
    property_class: Optional[str] = None
    acreage: Optional[float] = None
    building_sqft: Optional[int] = None
    year_built: Optional[int] = None
    quality_score: Optional[float] = None
    completeness_flags: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PropertyStatsResponse(BaseModel):
    total: int
    towns: list[str]
    avg_assessed_value: Optional[float] = None
    min_assessed_value: Optional[float] = None
    max_assessed_value: Optional[float] = None
    years: list[int]
