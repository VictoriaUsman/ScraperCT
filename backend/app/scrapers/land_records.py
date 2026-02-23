"""
Town clerk land records scraper (Laredo/Granicus-style HTML tables).
Searches by date range, parses paginated HTML tables.
"""
from typing import Any, Optional
from datetime import date, timedelta
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapeResult


class LandRecordsScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        days_back: int = self.config.get("days_back", 30)
        date_from = date.today() - timedelta(days=days_back)
        date_to = date.today()

        result.log(f"Starting land records scrape for {town} ({date_from} to {date_to})")

        page_num = 1
        while True:
            try:
                params = {
                    "town": town,
                    "dateFrom": date_from.strftime("%m/%d/%Y"),
                    "dateTo": date_to.strftime("%m/%d/%Y"),
                    "page": page_num,
                }
                resp = await self._client.get(self.base_url, params=params)
                resp.raise_for_status()

                records, has_next = self._parse_page(resp.text, town)
                if not records:
                    break

                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} records")

                if not has_next:
                    break
                page_num += 1
            except Exception as exc:
                result.error_message = str(exc)
                result.log(f"Error on page {page_num}: {exc}")
                break

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} land records found")
        return result

    def _parse_page(self, html: str, town: str) -> tuple[list[dict], bool]:
        soup = BeautifulSoup(html, "html.parser")
        records = []
        table = soup.find("table", {"class": "SearchResults"}) or soup.find("table")
        if not table:
            return records, False

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 4:
                continue
            # Determine record type
            raw_type = cells[2].lower() if len(cells) > 2 else ""
            rec_type = "other"
            for t in ("deed", "mortgage", "lien", "release"):
                if t in raw_type:
                    rec_type = t
                    break

            doc_link = row.find("a", href=True)
            doc_url = doc_link["href"] if doc_link else None

            records.append(
                {
                    "town": town,
                    "book": cells[0] if len(cells) > 0 else None,
                    "page": cells[1] if len(cells) > 1 else None,
                    "record_type": rec_type,
                    "grantor": cells[3] if len(cells) > 3 else None,
                    "grantee": cells[4] if len(cells) > 4 else None,
                    "recorded_date": self._parse_date(cells[5]) if len(cells) > 5 else None,
                    "instrument_no": cells[6] if len(cells) > 6 else None,
                    "consideration": self._parse_money(cells[7]) if len(cells) > 7 else None,
                    "document_url": doc_url,
                }
            )

        # Check for "Next" pagination link
        next_link = soup.find("a", string=lambda s: s and "next" in s.lower())
        return records, next_link is not None

    def _parse_date(self, val: str) -> Optional[str]:
        if not val:
            return None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
                from datetime import datetime
                return datetime.strptime(val.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    def _parse_money(self, val: str) -> Optional[float]:
        if not val:
            return None
        cleaned = val.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
