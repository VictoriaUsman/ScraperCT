"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-02-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # sources
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("base_url", sa.String(1024), nullable=False),
        sa.Column("config_json", sa.Text(), nullable=True),
        sa.Column("cron_schedule", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("last_scraped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # scrape_jobs
    op.create_table(
        "scrape_jobs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("triggered_by", sa.String(50), nullable=False, server_default="scheduler"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_new", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("records_skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("log_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # property_records
    op.create_table(
        "property_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("town", sa.String(100), nullable=True),
        sa.Column("parcel_id", sa.String(100), nullable=True),
        sa.Column("map_lot", sa.String(100), nullable=True),
        sa.Column("street_number", sa.String(50), nullable=True),
        sa.Column("street_name", sa.String(255), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("owner_name", sa.String(500), nullable=True),
        sa.Column("owner_address", sa.String(500), nullable=True),
        sa.Column("assessed_value", sa.Float(), nullable=True),
        sa.Column("land_value", sa.Float(), nullable=True),
        sa.Column("building_value", sa.Float(), nullable=True),
        sa.Column("assessment_year", sa.Integer(), nullable=True),
        sa.Column("property_class", sa.String(100), nullable=True),
        sa.Column("acreage", sa.Float(), nullable=True),
        sa.Column("building_sqft", sa.Integer(), nullable=True),
        sa.Column("year_built", sa.Integer(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_property_fingerprint"),
    )

    # land_records
    op.create_table(
        "land_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("town", sa.String(100), nullable=True),
        sa.Column("record_type", sa.String(20), nullable=True),
        sa.Column("grantor", sa.String(500), nullable=True),
        sa.Column("grantee", sa.String(500), nullable=True),
        sa.Column("recorded_date", sa.Date(), nullable=True),
        sa.Column("book", sa.String(50), nullable=True),
        sa.Column("page", sa.String(50), nullable=True),
        sa.Column("instrument_no", sa.String(100), nullable=True),
        sa.Column("consideration", sa.Float(), nullable=True),
        sa.Column("parcel_id", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("document_url", sa.String(1024), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_land_fingerprint"),
    )

    # business_records
    op.create_table(
        "business_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("business_id", sa.String(100), nullable=True),
        sa.Column("business_name", sa.String(500), nullable=True),
        sa.Column("business_type", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("formation_date", sa.Date(), nullable=True),
        sa.Column("dissolution_date", sa.Date(), nullable=True),
        sa.Column("principal_office", sa.String(500), nullable=True),
        sa.Column("registered_agent", sa.String(500), nullable=True),
        sa.Column("agent_address", sa.String(500), nullable=True),
        sa.Column("annual_report_year", sa.Integer(), nullable=True),
        sa.Column("naics_code", sa.String(20), nullable=True),
        sa.Column("state_of_formation", sa.String(50), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_business_fingerprint"),
        sa.UniqueConstraint("business_id"),
    )

    # open_data_records
    op.create_table(
        "open_data_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("dataset_id", sa.String(255), nullable=False),
        sa.Column("dataset_name", sa.String(500), nullable=True),
        sa.Column("row_id", sa.String(255), nullable=False),
        sa.Column("data_json", sa.JSON(), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_open_data_fingerprint"),
        sa.UniqueConstraint("dataset_id", "row_id", name="uq_open_data_dataset_row"),
    )


def downgrade() -> None:
    op.drop_table("open_data_records")
    op.drop_table("business_records")
    op.drop_table("land_records")
    op.drop_table("property_records")
    op.drop_table("scrape_jobs")
    op.drop_table("sources")
