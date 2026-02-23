from sqlalchemy import String, Boolean, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import enum

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .scrape_job import ScrapeJob


class SourceType(str, enum.Enum):
    ckan_api = "ckan_api"
    vision_gov = "vision_gov"
    land_records = "land_records"
    ct_sos = "ct_sos"
    iqs_land_records = "iqs_land_records"
    patriot_assessor = "patriot_assessor"
    arcgis_parcels = "arcgis_parcels"
    ct_courts = "ct_courts"
    ct_tax = "ct_tax"
    municipal_data = "municipal_data"


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    source_type: Mapped[SourceType] = mapped_column(
        SAEnum(SourceType, name="source_type_enum"), nullable=False
    )
    base_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    config_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cron_schedule: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_scraped_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    scrape_jobs: Mapped[list["ScrapeJob"]] = relationship(
        "ScrapeJob", back_populates="source", lazy="select"
    )
