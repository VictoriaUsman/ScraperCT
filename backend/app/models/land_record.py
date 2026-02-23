from sqlalchemy import String, Float, Text, ForeignKey, Date, Enum as SAEnum, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional
import enum

from .base import Base, TimestampMixin


class LandRecordType(str, enum.Enum):
    deed = "deed"
    mortgage = "mortgage"
    lien = "lien"
    release = "release"
    other = "other"


class LandRecord(Base, TimestampMixin):
    __tablename__ = "land_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_land_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    town: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    record_type: Mapped[Optional[LandRecordType]] = mapped_column(
        SAEnum(LandRecordType, name="land_record_type_enum"), nullable=True
    )
    grantor: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    grantee: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recorded_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    book: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    page: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    instrument_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consideration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    parcel_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
