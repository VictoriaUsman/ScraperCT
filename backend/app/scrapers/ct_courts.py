"""
CT Judicial Branch civil and small claims court records scraper.
Targets civilinquiry.jud.ct.gov and smallclaimsinquiry.jud.ct.gov.
"""
from datetime import date, timedelta, datetime
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult

COURT_URLS = {
    "civil": "https://civilinquiry.jud.ct.gov/CaseSearch.aspx",
    "small_claims": "https://smallclaimsinquiry.jud.ct.gov/CaseSearch.aspx",
}


class CTCourtsScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        case_type: str = self.config.get("case_type", "civil")
        days_back: int = self.config.get("days_back", 30)
        court_location: Optional[str] = self.config.get("court_location")
        use_playwright: bool = self.config.get("use_playwright", False)

        date_from = date.today() - timedelta(days=days_back)
        date_to = date.today()

        search_url = COURT_URLS.get(case_type, COURT_URLS["civil"])
        result.log(f"Starting CT courts scrape: {case_type} ({date_from} to {date_to})")
        result.log(f"Target URL: {search_url}")

        if use_playwright:
            return await self._scrape_playwright(result, search_url, case_type, date_from, date_to, court_location)
        return await self._scrape_httpx(result, search_url, case_type, date_from, date_to, court_location)

    async def _scrape_httpx(
        self,
        result: ScrapeResult,
        search_url: str,
        case_type: str,
        date_from: date,
        date_to: date,
        court_location: Optional[str],
    ) -> ScrapeResult:
        try:
            resp = await self._client.get(search_url)
            result.log(f"GET {search_url} → HTTP {resp.status_code}")
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Dynamically extract all form fields so we don't rely on hardcoded names
            form_data = self._extract_form_fields(soup)
            result.log(f"Form fields found: {list(form_data.keys())}")

            # Inject date range into whichever fields hold filing dates
            date_from_str = date_from.strftime("%m/%d/%Y")
            date_to_str = date_to.strftime("%m/%d/%Y")
            self._set_date_field(form_data, ["FilingDateFrom", "DateFrom", "StartDate", "FromDate"], date_from_str)
            self._set_date_field(form_data, ["FilingDateTo", "DateTo", "EndDate", "ToDate"], date_to_str)

            # Trigger the search button
            self._set_submit_field(form_data, ["btnSearch", "ButtonSearch", "Search", "Submit"])

            if court_location:
                self._set_field(form_data, ["ddlCourt", "Court", "Location"], court_location)

            result.log(f"Submitting search with date range {date_from_str} to {date_to_str}")
            page_num = 1
            while True:
                search_resp = await self._client.post(search_url, data=form_data)
                result.log(f"POST page {page_num} → HTTP {search_resp.status_code}")
                search_resp.raise_for_status()

                records, has_next = self._parse_results(search_resp.text, case_type, result)

                if not records:
                    result.log("No records found on this page — stopping")
                    break

                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} court records")

                if not has_next:
                    break

                page_soup = BeautifulSoup(search_resp.text, "html.parser")
                form_data = self._extract_form_fields(page_soup)
                self._set_submit_field(form_data, ["lnkNext", "NextPage", "btnNext"])
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc) or repr(exc)
            result.log(f"Error: {result.error_message}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} court records found")
        return result

    async def _scrape_playwright(
        self,
        result: ScrapeResult,
        search_url: str,
        case_type: str,
        date_from: date,
        date_to: date,
        court_location: Optional[str],
    ) -> ScrapeResult:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(search_url, timeout=30000)
                result.log(f"Playwright loaded {search_url}")

                # Try to fill date fields by label text or common ID patterns
                for sel in ["[id*='FilingDateFrom']", "[id*='DateFrom']", "[name*='DateFrom']"]:
                    try:
                        await page.fill(sel, date_from.strftime("%m/%d/%Y"))
                        break
                    except Exception:
                        continue

                for sel in ["[id*='FilingDateTo']", "[id*='DateTo']", "[name*='DateTo']"]:
                    try:
                        await page.fill(sel, date_to.strftime("%m/%d/%Y"))
                        break
                    except Exception:
                        continue

                if court_location:
                    for sel in ["[id*='ddlCourt']", "[id*='Court']", "[name*='Court']"]:
                        try:
                            await page.select_option(sel, court_location)
                            break
                        except Exception:
                            continue

                for sel in ["input[id*='Search']", "input[value='Search']", "button[id*='Search']"]:
                    try:
                        await page.click(sel)
                        break
                    except Exception:
                        continue

                await page.wait_for_load_state("networkidle")
                html = await page.content()
                records, _ = self._parse_results(html, case_type, result)
                result.records.extend(records)
                result.records_found = len(result.records)
                result.log(f"Playwright: {result.records_found} court records")
                await browser.close()
        except Exception as exc:
            result.error_message = str(exc) or repr(exc)
            result.log(f"Playwright error: {result.error_message}")
        return result

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _extract_form_fields(self, soup: BeautifulSoup) -> dict:
        """Extract all hidden + visible form inputs into a dict."""
        fields: dict[str, str] = {}
        form = soup.find("form") or soup
        for inp in form.find_all("input"):
            name = inp.get("name")
            if not name:
                continue
            fields[name] = inp.get("value", "")
        for sel in form.find_all("select"):
            name = sel.get("name")
            if not name:
                continue
            selected = sel.find("option", selected=True)
            fields[name] = selected["value"] if selected else ""
        return fields

    def _set_date_field(self, fields: dict, candidates: list[str], value: str) -> None:
        """Set the first matching field name (case-insensitive suffix match)."""
        for key in list(fields.keys()):
            key_lower = key.lower()
            for candidate in candidates:
                if candidate.lower() in key_lower:
                    fields[key] = value
                    return

    def _set_field(self, fields: dict, candidates: list[str], value: str) -> None:
        for key in list(fields.keys()):
            key_lower = key.lower()
            for candidate in candidates:
                if candidate.lower() in key_lower:
                    fields[key] = value
                    return

    def _set_submit_field(self, fields: dict, candidates: list[str]) -> None:
        """Mark the submit/button field so ASP.NET knows which button was clicked."""
        for key in list(fields.keys()):
            key_lower = key.lower()
            for candidate in candidates:
                if candidate.lower() in key_lower:
                    fields[key] = "Search"
                    return

    def _parse_results(self, html: str, case_type: str, result: ScrapeResult) -> tuple[list[dict], bool]:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        # Try multiple table selectors used by CT Judicial sites
        table = (
            soup.find("table", {"class": "GridView"})
            or soup.find("table", id=lambda x: x and "Grid" in str(x))
            or soup.find("table", {"class": "tblSearch"})
            or soup.find("table", {"class": "searchresults"})
            or soup.find("table", {"summary": lambda x: x and "case" in str(x).lower()})
        )

        if not table:
            # Log a snippet to help diagnose what the page actually returned
            body_text = soup.get_text(separator=" ", strip=True)[:300]
            result.log(f"No results table found. Page snippet: {body_text}")
            return records, False

        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        result.log(f"Table headers: {headers}")

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 2:
                continue

            # Map by header position if available, otherwise fall back to index
            def cell(idx: int, *keys: str) -> Optional[str]:
                for k in keys:
                    for i, h in enumerate(headers):
                        if k in h and i < len(cells):
                            return cells[i] or None
                return cells[idx] if idx < len(cells) else None

            records.append({
                "case_number": cell(0, "case", "docket", "number"),
                "docket_id": cell(1, "docket"),
                "court_location": cell(2, "court", "location", "jd"),
                "case_type": case_type,
                "plaintiff": cell(3, "plaintiff", "party"),
                "defendant": cell(4, "defendant"),
                "filing_date": self._parse_date(cell(5, "filed", "filing", "date") or ""),
                "disposition": cell(6, "disposition", "status"),
                "disposition_date": self._parse_date(cell(7, "disposition date") or ""),
                "judge": cell(8, "judge"),
                "amount_in_controversy": self._parse_money(cell(9, "amount") or ""),
            })

        has_next = (
            soup.find("a", id=lambda x: x and "lnkNext" in str(x)) is not None
            or soup.find("a", string=lambda s: s and "next" in s.lower()) is not None
        )
        return records, has_next

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
