"""
Patriot Properties assessor portal scraper.
ASP.NET WebForms — same VIEWSTATE pattern as Vision.
Portals: New Haven, Bridgeport, Waterbury, Norwalk, etc.
"""
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult


class PatriotAssessorScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        year: int = self.config.get("assessment_year", 2024)
        use_playwright: bool = self.config.get("use_playwright", False)

        result.log(f"Starting Patriot assessor scrape for {town} (playwright={use_playwright})")

        if use_playwright:
            return await self._scrape_playwright(result, town, year)
        return await self._scrape_httpx(result, town, year)

    async def _scrape_httpx(self, result: ScrapeResult, town: str, year: int) -> ScrapeResult:
        search_url = self.base_url.rstrip("/") + "/FieldCard.asp"
        try:
            resp = await self._client.get(search_url)
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
                "btSearch": "Search",
            }

            page_num = 1
            while True:
                search_resp = await self._client.post(search_url, data=form_data)
                search_resp.raise_for_status()
                records, has_next = self._parse_results(search_resp.text, town, year)

                if not records:
                    break

                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} property records")

                if not has_next:
                    break

                # Navigate to next page via postback
                page_soup = BeautifulSoup(search_resp.text, "html.parser")
                form_data = {
                    "__VIEWSTATE": self._extract_hidden(page_soup, "__VIEWSTATE"),
                    "__VIEWSTATEGENERATOR": self._extract_hidden(page_soup, "__VIEWSTATEGENERATOR"),
                    "__EVENTVALIDATION": self._extract_hidden(page_soup, "__EVENTVALIDATION"),
                    "__EVENTTARGET": "lnkNext",
                    "__EVENTARGUMENT": "",
                }
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Error: {exc}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} Patriot property records")
        return result

    async def _scrape_playwright(self, result: ScrapeResult, town: str, year: int) -> ScrapeResult:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()
                search_url = self.base_url.rstrip("/") + "/FieldCard.asp"
                await page.goto(search_url, timeout=30000)
                await page.click("input[value='Search']")
                await page.wait_for_load_state("networkidle")
                html = await page.content()
                records, _ = self._parse_results(html, town, year)
                result.records.extend(records)
                result.records_found = len(result.records)
                result.log(f"Playwright: {result.records_found} records")
                await browser.close()
        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Playwright error: {exc}")
        return result

    def _extract_hidden(self, soup: BeautifulSoup, name: str) -> str:
        el = soup.find("input", {"name": name})
        return el["value"] if el else ""

    def _parse_results(self, html: str, town: str, year: int) -> tuple[list[dict], bool]:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        table = soup.find("table", {"class": "SearchResults"}) or soup.find("table")
        if not table:
            return records, False

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 3:
                continue
            records.append({
                "town": town,
                "assessment_year": year,
                "parcel_id": cells[0] if len(cells) > 0 else None,
                "owner_name": cells[1] if len(cells) > 1 else None,
                "street_number": cells[2].split()[0] if len(cells) > 2 and cells[2] else None,
                "street_name": " ".join(cells[2].split()[1:]) if len(cells) > 2 and cells[2] else None,
                "assessed_value": self._parse_money(cells[3]) if len(cells) > 3 else None,
                "land_value": self._parse_money(cells[4]) if len(cells) > 4 else None,
                "building_value": self._parse_money(cells[5]) if len(cells) > 5 else None,
                "property_class": cells[6] if len(cells) > 6 else None,
            })

        has_next = soup.find("a", string=lambda s: s and "next" in s.lower()) is not None
        return records, has_next

    def _parse_money(self, val: str) -> Optional[float]:
        if not val:
            return None
        cleaned = val.replace("$", "").replace(",", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
