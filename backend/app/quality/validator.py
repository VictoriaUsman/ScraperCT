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
