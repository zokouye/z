from __future__ import annotations

from typing import Iterable, List

from .base import CollectorSettings, HttpCollector, PriceQuote


class Buff163Collector(HttpCollector):
    name = "buff163"

    def __init__(self, settings: CollectorSettings | None = None) -> None:
        settings = settings or CollectorSettings(
            base_url="https://buff.163.com/",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://buff.163.com/"},
            max_retries=4,
            backoff_factor=1.8,
        )
        super().__init__(settings)

    def fetch(self, items: Iterable[str]) -> List[PriceQuote]:
        quotes: List[PriceQuote] = []
        for item in items:
            response = self._request(
                "GET",
                "api/market/goods",
                params={"game": "csgo", "page_num": 1, "search": item},
            )
            payload = response.json()
            for entry in payload.get("data", {}).get("items", []):
                if entry.get("market_hash_name") != item:
                    continue
                sell_order = entry.get("sell_min_price")
                if sell_order is None:
                    continue
                quotes.append(
                    PriceQuote(
                        source=self.name,
                        market_hash_name=item,
                        price=float(sell_order),
                        currency="CNY",
                        metadata={"goods_id": entry.get("id")},
                    )
                )
        return quotes
