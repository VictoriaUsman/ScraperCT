from sqlalchemy import String, Float, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from .base import Base, TimestampMixin


class CourtRecord(Base, TimestampMixin):
    __tablename__ = "court_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_court_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    case_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    docket_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    court_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    case_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    plaintiff: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    defendant: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    filing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    disposition: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    disposition_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    judge: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount_in_controversy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
