"""
ArcGIS REST Feature Service parcel scraper.
Paginates using resultOffset until exceededTransferLimit is false.
Reprojects geometry centroid to WGS84 lat/lon if needed.
"""
import math
from typing import Optional, Any

from .base import BaseScraper, ScrapeResult

# CT State Plane (NAD83 / Connecticut) EPSG:2234 → WGS84 conversion constants
# We use a simple offset-based approximation; full reprojection would require pyproj.
# If the API returns wkid 4326 already, geometry x/y are already lon/lat.
_ARCGIS_WGS84_WKID = 4326


class ArcGISParcelsScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        layer_id: int = self.config.get("layer_id", 0)
        field_map: dict = self.config.get("field_map", {})

        query_url = self.base_url.rstrip("/") + "/query"
        result.log(f"Starting ArcGIS parcels scrape for {town} at {query_url}")

        offset = 0
        page_size = 1000
        page_num = 1

        try:
            # First, check spatial reference so we know if reprojection is needed
            sr_wkid = await self._get_spatial_ref_wkid()
            result.log(f"Spatial reference wkid: {sr_wkid}")

            while True:
                params = {
                    "where": "1=1",
                    "outFields": "*",
                    "returnGeometry": "true",
                    "outSR": "4326",  # request WGS84 from server
                    "f": "json",
                    "resultOffset": offset,
                    "resultRecordCount": page_size,
                }
                resp = await self._client.get(query_url, params=params)
                resp.raise_for_status()
                data = resp.json()

                if "error" in data:
                    result.error_message = str(data["error"])
                    result.log(f"ArcGIS API error: {data['error']}")
                    break

                features = data.get("features", [])
                if not features:
                    break

                records = [
                    self._feature_to_record(feat, town, field_map)
                    for feat in features
                ]
                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} parcels (offset {offset})")

                if not data.get("exceededTransferLimit", False):
                    break

                offset += page_size
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Error: {exc}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} ArcGIS parcel records")
        return result

    async def _get_spatial_ref_wkid(self) -> int:
        try:
            resp = await self._client.get(self.base_url.rstrip("/"), params={"f": "json"})
            data = resp.json()
            return data.get("extent", {}).get("spatialReference", {}).get("wkid", _ARCGIS_WGS84_WKID)
        except Exception:
            return _ARCGIS_WGS84_WKID

    def _feature_to_record(self, feature: dict[str, Any], town: str, field_map: dict) -> dict:
        attrs = feature.get("attributes", {})
        geom = feature.get("geometry", {})

        # Apply optional field_map remapping
        remapped: dict[str, Any] = {}
        for k, v in attrs.items():
            canonical = field_map.get(k, k)
            remapped[canonical] = v

        # Extract lat/lon from centroid (server returns in WGS84 when outSR=4326)
        lat: Optional[float] = None
        lon: Optional[float] = None
        if geom:
            if "x" in geom and "y" in geom:
                lon = geom["x"]
                lat = geom["y"]
            elif "rings" in geom:
                # Polygon: compute centroid from first ring
                ring = geom["rings"][0]
                if ring:
                    xs = [pt[0] for pt in ring]
                    ys = [pt[1] for pt in ring]
                    lon = sum(xs) / len(xs)
                    lat = sum(ys) / len(ys)

        def _get(*keys: str) -> Optional[Any]:
            for k in keys:
                v = remapped.get(k)
                if v is not None:
                    return v
            return None

        return {
            "town": town,
            "parcel_id": str(_get("parcel_id", "PARCEL_ID", "PID", "GIS_PIN", "MAP_LOT") or ""),
            "owner_name": _get("owner_name", "OWNER", "OWNERNAME", "OWN_NAME"),
            "street_number": _get("street_number", "SITE_NUMBER", "HOUSE_NO"),
            "street_name": _get("street_name", "SITE_STREET", "STREET_NAME"),
            "zip_code": _get("zip_code", "ZIP", "ZIPCODE"),
            "assessed_value": self._to_float(_get("assessed_value", "TOTAL_VAL", "ASSESS_VAL")),
            "land_value": self._to_float(_get("land_value", "LAND_VAL")),
            "building_value": self._to_float(_get("building_value", "BLDG_VAL")),
            "acreage": self._to_float(_get("acreage", "ACREAGE", "ACRES", "CALC_ACREAGE")),
            "property_class": _get("property_class", "USE_CODE", "PROP_CLASS"),
            "lat": lat,
            "lon": lon,
        }

    def _to_float(self, val: Any) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
