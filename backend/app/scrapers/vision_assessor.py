"""
Vision Government Solutions assessor portal scraper.
Primary: httpx + BeautifulSoup (form POST with VIEWSTATE).
Fallback: Playwright when config["use_playwright"] = true.
"""
from typing import Any, Optional
from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapeResult


class VisionAssessorScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        use_playwright: bool = self.config.get("use_playwright", False)
        search_type: str = self.config.get("search_type", "all")
        year: int = self.config.get("assessment_year", 2024)

        result.log(f"Starting Vision assessor scrape for {town} (playwright={use_playwright})")

        if use_playwright:
            return await self._scrape_playwright(result, town, year)
        return await self._scrape_httpx(result, town, year)

    async def _scrape_httpx(self, result: ScrapeResult, town: str, year: int) -> ScrapeResult:
        try:
            # Load the search page to get VIEWSTATE
            resp = await self._client.get(self.base_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            viewstate = self._extract_hidden(soup, "__VIEWSTATE")
            eventval = self._extract_hidden(soup, "__EVENTVALIDATION")

            # POST a search for all records (empty search = browse all)
            form_data = {
                "__VIEWSTATE": viewstate,
                "__EVENTVALIDATION": eventval,
                "__EVENTTARGET": "",
                "__EVENTARGUMENT": "",
                "btSearch": "Search",
            }
            search_resp = await self._client.post(self.base_url, data=form_data)
            search_resp.raise_for_status()
            result.log("Posted search form")

            records = self._parse_results(search_resp.text, town, year)
            result.records.extend(records)
            result.records_found = len(result.records)
            result.log(f"Parsed {result.records_found} property records")
        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Error: {exc}")
        return result

    async def _scrape_playwright(self, result: ScrapeResult, town: str, year: int) -> ScrapeResult:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(self.base_url, timeout=30000)
                # Click search to get all records
                await page.click("input[value='Search']")
                await page.wait_for_load_state("networkidle")
                html = await page.content()
                records = self._parse_results(html, town, year)
                result.records.extend(records)
                result.records_found = len(result.records)
                result.log(f"Playwright: parsed {result.records_found} records")
                await browser.close()
        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Playwright error: {exc}")
        return result

    def _extract_hidden(self, soup: BeautifulSoup, name: str) -> str:
        el = soup.find("input", {"name": name})
        return el["value"] if el else ""

    def _parse_results(self, html: str, town: str, year: int) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        records = []
        # Vision portals typically render results in a table with class 'SearchResults'
        table = soup.find("table", {"class": "SearchResults"}) or soup.find("table")
        if not table:
            return records
        rows = table.find_all("tr")[1:]  # skip header
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 3:
                continue
            records.append(
                {
                    "town": town,
                    "assessment_year": year,
                    "parcel_id": cells[0] if len(cells) > 0 else None,
                    "owner_name": cells[1] if len(cells) > 1 else None,
                    "street_number": cells[2].split()[0] if len(cells) > 2 and cells[2] else None,
                    "street_name": " ".join(cells[2].split()[1:]) if len(cells) > 2 and cells[2] else None,
                    "assessed_value": self._parse_money(cells[3]) if len(cells) > 3 else None,
                    "land_value": self._parse_money(cells[4]) if len(cells) > 4 else None,
                    "building_value": self._parse_money(cells[5]) if len(cells) > 5 else None,
                }
            )
        return records

    def _parse_money(self, val: str) -> Optional[float]:
        if not val:
            return None
        cleaned = val.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
