"""
CT Secretary of State business registry scraper.
Primary: undocumented CONCORD REST API.
Fallback: Playwright alphabetical sweep.
"""
from typing import Any, Optional
import string
from .base import BaseScraper, ScrapeResult


class SoSBusinessScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        result.log("Starting CT SoS business scrape")
        try:
            return await self._scrape_api(result)
        except Exception as exc:
            result.log(f"REST API failed ({exc}), falling back to Playwright")
            result.error_message = None  # Reset for fallback
            return await self._scrape_playwright(result)

    async def _scrape_api(self, result: ScrapeResult) -> ScrapeResult:
        """Try the undocumented CONCORD REST endpoint."""
        api_url = f"{self.base_url.rstrip('/')}/CONCORD/web.user.search.controller"
        page = 1
        per_page = 100

        while True:
            params = {
                "action": "getSearchResults",
                "searchType": "BUSINESS",
                "businessName": "",
                "page": page,
                "resultsPerPage": per_page,
            }
            resp = await self._client.get(api_url, params=params)
            if resp.status_code != 200:
                raise RuntimeError(f"API returned {resp.status_code}")

            data = resp.json()
            items = data.get("results", data.get("businesses", []))
            if not items:
                break

            for item in items:
                result.records.append(self._normalize(item))

            result.log(f"API page {page}: {len(items)} records")
            if len(items) < per_page:
                break
            page += 1

        result.records_found = len(result.records)
        return result

    async def _scrape_playwright(self, result: ScrapeResult) -> ScrapeResult:
        """Alphabetical sweep via Playwright."""
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as pw:
                browser = await pw.chromium.launch(headless=True)
                page = await browser.new_page()

                for letter in string.ascii_uppercase:
                    try:
                        await page.goto(self.base_url, timeout=30000)
                        await page.fill("input[name='businessName']", letter)
                        await page.click("input[type='submit']")
                        await page.wait_for_load_state("networkidle")

                        rows = await page.query_selector_all("table tr")
                        for row in rows[1:]:  # skip header
                            cells = await row.query_selector_all("td")
                            if len(cells) < 3:
                                continue
                            texts = [await c.inner_text() for c in cells]
                            result.records.append(
                                {
                                    "business_id": texts[0].strip() if texts else None,
                                    "business_name": texts[1].strip() if len(texts) > 1 else None,
                                    "business_type": texts[2].strip() if len(texts) > 2 else None,
                                    "status": texts[3].strip() if len(texts) > 3 else None,
                                }
                            )
                        result.log(f"Letter {letter}: {len(rows)-1} rows")
                    except Exception as exc:
                        result.log(f"Error on letter {letter}: {exc}")

                await browser.close()
        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Playwright error: {exc}")

        result.records_found = len(result.records)
        return result

    def _normalize(self, raw: dict) -> dict:
        return {
            "business_id": str(raw.get("businessID") or raw.get("id") or ""),
            "business_name": raw.get("businessName") or raw.get("name"),
            "business_type": raw.get("businessType") or raw.get("type"),
            "status": raw.get("status"),
            "formation_date": raw.get("formationDate") or raw.get("registrationDate"),
            "dissolution_date": raw.get("dissolutionDate"),
            "principal_office": raw.get("principalOffice") or raw.get("address"),
            "registered_agent": raw.get("agentName") or raw.get("registeredAgent"),
            "agent_address": raw.get("agentAddress"),
            "annual_report_year": raw.get("annualReportYear"),
            "naics_code": raw.get("naicsCode"),
            "state_of_formation": raw.get("stateOfFormation") or "CT",
        }
