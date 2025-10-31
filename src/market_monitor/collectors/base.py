"""Collector abstractions for marketplace price retrieval."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    import httpx

from ..logging_config import get_logger

logger = get_logger(__name__)


class CollectorError(RuntimeError):
    """Raised when a collector fails to retrieve data."""


class PriceCollector(Protocol):
    """Interface definition for price collectors."""

    name: str

    def fetch(self, items: Iterable[str]) -> List["PriceQuote"]:
        """Fetch price quotes for the provided market hash names."""


@dataclass
class CollectorSettings:
    base_url: str
    timeout: float = 10.0
    max_retries: int = 3
    backoff_factor: float = 1.5
    proxy_pool: Optional[List[str]] = None
    headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class PriceQuote:
    source: str
    market_hash_name: str
    price: float
    currency: str
    metadata: Dict[str, object] = field(default_factory=dict)


class HttpCollector:
    """Base class for HTTP powered collectors with retry/backoff."""

    name = "base"

    def __init__(self, settings: CollectorSettings) -> None:
        self.settings = settings
        httpx_module = _require_httpx()
        self._client = httpx_module.Client(timeout=settings.timeout, headers=settings.headers)

    def _choose_proxy(self) -> Optional[str]:
        if not self.settings.proxy_pool:
            return None
        return random.choice(self.settings.proxy_pool)

    def _request(self, method: str, endpoint: str, **kwargs) -> "httpx.Response":
        httpx_module = _require_httpx()
        url = endpoint if endpoint.startswith("http") else self.settings.base_url + endpoint
        last_exc: Optional[Exception] = None
        for attempt in range(1, self.settings.max_retries + 1):
            proxy = self._choose_proxy()
            try:
                response = self._client.request(method, url, proxies=proxy, **kwargs)
                response.raise_for_status()
                return response
            except (httpx_module.RequestError, httpx_module.HTTPStatusError) as exc:
                last_exc = exc
                wait = self.settings.backoff_factor ** attempt
                logger.warning("%s collector request failed (attempt %s/%s): %s", self.name, attempt, self.settings.max_retries, exc)
                time.sleep(wait)
        raise CollectorError(f"{self.name} collector failed after {self.settings.max_retries} attempts") from last_exc

    def fetch(self, items: Iterable[str]) -> List[PriceQuote]:
        raise NotImplementedError

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpCollector":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def _require_httpx():
    try:
        import httpx
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised when dependency missing
        raise RuntimeError(
            "httpx is required for HTTP collectors. Install the 'httpx' extra to enable them."
        ) from exc

    return httpx
