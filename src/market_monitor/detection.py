from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence


@dataclass
class DealRule:
    min_margin_percent: float = 5.0
    max_price_usd: float | None = None
    lookback_prices: Sequence[float] = ()
    price_drop_percent: float = 10.0


@dataclass
class DealCandidate:
    normalized_name: str
    market_hash_name: str
    target_price_usd: float
    best_source: Dict[str, object]
    margin_percent: float
    price_drop_percent: float


def _calculate_margin(target_price: float, reference_price: float) -> float:
    if reference_price == 0:
        return 0.0
    return ((reference_price - target_price) / reference_price) * 100


def _calculate_drop(target_price: float, history: Sequence[float]) -> float:
    if not history:
        return 0.0
    baseline = sum(history) / len(history)
    if baseline == 0:
        return 0.0
    return ((baseline - target_price) / baseline) * 100


def detect_deals(aggregated: Dict[str, Dict[str, object]], rules: DealRule) -> List[DealCandidate]:
    deals: List[DealCandidate] = []
    for item in aggregated.values():
        best_source = min(item["sources"], key=lambda s: s["price_usd"])
        reference_price = item["avg_price_usd"]
        margin = _calculate_margin(best_source["price_usd"], reference_price)
        drop = _calculate_drop(best_source["price_usd"], rules.lookback_prices)
        if margin < rules.min_margin_percent:
            continue
        if rules.max_price_usd is not None and best_source["price_usd"] > rules.max_price_usd:
            continue
        if drop < rules.price_drop_percent:
            continue
        deals.append(
            DealCandidate(
                normalized_name=item["normalized_name"],
                market_hash_name=item["market_hash_name"],
                target_price_usd=best_source["price_usd"],
                best_source=best_source,
                margin_percent=round(margin, 2),
                price_drop_percent=round(drop, 2),
            )
        )
    return deals
