from sqlalchemy import String, Integer, Float, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from .base import Base, TimestampMixin


class TaxRecord(Base, TimestampMixin):
    __tablename__ = "tax_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_tax_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    town: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    account_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    owner_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    property_address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    levy_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    bill_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    original_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interest: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    penalty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_due: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    paid_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
