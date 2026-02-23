"""
CT Open Data scraper — Socrata SODA API (data.ct.gov)
Endpoint: /resource/{dataset_id}.json?$limit=N&$offset=N
Dataset IDs look like: 5mzw-sjtu  (4x4 Socrata format)

Config keys:
  dataset_id   (required) — 4x4 Socrata dataset identifier
  dataset_name (optional) — human label stored with each record
  page_size    (optional, default 1000) — rows per request
  max_records  (optional, default unlimited) — stop after N total rows
  tags         (optional) — list of tag strings
  params       (optional) — extra SODA params e.g. {"$where": "town='Hartford'"}
"""
from urllib.parse import quote
from .base import BaseScraper, ScrapeResult


class CTOpenDataScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        dataset_id: str = self.config.get("dataset_id", "")
        dataset_name: str = self.config.get("dataset_name", dataset_id)
        page_size: int = int(self.config.get("page_size", 1000))
        max_records: int | None = self.config.get("max_records")  # None = fetch all
        tags: list[str] = self.config.get("tags", [])
        extra_params: dict = self.config.get("params", {})

        if not dataset_id:
            result.error_message = "config missing 'dataset_id'"
            return result

        result.log(f"Starting Socrata scrape: dataset='{dataset_id}' base='{self.base_url}'"
                   + (f" max_records={max_records}" if max_records else ""))

        offset = 0
        total_fetched = 0

        while True:
            # Respect max_records — shrink the last page request if needed
            remaining = (max_records - total_fetched) if max_records else page_size
            this_page = min(page_size, remaining)

            # Build query string manually:
            # Keys keep literal '$' (httpx encodes '$'→'%24', breaking SODA param names)
            # Values are percent-encoded so spaces/quotes are safe in the URL
            qs_parts = [f"$limit={this_page}", f"$offset={offset}"]
            for k, v in extra_params.items():
                qs_parts.append(f"{k}={quote(str(v), safe='')}")
            url = f"{self.base_url.rstrip('/')}/resource/{dataset_id}.json?{'&'.join(qs_parts)}"
            result.log(f"GET {url}")

            try:
                resp = await self._client.get(url)
                if resp.status_code == 400:
                    # Surface Socrata's error message when available
                    try:
                        detail = resp.json().get("message", resp.text[:200])
                    except Exception:
                        detail = resp.text[:200]
                    result.error_message = f"Socrata 400: {detail}"
                    result.log(f"Bad request: {detail}")
                    break
                if resp.status_code == 404:
                    result.error_message = f"Dataset '{dataset_id}' not found — check the ID at data.ct.gov"
                    break
                resp.raise_for_status()
                rows: list[dict] = resp.json()
            except Exception as exc:
                result.error_message = str(exc)
                result.log(f"Request failed: {exc}")
                break

            if not rows:
                break

            for i, row in enumerate(rows):
                row_id = str(row.get(":id", offset + i))
                clean = {k: v for k, v in row.items() if not k.startswith(":")}
                result.records.append({
                    "dataset_id": dataset_id,
                    "dataset_name": dataset_name,
                    "row_id": row_id,
                    "data_json": clean,
                    "tags": tags,
                })

            total_fetched += len(rows)
            result.log(f"Fetched {total_fetched} rows so far")

            if len(rows) < this_page:
                break  # last page
            if max_records and total_fetched >= max_records:
                break  # hit the cap
            offset += this_page

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} records found")
        return result
