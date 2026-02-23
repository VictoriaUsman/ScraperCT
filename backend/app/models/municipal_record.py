from sqlalchemy import String, Float, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import date
from typing import Optional

from .base import Base, TimestampMixin


class MunicipalRecord(Base, TimestampMixin):
    __tablename__ = "municipal_records"
    __table_args__ = (UniqueConstraint("fingerprint", name="uq_municipal_fingerprint"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    town: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    document_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    meeting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    body_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    document_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    file_format: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
