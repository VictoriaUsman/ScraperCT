from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional
import httpx
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    records: list[dict[str, Any]] = field(default_factory=list)
    records_found: int = 0
    records_new: int = 0
    records_updated: int = 0
    records_skipped: int = 0
    error_message: Optional[str] = None
    log_lines: list[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        logger.info(msg)
        self.log_lines.append(msg)

    @property
    def log_text(self) -> str:
        return "\n".join(self.log_lines)


class BaseScraper(ABC):
    def __init__(self, source_id: int, config: dict[str, Any], base_url: str):
        self.source_id = source_id
        self.config = config
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "BaseScraper":
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
            headers={"User-Agent": "CTRecordsScraper/1.0"},
        )
        return self

    async def __aexit__(self, *args) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def run(self) -> ScrapeResult:
        """Execute the scrape and return results."""
        ...
