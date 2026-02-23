"""
Data quality validator.
Computes quality_score (0.0–1.0) and completeness_flags dict per record type.
"""
from typing import Any
from ..models.source import SourceType

# Fields required for a "complete" record per type
REQUIRED_FIELDS = {
    SourceType.ckan_api: ["dataset_id", "row_id", "data_json"],
    SourceType.vision_gov: ["town", "parcel_id", "owner_name", "assessed_value"],
    SourceType.land_records: ["town", "book", "page", "grantor", "recorded_date"],
    SourceType.ct_sos: ["business_id", "business_name", "status"],
    SourceType.iqs_land_records: ["town", "book", "page", "grantor", "recorded_date"],
    SourceType.patriot_assessor: ["town", "parcel_id", "owner_name", "assessed_value"],
    SourceType.arcgis_parcels: ["town", "parcel_id"],
    SourceType.ct_courts: ["case_number", "court_location", "case_type", "plaintiff"],
    SourceType.ct_tax: ["town", "account_no", "levy_year", "status"],
    SourceType.municipal_data: ["town", "document_url", "meeting_date", "document_type"],
}

OPTIONAL_SCORED_FIELDS = {
    SourceType.vision_gov: [
        "street_number", "street_name", "zip_code", "land_value",
        "building_value", "assessment_year", "property_class",
        "acreage", "building_sqft", "year_built",
    ],
    SourceType.land_records: [
        "grantee", "record_type", "instrument_no", "consideration",
        "parcel_id", "description", "document_url",
    ],
    SourceType.ct_sos: [
        "business_type", "formation_date", "principal_office",
        "registered_agent", "state_of_formation",
    ],
    SourceType.ckan_api: [],
    SourceType.iqs_land_records: [
        "grantee", "record_type", "instrument_no", "consideration",
        "parcel_id", "description", "document_url",
    ],
    SourceType.patriot_assessor: [
        "street_number", "street_name", "zip_code", "land_value",
        "building_value", "assessment_year", "property_class",
        "acreage", "building_sqft", "year_built",
    ],
    SourceType.arcgis_parcels: [
        "owner_name", "assessed_value", "acreage", "property_class", "lat", "lon",
    ],
    SourceType.ct_courts: [
        "defendant", "filing_date", "disposition", "judge", "amount_in_controversy",
    ],
    SourceType.ct_tax: [
        "owner_name", "property_address", "original_amount", "total_due", "due_date",
    ],
    SourceType.municipal_data: [
        "title", "body_name", "file_format", "description",
    ],
}


def validate_record(record: dict[str, Any], source_type: SourceType) -> tuple[float, dict]:
    """
    Returns (quality_score, completeness_flags).
    quality_score = fraction of required + optional fields that are non-null.
    completeness_flags = {field: True/False, ...}
    """
    required = REQUIRED_FIELDS.get(source_type, [])
    optional = OPTIONAL_SCORED_FIELDS.get(source_type, [])
    all_fields = required + optional

    flags: dict[str, bool] = {}
    for f in all_fields:
        val = record.get(f)
        flags[f] = val is not None and str(val).strip() != ""

    # Required fields missing → heavily penalise
    req_score = sum(flags.get(f, False) for f in required) / max(len(required), 1)
    opt_score = sum(flags.get(f, False) for f in optional) / max(len(optional), 1) if optional else 1.0

    # Weighted: 70% required, 30% optional
    quality_score = round(0.7 * req_score + 0.3 * opt_score, 4)
    return quality_score, flags
