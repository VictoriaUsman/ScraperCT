"""
Municipal meeting documents scraper.

Supports two platforms:
  - platform="legistar"   Legistar Web API (webapi.legistar.com) — NYC, Boston, Chicago, etc.
  - platform="civicweb"   CivicWeb / iCompass portal (*.civicweb.net) — Hartford CT and others.
"""
from datetime import date, timedelta, datetime
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapeResult

LEGISTAR_API = "https://webapi.legistar.com/v1"


class MunicipalDataScraper(BaseScraper):
    async def run(self) -> ScrapeResult:
        result = ScrapeResult()
        town: str = self.config.get("town", "")
        days_back: int = self.config.get("days_back", 90)
        body_filter: Optional[str] = self.config.get("body_filter")
        document_types: Optional[list] = self.config.get("document_types")
        platform: str = self.config.get("platform", "legistar")

        since_date = date.today() - timedelta(days=days_back)
        result.log(f"Starting {platform} scrape for {town} (since {since_date})")

        if platform == "civicweb":
            return await self._scrape_civicweb(result, town, since_date, body_filter, document_types)
        return await self._scrape_legistar(result, town, since_date, body_filter, document_types)

    # ── Legistar ───────────────────────────────────────────────────────────────

    async def _scrape_legistar(
        self,
        result: ScrapeResult,
        town: str,
        since_date: date,
        body_filter: Optional[str],
        document_types: Optional[list],
    ) -> ScrapeResult:
        api_base = f"{LEGISTAR_API}/{town}"
        date_str = since_date.strftime("%Y-%m-%dT00:00:00")
        meetings_url = f"{api_base}/Meetings"
        params: dict = {
            "$filter": f"MeetingDate ge datetime'{date_str}'",
            "$orderby": "MeetingDate desc",
        }
        if body_filter:
            params["$filter"] += f" and MeetingBodyName eq '{body_filter}'"

        try:
            resp = await self._client.get(meetings_url, params=params)
            result.log(f"GET {meetings_url} → HTTP {resp.status_code}")
            resp.raise_for_status()
            meetings = resp.json()
            result.log(f"Found {len(meetings)} meetings")

            for meeting in meetings:
                meeting_id = meeting.get("MeetingId") or meeting.get("EventId")
                if not meeting_id:
                    continue
                meeting_date = self._parse_date(str(meeting.get("MeetingDate", "")))
                body_name = meeting.get("MeetingBodyName") or meeting.get("EventBodyName", "")

                for doc_key in ("MeetingAgendaFile", "MeetingMinutesFile", "MeetingPacketFile"):
                    doc_url = meeting.get(doc_key)
                    if not doc_url:
                        continue
                    doc_type = doc_key.replace("Meeting", "").replace("File", "").lower()
                    if document_types and doc_type not in document_types:
                        continue
                    result.records.append({
                        "town": town,
                        "document_type": doc_type,
                        "title": f"{body_name} {doc_type.capitalize()} {meeting_date or ''}".strip(),
                        "meeting_date": meeting_date,
                        "body_name": body_name,
                        "document_url": doc_url,
                        "file_format": self._guess_format(doc_url),
                        "description": None,
                        "tags": None,
                    })

                try:
                    items_resp = await self._client.get(f"{api_base}/Meetings/{meeting_id}/MeetingItems")
                    items_resp.raise_for_status()
                    items = items_resp.json()
                except Exception:
                    items = []

                for item in items:
                    for doc in item.get("MatterAttachments", []) or []:
                        doc_url = doc.get("MatterAttachmentHyperlink") or doc.get("MatterAttachmentName")
                        if not doc_url:
                            continue
                        if document_types and "attachment" not in document_types:
                            continue
                        result.records.append({
                            "town": town,
                            "document_type": "attachment",
                            "title": doc.get("MatterAttachmentName") or "",
                            "meeting_date": meeting_date,
                            "body_name": body_name,
                            "document_url": doc_url,
                            "file_format": self._guess_format(doc_url),
                            "description": item.get("MatterTitle"),
                            "tags": None,
                        })

        except Exception as exc:
            result.error_message = str(exc) or repr(exc)
            result.log(f"Legistar error: {result.error_message}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} Legistar documents")
        return result

    # ── CivicWeb (iCompass/Granicus) ───────────────────────────────────────────

    async def _scrape_civicweb(
        self,
        result: ScrapeResult,
        town: str,
        since_date: date,
        body_filter: Optional[str],
        document_types: Optional[list],
    ) -> ScrapeResult:
        """
        Scrape CivicWeb portal (*.civicweb.net/Portal).
        Hartford CT: https://hartford.civicweb.net/Portal
        """
        portal_base = self.base_url.rstrip("/")
        meetings_url = f"{portal_base}/MeetingInformation.aspx"

        try:
            resp = await self._client.get(meetings_url)
            result.log(f"GET {meetings_url} → HTTP {resp.status_code}")
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")
            meeting_links = self._find_civicweb_meetings(soup, since_date, body_filter)
            result.log(f"Found {len(meeting_links)} meeting links since {since_date}")

            for meeting_url, meeting_date, body_name in meeting_links:
                if not meeting_url.startswith("http"):
                    meeting_url = urljoin(portal_base + "/", meeting_url)
                try:
                    m_resp = await self._client.get(meeting_url)
                    m_resp.raise_for_status()
                    docs = self._parse_civicweb_meeting(
                        m_resp.text, town, meeting_date, body_name,
                        portal_base, document_types,
                    )
                    result.records.extend(docs)
                    result.log(f"  {body_name} {meeting_date}: {len(docs)} documents")
                except Exception as exc:
                    result.log(f"  Skipped {meeting_url}: {exc}")

        except Exception as exc:
            result.error_message = str(exc) or repr(exc)
            result.log(f"CivicWeb error: {result.error_message}")

        result.records_found = len(result.records)
        result.log(f"Completed: {result.records_found} CivicWeb documents")
        return result

    def _find_civicweb_meetings(
        self,
        soup: BeautifulSoup,
        since_date: date,
        body_filter: Optional[str],
    ) -> list[tuple[str, Optional[str], str]]:
        """Return list of (url, date_str, body_name) for meetings on or after since_date."""
        results = []
        # CivicWeb renders meetings in a table or list; look for rows with date + link
        for row in soup.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 2:
                continue
            link = row.find("a", href=True)
            if not link:
                continue

            # Try to extract a date from the row text
            row_text = row.get_text(separator=" ", strip=True)
            meeting_date_str = None
            for cell in cells:
                text = cell.get_text(strip=True)
                parsed = self._parse_date(text)
                if parsed:
                    meeting_date_str = parsed
                    break

            # Filter by date
            if meeting_date_str:
                try:
                    m_date = datetime.strptime(meeting_date_str, "%Y-%m-%d").date()
                    if m_date < since_date:
                        continue
                except ValueError:
                    pass

            # Filter by body name
            body_name = cells[0].get_text(strip=True) if cells else ""
            if body_filter and body_filter.lower() not in body_name.lower():
                continue

            results.append((link["href"], meeting_date_str, body_name))
        return results

    def _parse_civicweb_meeting(
        self,
        html: str,
        town: str,
        meeting_date: Optional[str],
        body_name: str,
        portal_base: str,
        document_types: Optional[list],
    ) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        docs = []

        # CivicWeb meeting pages have document links — look for PDF/doc links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            lower = href.lower()
            label = link.get_text(strip=True).lower()

            # Determine document type from link text or href
            if "agenda" in label or "agenda" in lower:
                doc_type = "agenda"
            elif "minute" in label or "minute" in lower:
                doc_type = "minutes"
            elif "packet" in label or "packet" in lower:
                doc_type = "packet"
            else:
                doc_type = "attachment"

            if document_types and doc_type not in document_types:
                continue

            # Only include actual file links
            if not any(lower.endswith(ext) for ext in (".pdf", ".doc", ".docx", ".xlsx", ".pptx")):
                if "/document/" not in lower and "/file/" not in lower:
                    continue

            doc_url = href if href.startswith("http") else urljoin(portal_base + "/", href)
            docs.append({
                "town": town,
                "document_type": doc_type,
                "title": link.get_text(strip=True),
                "meeting_date": meeting_date,
                "body_name": body_name,
                "document_url": doc_url,
                "file_format": self._guess_format(doc_url),
                "description": None,
                "tags": None,
            })

        return docs

    # ── Shared helpers ─────────────────────────────────────────────────────────

    def _parse_date(self, val: str) -> Optional[str]:
        if not val:
            return None
        if val.startswith("/Date("):
            try:
                ms = int(val[6:val.index(")")])
                return datetime.utcfromtimestamp(ms / 1000).date().isoformat()
            except Exception:
                return None
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y"):
            try:
                return datetime.strptime(val.strip(), fmt).date().isoformat()
            except ValueError:
                continue
        return None

    def _guess_format(self, url: str) -> Optional[str]:
        if not url:
            return None
        for ext in (".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt"):
            if url.lower().endswith(ext):
                return ext.lstrip(".")
        return None
