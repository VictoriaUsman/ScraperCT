from sqlalchemy import String, Float, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from .base import Base, TimestampMixin


class OpenDataRecord(Base, TimestampMixin):
    __tablename__ = "open_data_records"
    __table_args__ = (
        UniqueConstraint("dataset_id", "row_id", name="uq_open_data_dataset_row"),
        UniqueConstraint("fingerprint", name="uq_open_data_fingerprint"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    scrape_job_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("scrape_jobs.id"), nullable=True
    )
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    dataset_id: Mapped[str] = mapped_column(String(255), nullable=False)
    dataset_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    row_id: Mapped[str] = mapped_column(String(255), nullable=False)
    data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
