from __future__ import annotations

from typing import Iterable, List

from .base import CollectorSettings, HttpCollector, PriceQuote


class SkinportCollector(HttpCollector):
    name = "skinport"

    def __init__(self, settings: CollectorSettings | None = None) -> None:
        settings = settings or CollectorSettings(
            base_url="https://skinport.com/",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        super().__init__(settings)

    def fetch(self, items: Iterable[str]) -> List[PriceQuote]:
        response = self._request(
            "GET",
            "api/bots/prices",
            params={"app_id": 730, "currency": "USD"},
        )
        payload = response.json()
        quotes: List[PriceQuote] = []
        lookup = {entry["market_hash_name"]: entry for entry in payload}
        for item in items:
            data = lookup.get(item)
            if not data:
                continue
            quotes.append(
                PriceQuote(
                    source=self.name,
                    market_hash_name=item,
                    price=float(data["min_price"]),
                    currency=data.get("currency", "USD"),
                    metadata={"max_price": float(data.get("max_price", 0.0)), "suggested_price": float(data.get("suggested_price", 0.0))},
                )
            )
        return quotes
