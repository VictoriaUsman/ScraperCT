from sqlalchemy import String, Integer, Float, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .base import Base, TimestampMixin


class PropertyRecord(Base, TimestampMixin):
    __tablename__ = "property_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_property_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    town: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parcel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    map_lot: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    street_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    street_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    zip_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    owner_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    owner_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    assessed_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    land_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    building_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    assessment_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    property_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    acreage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    building_sqft: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    year_built: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
