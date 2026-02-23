from sqlalchemy import String, Integer, Float, ForeignKey, Date, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from .base import Base, TimestampMixin


class BusinessRecord(Base, TimestampMixin):
    __tablename__ = "business_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_business_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    business_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    business_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    formation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    dissolution_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    principal_office: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    registered_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    agent_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    annual_report_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    naics_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    state_of_formation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
