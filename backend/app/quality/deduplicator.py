"""
Deduplicator using SHA-256 fingerprints on stable identity fields.
Returns "new" | "updated" | "skipped" for each record.
"""
import hashlib
import json
from typing import Any, Literal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.source import SourceType
from ..models.property_record import PropertyRecord
from ..models.land_record import LandRecord
from ..models.business_record import BusinessRecord
from ..models.open_data_record import OpenDataRecord
from ..models.court_record import CourtRecord
from ..models.tax_record import TaxRecord
from ..models.municipal_record import MunicipalRecord

DedupResult = Literal["new", "updated", "skipped"]

# Identity fields used to compute the fingerprint
FINGERPRINT_FIELDS = {
    SourceType.vision_gov: ["town", "parcel_id"],
    SourceType.land_records: ["town", "book", "page"],
    SourceType.ct_sos: ["business_id"],
    SourceType.ckan_api: ["dataset_id", "row_id"],
    SourceType.iqs_land_records: ["town", "book", "page"],
    SourceType.patriot_assessor: ["town", "parcel_id"],
    SourceType.arcgis_parcels: ["town", "parcel_id"],
    SourceType.ct_courts: ["case_number", "court_location"],
    SourceType.ct_tax: ["town", "account_no", "levy_year"],
    SourceType.municipal_data: ["town", "document_url"],
}

MODEL_MAP = {
    SourceType.vision_gov: PropertyRecord,
    SourceType.land_records: LandRecord,
    SourceType.ct_sos: BusinessRecord,
    SourceType.ckan_api: OpenDataRecord,
    SourceType.iqs_land_records: LandRecord,
    SourceType.patriot_assessor: PropertyRecord,
    SourceType.arcgis_parcels: PropertyRecord,
    SourceType.ct_courts: CourtRecord,
    SourceType.ct_tax: TaxRecord,
    SourceType.municipal_data: MunicipalRecord,
}


def compute_fingerprint(record: dict[str, Any], source_type: SourceType) -> str:
    fields = FINGERPRINT_FIELDS.get(source_type, [])
    key_parts = [str(record.get(f, "")).strip().lower() for f in fields]
    key = "|".join(key_parts)
    return hashlib.sha256(key.encode()).hexdigest()


async def upsert_record(
    record: dict[str, Any],
    source_type: SourceType,
    source_id: int,
    scrape_job_id: int,
    db: AsyncSession,
) -> DedupResult:
    """
    Attempt to insert; if fingerprint exists, update non-identity fields.
    Returns "new", "updated", or "skipped" (when data unchanged).
    """
    fingerprint = compute_fingerprint(record, source_type)
    Model = MODEL_MAP[source_type]

    # Look up existing record
    existing = (
        await db.execute(select(Model).where(Model.fingerprint == fingerprint))
    ).scalar_one_or_none()

    if existing is None:
        # Insert new
        obj = Model(
            source_id=source_id,
            scrape_job_id=scrape_job_id,
            fingerprint=fingerprint,
            **{k: v for k, v in record.items() if hasattr(Model, k)},
        )
        db.add(obj)
        await db.flush()
        return "new"
    else:
        # Check if any field changed
        changed = False
        for k, v in record.items():
            if hasattr(existing, k) and getattr(existing, k) != v:
                setattr(existing, k, v)
                changed = True
        # Always update job reference
        existing.scrape_job_id = scrape_job_id

        if changed:
            return "updated"
        return "skipped"
