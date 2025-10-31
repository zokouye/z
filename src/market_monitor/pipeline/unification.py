from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping

from ..collectors.base import PriceQuote


@dataclass
class CurrencyRate:
    code: str
    to_usd: float


DEFAULT_RATES: Dict[str, CurrencyRate] = {
    "USD": CurrencyRate(code="USD", to_usd=1.0),
    "EUR": CurrencyRate(code="EUR", to_usd=1.07),
    "CNY": CurrencyRate(code="CNY", to_usd=0.14),
}


def normalize_name(name: str) -> str:
    sanitized = name.replace("™", "")
    normalized = unicodedata.normalize("NFKD", sanitized)
    normalized = normalized.replace("★", "Star").replace("StatTrak", "StatTrak")
    normalized = " ".join(normalized.split())
    return normalized.lower()


def convert_currency(price: float, currency: str, rates: Mapping[str, CurrencyRate] | None = None) -> float:
    rates = rates or DEFAULT_RATES
    rate = rates.get(currency.upper())
    if not rate:
        raise ValueError(f"Unknown currency: {currency}")
    return price * rate.to_usd


def enrich_metadata(quote: PriceQuote, float_value: float | None = None, stickers: Iterable[str] | None = None) -> PriceQuote:
    metadata = dict(quote.metadata)
    if float_value is not None:
        metadata["float"] = float_value
    if stickers:
        metadata["stickers"] = list(stickers)
    return PriceQuote(
        source=quote.source,
        market_hash_name=quote.market_hash_name,
        price=quote.price,
        currency=quote.currency,
        metadata=metadata,
    )


def unify_quotes(quotes: Iterable[PriceQuote], rates: Mapping[str, CurrencyRate] | None = None) -> List[Dict[str, object]]:
    unified: List[Dict[str, object]] = []
    for quote in quotes:
        try:
            usd_price = convert_currency(quote.price, quote.currency, rates)
        except ValueError:
            continue
        unified.append(
            {
                "source": quote.source,
                "market_hash_name": quote.market_hash_name,
                "normalized_name": normalize_name(quote.market_hash_name),
                "price": quote.price,
                "currency": quote.currency,
                "price_usd": round(usd_price, 2),
                "metadata": quote.metadata,
            }
        )
    return unified


def aggregate_by_item(quotes: Iterable[Dict[str, object]]) -> Dict[str, Dict[str, object]]:
    aggregated: Dict[str, Dict[str, object]] = {}
    for record in quotes:
        key = record["normalized_name"]
        existing = aggregated.get(key)
        price_usd = record["price_usd"]
        if existing:
            existing["sources"].append(record)
            existing["min_price_usd"] = min(existing["min_price_usd"], price_usd)
            existing["max_price_usd"] = max(existing["max_price_usd"], price_usd)
            existing["avg_price_usd"] = round(
                (existing["avg_price_usd"] * (len(existing["sources"]) - 1) + price_usd) / len(existing["sources"]),
                2,
            )
        else:
            aggregated[key] = {
                "normalized_name": key,
                "market_hash_name": record["market_hash_name"],
                "min_price_usd": price_usd,
                "max_price_usd": price_usd,
                "avg_price_usd": price_usd,
                "sources": [record],
            }
    return aggregated
