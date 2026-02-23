"""add new source types and tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-02-23
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add lat/lon to property_records (SQLite supports ADD COLUMN)
    op.add_column("property_records", sa.Column("lat", sa.Float(), nullable=True))
    op.add_column("property_records", sa.Column("lon", sa.Float(), nullable=True))

    # court_records
    op.create_table(
        "court_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("case_number", sa.String(100), nullable=True),
        sa.Column("docket_id", sa.String(100), nullable=True),
        sa.Column("court_location", sa.String(255), nullable=True),
        sa.Column("case_type", sa.String(50), nullable=True),
        sa.Column("plaintiff", sa.String(500), nullable=True),
        sa.Column("defendant", sa.String(500), nullable=True),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("disposition", sa.String(255), nullable=True),
        sa.Column("disposition_date", sa.Date(), nullable=True),
        sa.Column("judge", sa.String(255), nullable=True),
        sa.Column("amount_in_controversy", sa.Float(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_court_fingerprint"),
    )

    # tax_records
    op.create_table(
        "tax_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("town", sa.String(100), nullable=True),
        sa.Column("account_no", sa.String(100), nullable=True),
        sa.Column("owner_name", sa.String(500), nullable=True),
        sa.Column("property_address", sa.String(500), nullable=True),
        sa.Column("levy_year", sa.Integer(), nullable=True),
        sa.Column("bill_type", sa.String(100), nullable=True),
        sa.Column("original_amount", sa.Float(), nullable=True),
        sa.Column("interest", sa.Float(), nullable=True),
        sa.Column("penalty", sa.Float(), nullable=True),
        sa.Column("total_due", sa.Float(), nullable=True),
        sa.Column("paid_amount", sa.Float(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_tax_fingerprint"),
    )

    # municipal_records
    op.create_table(
        "municipal_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.Column("scrape_job_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("town", sa.String(100), nullable=True),
        sa.Column("document_type", sa.String(100), nullable=True),
        sa.Column("title", sa.String(500), nullable=True),
        sa.Column("meeting_date", sa.Date(), nullable=True),
        sa.Column("body_name", sa.String(255), nullable=True),
        sa.Column("document_url", sa.String(1024), nullable=True),
        sa.Column("file_format", sa.String(50), nullable=True),
        sa.Column("description", sa.String(1024), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("completeness_flags", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.ForeignKeyConstraint(["scrape_job_id"], ["scrape_jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint", name="uq_municipal_fingerprint"),
    )


def downgrade() -> None:
    op.drop_table("municipal_records")
    op.drop_table("tax_records")
    op.drop_table("court_records")
    op.drop_column("property_records", "lon")
    op.drop_column("property_records", "lat")
