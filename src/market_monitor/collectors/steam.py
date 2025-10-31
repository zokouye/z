from __future__ import annotations

from typing import Iterable, List

from .base import CollectorSettings, HttpCollector, PriceQuote


class SteamMarketCollector(HttpCollector):
    name = "steam_market"

    def __init__(self, settings: CollectorSettings | None = None) -> None:
        settings = settings or CollectorSettings(
            base_url="https://steamcommunity.com/market/",
            headers={"User-Agent": "Mozilla/5.0"},
            max_retries=5,
            backoff_factor=2.0,
        )
        super().__init__(settings)

    def fetch(self, items: Iterable[str]) -> List[PriceQuote]:
        quotes: List[PriceQuote] = []
        for item in items:
            response = self._request(
                "GET",
                "priceoverview/",
                params={"appid": 730, "market_hash_name": item, "currency": 1},
            )
            payload = response.json()
            price_str = payload.get("lowest_price") or payload.get("median_price")
            if not price_str:
                continue
            price = float(price_str.replace("$", "").replace(",", ""))
            quotes.append(
                PriceQuote(
                    source=self.name,
                    market_hash_name=item,
                    price=price,
                    currency="USD",
                    metadata={"volume": payload.get("volume")},
                )
            )
        return quotes
