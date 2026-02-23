"""
SearchIQS land records scraper.
Handles portals at searchiqs.com using VIEWSTATE form POSTs.
URL pattern: https://www.searchiqs.com/ct{abbrev}/
  Milford:    https://www.searchiqs.com/ctmilf/
  New Haven:  https://www.searchiqs.com/ctnha/
  Waterbury:  https://www.searchiqs.com/ctwby/
"""
from datetime import date, timedelta, datetime
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult


class IQSLandRecordsScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        days_back: int = self.config.get("days_back", 30)
        date_from = date.today() - timedelta(days=days_back)
        date_to = date.today()

        result.log(f"Starting IQS land records scrape for {town} ({date_from} to {date_to})")

        try:
            # Load search form to capture VIEWSTATE
            resp = await self._client.get(self.base_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            viewstate = self._extract_hidden(soup, "__VIEWSTATE")
            viewstate_gen = self._extract_hidden(soup, "__VIEWSTATEGENERATOR")
            eventval = self._extract_hidden(soup, "__EVENTVALIDATION")

            form_data = {
                "__VIEWSTATE": viewstate,
                "__VIEWSTATEGENERATOR": viewstate_gen,
                "__EVENTVALIDATION": eventval,
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "ctl00$cphMain$txtDateFrom": date_from.strftime("%m/%d/%Y"),
                "ctl00$cphMain$txtDateTo": date_to.strftime("%m/%d/%Y"),
                "ctl00$cphMain$btnSearch": "Search",
            }

            page_url = self.base_url
            page_num = 1
            while True:
                search_resp = await self._client.post(page_url, data=form_data)
                search_resp.raise_for_status()
                records, next_url = self._parse_page(search_resp.text, town)

                if not records:
                    break

                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} records")

                if not next_url:
                    break

                page_url = next_url
                # For subsequent pages, only carry VIEWSTATE (no search params)
                page_soup = BeautifulSoup(search_resp.text, "html.parser")
                form_data = {
                    "__VIEWSTATE": self._extract_hidden(page_soup, "__VIEWSTATE"),
                    "__VIEWSTATEGENERATOR": self._extract_hidden(page_soup, "__VIEWSTATEGENERATOR"),
                    "__EVENTVALIDATION": self._extract_hidden(page_soup, "__EVENTVALIDATION"),
                    "__EVENTTARGET": "ctl00$cphMain$lnkNext",
                    "__EVENTARGUMENT": "",
                }
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Error: {exc}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} IQS land records found")
        return result

    def _extract_hidden(self, soup: BeautifulSoup, name: str) -> str:
        el = soup.find("input", {"name": name})
        return el["value"] if el else ""

    def _parse_page(self, html: str, town: str) -> tuple[list[dict], Optional[str]]:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        table = soup.find("table", {"class": "SearchResults"}) or soup.find("table", id=lambda x: x and "grid" in x.lower())
        if not table:
            return records, None

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 4:
                continue

            raw_type = cells[2].lower() if len(cells) > 2 else ""
            rec_type = "other"
            for t in ("deed", "mortgage", "lien", "release"):
                if t in raw_type:
                    rec_type = t
                    break

            doc_link = row.find("a", href=True)
            doc_url = doc_link["href"] if doc_link else None

            records.append({
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
            })

        # Check for "Next" pagination link
        next_link = soup.find("a", id=lambda x: x and "lnkNext" in str(x))
        if not next_link:
            next_link = soup.find("a", string=lambda s: s and "next" in s.lower())
        next_url = next_link["href"] if next_link and next_link.get("href") else None

        return records, next_url

    def _parse_date(self, val: str) -> Optional[str]:
        if not val:
            return None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
            try:
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
