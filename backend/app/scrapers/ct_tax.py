"""
CT town tax collector portal scraper.
Supports TaxSys (Grant Street Group) HTML and Invoice Cloud JSON REST.
"""
from datetime import date, datetime
from typing import Optional
from bs4 import BeautifulSoup

from .base import BaseScraper, ScrapeResult


class CTTaxCollectorScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "unknown")
        platform: str = self.config.get("platform", "taxsys")
        levy_year: int = self.config.get("levy_year", date.today().year)
        status_filter: str = self.config.get("status_filter", "all")

        result.log(f"Starting CT tax scrape for {town} (platform={platform}, year={levy_year})")

        if platform == "invoice_cloud":
            return await self._scrape_invoice_cloud(result, town, levy_year, status_filter)
        return await self._scrape_taxsys(result, town, levy_year, status_filter)

    async def _scrape_taxsys(
        self,
        result: ScrapeResult,
        town: str,
        levy_year: int,
        status_filter: str,
    ) -> ScrapeResult:
        base = self.base_url.rstrip("/")

        # mytaxbill.org (Grant Street Group TaxSys) — CT's actual tax portal
        # Home page: GET /inet/bill/home.do?town={town}
        if "mytaxbill.org" in base:
            home_url = f"{base}/inet/bill/home.do"
            init_params: dict = {"town": town}
        else:
            home_url = f"{base}/search"
            init_params = {}

        try:
            resp = await self._client.get(home_url, params=init_params)
            result.log(f"GET {home_url} → HTTP {resp.status_code}")
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract the search form and its action URL
            form = soup.find("form")
            action = (form.get("action") if form else None) or home_url
            if action and not action.startswith("http"):
                from urllib.parse import urljoin
                action = urljoin(home_url, action)

            # Collect all existing form field values (hidden inputs, etc.)
            form_data: dict = {}
            if form:
                for inp in form.find_all("input"):
                    name = inp.get("name")
                    if name:
                        form_data[name] = inp.get("value", "")
                for sel in form.find_all("select"):
                    name = sel.get("name")
                    if name:
                        selected = sel.find("option", selected=True)
                        form_data[name] = selected["value"] if selected else ""

            # Inject search criteria — TaxSys field names
            form_data["town"] = town
            for key in list(form_data.keys()):
                kl = key.lower()
                if "year" in kl or "billyear" in kl:
                    form_data[key] = str(levy_year)
            if status_filter == "delinquent":
                form_data["delinquent"] = "Y"

            # Activate the search submit button
            for inp in soup.find_all("input", {"type": "submit"}):
                name = inp.get("name")
                if name:
                    form_data[name] = inp.get("value", "Search")
                    break

            result.log(f"Submitting TaxSys search to {action} for {town} year={levy_year}")

            page_num = 1
            while True:
                search_resp = await self._client.post(action, data=form_data)
                result.log(f"POST page {page_num} → HTTP {search_resp.status_code}")
                search_resp.raise_for_status()

                records, has_next = self._parse_taxsys_page(search_resp.text, town, levy_year)

                if not records:
                    snippet = BeautifulSoup(search_resp.text, "html.parser").get_text(separator=" ", strip=True)[:300]
                    result.log(f"No records found. Page snippet: {snippet}")
                    break

                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} tax records")

                if not has_next:
                    break

                form_data["page"] = str(page_num + 1)
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc) or repr(exc)
            result.log(f"TaxSys error: {result.error_message}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} tax records found")
        return result

    async def _scrape_invoice_cloud(
        self,
        result: ScrapeResult,
        town: str,
        levy_year: int,
        status_filter: str,
    ) -> ScrapeResult:
        """Invoice Cloud exposes a JSON REST endpoint."""
        api_url = self.base_url.rstrip("/") + "/api/bills"
        params = {
            "levy_year": levy_year,
            "format": "json",
        }
        if status_filter == "delinquent":
            params["status"] = "delinquent"

        try:
            offset = 0
            page_size = 500
            page_num = 1
            while True:
                params["offset"] = offset
                params["limit"] = page_size
                resp = await self._client.get(api_url, params=params)
                resp.raise_for_status()
                data = resp.json()

                items = data if isinstance(data, list) else data.get("bills", data.get("items", []))
                if not items:
                    break

                records = [self._invoice_cloud_to_record(item, town, levy_year) for item in items]
                result.records.extend(records)
                result.log(f"Page {page_num}: {len(records)} tax records")

                if len(items) < page_size:
                    break

                offset += page_size
                page_num += 1

        except Exception as exc:
            result.error_message = str(exc)
            result.log(f"Invoice Cloud error: {exc}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} Invoice Cloud tax records")
        return result

    def _parse_taxsys_page(self, html: str, town: str, levy_year: int) -> tuple[list[dict], bool]:
        soup = BeautifulSoup(html, "html.parser")
        records = []

        table = soup.find("table", {"class": "results"}) or soup.find("table")
        if not table:
            return records, False

        rows = table.find_all("tr")[1:]
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all("td")]
            if len(cells) < 3:
                continue
            records.append({
                "town": town,
                "account_no": cells[0] if len(cells) > 0 else None,
                "owner_name": cells[1] if len(cells) > 1 else None,
                "property_address": cells[2] if len(cells) > 2 else None,
                "levy_year": levy_year,
                "bill_type": cells[3] if len(cells) > 3 else None,
                "original_amount": self._parse_money(cells[4]) if len(cells) > 4 else None,
                "interest": self._parse_money(cells[5]) if len(cells) > 5 else None,
                "penalty": self._parse_money(cells[6]) if len(cells) > 6 else None,
                "total_due": self._parse_money(cells[7]) if len(cells) > 7 else None,
                "paid_amount": self._parse_money(cells[8]) if len(cells) > 8 else None,
                "due_date": self._parse_date(cells[9]) if len(cells) > 9 else None,
                "status": cells[10] if len(cells) > 10 else None,
            })

        has_next = soup.find("a", string=lambda s: s and "next" in s.lower()) is not None
        return records, has_next

    def _invoice_cloud_to_record(self, item: dict, town: str, levy_year: int) -> dict:
        return {
            "town": town,
            "account_no": item.get("account_number") or item.get("accountNo"),
            "owner_name": item.get("owner_name") or item.get("ownerName"),
            "property_address": item.get("property_address") or item.get("propertyAddress"),
            "levy_year": levy_year,
            "bill_type": item.get("bill_type") or item.get("billType"),
            "original_amount": self._to_float(item.get("original_amount") or item.get("originalAmount")),
            "interest": self._to_float(item.get("interest")),
            "penalty": self._to_float(item.get("penalty")),
            "total_due": self._to_float(item.get("total_due") or item.get("totalDue")),
            "paid_amount": self._to_float(item.get("paid_amount") or item.get("paidAmount")),
            "due_date": self._parse_date(str(item.get("due_date") or item.get("dueDate") or "")),
            "status": item.get("status"),
        }

    def _parse_date(self, val: str) -> Optional[str]:
        if not val:
            return None
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
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

    def _to_float(self, val) -> Optional[float]:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
